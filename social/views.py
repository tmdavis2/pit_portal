"""
View functions for the social (chat) application.
Handles HTTP requests for chat pages and user search functionality.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Max
from accounts.models import CustomUser
from .models import Message


def socialPage(request, *args, **kwargs):
    """
    Display the main social hub page with previous chat rooms.
    
    Shows:
    - List of chat rooms the user has participated in
    - Options to join new rooms or start direct messages
    
    Args:
        request: HTTP request object
        *args, **kwargs: Additional arguments (unused)
    
    Returns:
        Rendered socialPage.html template with previous rooms context
        Redirects to login if user is not authenticated
    """
    # Redirect unauthenticated users to login page
    if not request.user.is_authenticated:
        return redirect("login")
    
    # Get all rooms where user has sent messages, ordered by most recent activity
    previous_rooms = Message.objects.filter(
        username=request.user.username
    ).values('room_name').annotate(
        last_message=Max('timestamp')  # Find most recent message timestamp
    ).order_by('-last_message').distinct()  # Sort newest first, remove duplicates
    
    # Process room names for display (especially for DM rooms)
    for room in previous_rooms:
        if room['room_name'].startswith('dm_'):
            # Extract usernames from DM room name (format: dm_user1_user2)
            parts = room['room_name'][3:].split('_')
            # Find the other user's name (not current user)
            other_user = next((p for p in parts if p != request.user.username), None)
            # Display other user's name instead of technical room name
            room['display_name'] = other_user if other_user else room['room_name']
        else:
            # For regular rooms, use the room name as-is
            room['display_name'] = room['room_name']
    
    context = {'previous_rooms': previous_rooms}
    return render(request, "social/socialPage.html", context)


def room(request, room_name):
    """
    Display a specific chat room with message history.
    
    Args:
        request: HTTP request object
        room_name: Name/identifier of the chat room
    
    Returns:
        Rendered room.html template with room name, messages, and display name
    """
    # Fetch the 50 most recent messages for this room
    messages = Message.objects.filter(
        room_name=room_name
    ).order_by('timestamp')[:50]
    
    # Generate user-friendly display name for the room
    if room_name.startswith('dm_'):
        # For DM rooms, show the other user's name
        parts = room_name[3:].split('_')
        other_user = next((p for p in parts if p != request.user.username), None)
        room_display_name = other_user if other_user else room_name
    else:
        # For regular rooms, use room name as-is
        room_display_name = room_name
    
    return render(request, "social/room.html", {
        "room_name": room_name,  # Technical room identifier
        "messages": messages,  # Message history
        "room_display_name": room_display_name  # User-friendly display name
    })


def search_users(request):
    """
    AJAX endpoint for searching users by username.
    
    Used by the direct message feature to find users to chat with.
    
    Args:
        request: HTTP request object with 'q' query parameter
    
    Returns:
        JSON response containing list of matching usernames
        Returns error if user is not authenticated
        Returns empty list if query is too short (<2 characters)
    """
    # Verify user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)
    
    # Get search query from request parameters
    query = request.GET.get('q', '').strip()
    
    # Require at least 2 characters to search (avoid too many results)
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    # Search for users with matching usernames
    # Case-insensitive search, exclude current user, limit to 10 results
    users = CustomUser.objects.filter(
        username__icontains=query
    ).exclude(
        username=request.user.username
    )[:10]
    
    # Convert QuerySet to list of dictionaries for JSON serialization
    user_list = [{'username': user.username} for user in users]
    
    return JsonResponse({'users': user_list})