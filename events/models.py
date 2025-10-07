from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class Event(models.Model):
    EVENT_TYPES = [
        ('tournament', 'Tournament'),
        ('schedule', 'Schedule'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('completed', 'Completed'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    game = models.CharField(max_length=100)
    
    # Date and Time
    date = models.DateField()
    time = models.TimeField()
    duration = models.FloatField(
        help_text="Duration in hours", 
        null=True, 
        blank=True
    )
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='upcoming'
    )
    
    # Tournament specific fields
    prize_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    max_participants = models.IntegerField(null=True, blank=True)
    current_participants = models.IntegerField(default=0)
    
    # Schedule specific fields
    instructor = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    # Additional fields
    image = models.ImageField(
        upload_to='events/', 
        null=True, 
        blank=True
    )
    rules = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_events'
    )
    
    class Meta:
        ordering = ['date', 'time']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['event_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'pk': self.pk})
    
    def is_full(self):
        #Check if event is at capacity
        if self.max_participants:
            return self.current_participants >= self.max_participants
        return False
    
    def spots_remaining(self):
        #Calculate the remaining spots
        if self.max_participants:
            return max(0, self.max_participants - self.current_participants)
        return None
    
    def is_past(self):
        #Check if event date has passed
        return self.date < timezone.now().date()


class EventRegistration(models.Model):
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='registrations'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='event_registrations'
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    
    # For tournaments, track results
    score = models.IntegerField(default=0, null=True, blank=True)
    placement = models.IntegerField(null=True, blank=True)
    
    # For schedules, track attendance
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

