from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from .models import Event, EventRegistration
import json
from django.core.serializers.json import DjangoJSONEncoder

def index(request):
    """landing page for events"""
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    events = Event.objects.all().order_by('date', 'time')
    
    # Serialize events to JSON for JavaScript
    events_list = []
    for event in events:
        events_list.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'event_type': event.event_type,
            'game': event.game,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M'),
            'location': event.location,
            'status': event.status,
            'max_participants': event.max_participants,
            'current_participants': event.current_participants,
            'prize_amount': str(event.prize_amount) if event.prize_amount else None,
            'instructor': event.instructor,
            'duration': float(event.duration) if event.duration else None,
        })
    
    events_json = json.dumps(events_list, cls=DjangoJSONEncoder)
    
    return render(request, 'events/events.html', {'events': events, 'events_json': events_json})

def event_detail(request, pk):
    # display details for events
    event = get_object_or_404(Event, pk=pk)

    # Check if user is already registered (if authenticated)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(
            event=event,
            user=request.user
        ).exists()
    

    # Get related events (same game or type)
    related_events = Event.objects.filter(
        Q(game=event.game) | Q(event_type=event.event_type)
    ).exclude(pk=event.pk).filter(status='upcoming')[:3]
    
    # Calculate spots remaining
    spots_remaining = None
    if event.max_participants:
        spots_remaining = event.max_participants - event.current_participants
    
    context = {
        'event': event,
        'is_registered': is_registered,
        'related_events': related_events,
        'spots_remaining': spots_remaining,
        'can_register': event.status == 'upcoming' and not is_registered and (
        not event.max_participants or spots_remaining > 0
        ),
    }
    
    return render(request, 'events/detail.html', context)


@login_required
def register_event(request, pk):
    """Handle event registration"""
    event = get_object_or_404(Event, pk=pk)

    # If not POST, redirect to event detail
    if request.method != 'POST':
        return redirect('events:detail', pk=pk)
    
    # Check if event is available for registration
    if event.status != 'upcoming':
        messages.error(request, 'Registration is not available for this event.')
        return redirect('events:detail', pk=pk)
    
    # Check if event is full
    if event.max_participants and event.current_participants >= event.max_participants:
        messages.error(request, 'This event is full.')
        return redirect('events:detail', pk=pk)
    
    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return redirect('events:detail', pk=pk)
    
    # Create registration
    EventRegistration.objects.create(
        event=event,
        user=request.user
    )
 
 
    # Update participant count
    event.current_participants += 1
    event.save()
        
    messages.success(request, f'Successfully registered for {event.title}!')
    return redirect('events:detail', pk=pk)
    
    return redirect('events:detail', pk=pk)


@login_required
def unregister_event(request, pk):
    """Handle event unregistration"""
    event = get_object_or_404(Event, pk=pk)
    
    try:
        registration = EventRegistration.objects.get(event=event, user=request.user)
        registration.delete()
        
        # Update participant count
        event.current_participants = max(0, event.current_participants - 1)
        event.save()
        
        messages.success(request, f'Successfully unregistered from {event.title}.')
    except EventRegistration.DoesNotExist:
        messages.error(request, 'You are not registered for this event.')
    
    return redirect('events:detail', pk=pk)


def watch_live(request, pk):
    """View live event stream"""
    event = get_object_or_404(Event, pk=pk)
    
    if event.status != 'live':
        messages.error(request, 'This event is not currently live.')
        return redirect('events:detail', pk=pk)
    
    context = {
        'event': event,
    }
    return render(request, 'events/live.html', context)


def event_results(request, pk):
    """View event results and standings"""
    event = get_object_or_404(Event, pk=pk)
    
    if event.status != 'completed':
        messages.error(request, 'Results are not yet available for this event.')
        return redirect('events:detail', pk=pk)
    
    # Get event results/participants
    participants = EventRegistration.objects.filter(event=event).order_by('-score')
    
    context = {
        'event': event,
        'participants': participants,
    }
    return render(request, 'events/results.html', context)


def dashboard(request):
    """Display events dashboard"""
    events = Event.objects.all().order_by('date', 'time')
    
    context = {
        'events': events,
    }
    return render(request, 'events/dashboard.html', context)
# Events schedule page view
def schedule_view(request):
    """Display calendar view of all approved events"""
    events = Event.objects.filter(status='approved').order_by('date', 'time')

    events_json = [
        {
            "date": event.date.day,
            "title": event.title,
            "type": event.event_type,
            "game": event.game,
        }
        for event in events
    ]

    return render(request, 'events/events_schedule.html', {'events': events, "events_json": events_json})

# Esports Team schedule page view
def esports_schedule_view(request):
    """Display calendar view of all upcoming events"""
    events = Event.objects.filter(status='approved').order_by('date', 'time')
    return render(request, 'events/esports_schedule.html', {'events': events})

# Create event view
def create_event_view(request):
    """Allow users to submit events for approval"""
    if request.method == 'POST':
        # Get form data
        event = Event.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            event_type=request.POST['event_type'],
            game=request.POST['game'],
            date=request.POST['date'],
            time=request.POST['time'],
            location=request.POST.get('location', ''),
            max_participants=request.POST.get('max_participants') or None,
            status='pending',  # Needs approval!
            created_by=request.user if request.user.is_authenticated else None
        )
        
        messages.success(request, 'Event submitted! Awaiting administration approval.')
        return redirect('events:events_schedule')
    
    return render(request, 'events/create_event.html')