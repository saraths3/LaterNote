from django.contrib import admin
from django.utils import timezone
from .models import Message, Profile


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'unlock_date', 'created_at', 'get_status')
    list_filter = ('category', 'unlock_date', 'created_at')
    search_fields = ('title', 'content', 'user__username')
    readonly_fields = ('created_at',)

    @admin.display(description='Status')
    def get_status(self, obj):
        if obj.is_unlocked():
            return "🔓 Unlocked"
        return f"🔒 Locked ({obj.days_until_unlock()}d remaining)"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio_preview')
    search_fields = ('user__username', 'bio')

    @admin.display(description='Bio')
    def bio_preview(self, obj):
        return (obj.bio[:60] + '...') if len(obj.bio) > 60 else obj.bio

