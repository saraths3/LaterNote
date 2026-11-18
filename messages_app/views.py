from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Message, Profile, CATEGORY_CHOICES
from .forms import (
    RegisterForm,
    MessageCreateForm,
    MessageEditForm,
    UserUpdateForm,
    ProfileUpdateForm,
)


def home(request):
    """
    Public landing page introducing LaterNote.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def register_view(request):
    """
    Handle new user registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to LaterNote, {user.username}! Your account is ready.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """
    Handle user login.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def dashboard(request):
    """
    Dashboard providing summary metrics, upcoming unlocks, and recent messages.
    """
    today = timezone.localdate()
    user_messages = Message.objects.filter(user=request.user)

    total_count = user_messages.count()
    locked_messages = user_messages.filter(unlock_date__gt=today).order_by('unlock_date')
    locked_count = locked_messages.count()
    unlocked_messages = user_messages.filter(unlock_date__lte=today).order_by('-unlock_date')
    unlocked_count = unlocked_messages.count()

    upcoming_messages = locked_messages[:5]
    recent_unlocked = unlocked_messages[:5]

    context = {
        'total_count': total_count,
        'locked_count': locked_count,
        'unlocked_count': unlocked_count,
        'upcoming_messages': upcoming_messages,
        'recent_unlocked': recent_unlocked,
        'today': today,
    }
    return render(request, 'messages/dashboard.html', context)


@login_required
def message_create(request):
    """
    Create a new message with a future unlock date.
    """
    if request.method == 'POST':
        form = MessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            messages.success(
                request,
                f'Message "{message.title}" sealed! It will unlock on {message.unlock_date.strftime("%B %d, %Y")}.'
            )
            return redirect('message_list')
        else:
            messages.error(request, "Could not save message. Please review the form.")
    else:
        form = MessageCreateForm()

    return render(request, 'messages/create.html', {'form': form})


@login_required
def message_list(request):
    """
    Display all messages of the current user, separated into Locked and Unlocked.
    Supports title search and category filtering.
    """
    today = timezone.localdate()
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    messages_qs = Message.objects.filter(user=request.user)

    if query:
        messages_qs = messages_qs.filter(title__icontains=query)

    if selected_category:
        messages_qs = messages_qs.filter(category=selected_category)

    locked_messages = messages_qs.filter(
        unlock_date__gt=today
    ).order_by('unlock_date')

    unlocked_messages = messages_qs.filter(
        unlock_date__lte=today
    ).order_by('-unlock_date')

    context = {
        'locked_messages': locked_messages,
        'unlocked_messages': unlocked_messages,
        'today': today,
        'query': query,
        'selected_category': selected_category,
        'categories': CATEGORY_CHOICES,
    }
    return render(request, 'messages/list.html', context)


@login_required
def message_detail(request, pk):
    """
    Display a message.
    If still locked: displays locked page (never exposing content).
    If unlocked: displays full message content.
    """
    message = get_object_or_404(Message, pk=pk, user=request.user)

    if message.is_locked():
        return render(request, 'messages/locked.html', {
            'message': message,
            'days_remaining': message.days_until_unlock(),
        })

    return render(request, 'messages/detail.html', {
        'message': message,
    })


@login_required
def message_edit(request, pk):
    """
    Edit message title and content.
    Unlock date cannot be changed.
    """
    message = get_object_or_404(Message, pk=pk, user=request.user)

    if request.method == 'POST':
        form = MessageEditForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            messages.success(request, f'Message "{message.title}" updated successfully.')
            return redirect('message_detail', pk=message.pk)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = MessageEditForm(instance=message)

    return render(request, 'messages/edit.html', {
        'form': form,
        'message': message,
    })


@login_required
def message_delete(request, pk):
    """
    Delete a message. Only accepts POST requests.
    """
    message = get_object_or_404(Message, pk=pk, user=request.user)

    if request.method == 'POST':
        title = message.title
        message.delete()
        messages.success(request, f'Message "{title}" has been deleted.')
        return redirect('message_list')

    # If accessed via GET, redirect to the message detail page safely
    return redirect('message_detail', pk=message.pk)


@login_required
def profile_view(request):
    """
    User profile view displaying account stats and allowing profile updates.
    """
    # Ensure profile instance exists
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    today = timezone.localdate()
    user_messages = request.user.messages.all()
    total_messages = user_messages.count()
    locked_count = user_messages.filter(unlock_date__gt=today).count()
    unlocked_count = user_messages.filter(unlock_date__lte=today).count()

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'total_messages': total_messages,
        'locked_count': locked_count,
        'unlocked_count': unlocked_count,
        'profile': profile,
    }
    return render(request, 'registration/profile.html', context)


@login_required
def change_password_view(request):
    """
    Allow authenticated users to change their password securely.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, "Your password has been changed successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'registration/change_password.html', {'form': form})

