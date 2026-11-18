from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('messages/', views.message_list, name='message_list'),
    path('messages/new/', views.message_create, name='message_create'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('messages/<int:pk>/edit/', views.message_edit, name='message_edit'),
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),
]
