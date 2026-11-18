from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Message
from .forms import RegisterForm, MessageCreateForm, MessageEditForm


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
    """
    today = timezone.localdate()
    locked_messages = Message.objects.filter(
        user=request.user,
        unlock_date__gt=today
    ).order_by('unlock_date')

    unlocked_messages = Message.objects.filter(
        user=request.user,
        unlock_date__lte=today
    ).order_by('-unlock_date')

    context = {
        'locked_messages': locked_messages,
        'unlocked_messages': unlocked_messages,
        'today': today,
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
