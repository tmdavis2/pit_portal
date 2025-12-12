from django.contrib import admin
from .models import Event, EventRegistration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'time', 'event_type', 'status', 'created_by']
    list_filter = ['status', 'event_type', 'date']
    search_fields = ['title', 'game', 'description']
    actions = ['approve_events', 'reject_events']
    
    def approve_events(self, request, queryset):
        """Approve selected events"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} event(s) approved!')
    approve_events.short_description = "✅ Approve selected events"
    
    #def reject_events(self, request, queryset):
     #   """Reject selected events"""
      #  updated = queryset.update(status='completed')
       # self.message_user(request, f'{updated} event(s) rejected!')
    #reject_events.short_description = "❌ Reject selected events"

    def reject_events(self, request, queryset):
        """Reject selected events"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} event(s) rejected and deleted!')
    reject_events.short_description = "❌ Reject selected events"

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registration_date', 'attended']
    list_filter = ['attended', 'registration_date']
    search_fields = ['user__username', 'event__title']