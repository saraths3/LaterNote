from django.contrib import admin
from django.utils import timezone
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'unlock_date', 'created_at', 'get_status')
    list_filter = ('unlock_date', 'created_at')
    search_fields = ('title', 'content', 'user__username')
    readonly_fields = ('created_at',)

    @admin.display(description='Status')
    def get_status(self, obj):
        if obj.is_unlocked():
            return "🔓 Unlocked"
        return f"🔒 Locked ({obj.days_until_unlock()}d remaining)"
