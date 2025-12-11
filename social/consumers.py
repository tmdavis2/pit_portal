"""
WebSocket consumers for real-time chat functionality.
Handles WebSocket connections, message routing, and chat room logic using Django Channels.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Asynchronous WebSocket consumer for handling real-time chat messages.
    
    This consumer manages:
    - WebSocket connection establishment and authentication
    - Room membership and access control
    - Message receiving and broadcasting
    - Database persistence of messages
    """
    
    async def connect(self):
        """
        Handle new WebSocket connection requests.
        
        Process:
        1. Extract and sanitize room name from URL
        2. Verify user authentication
        3. Check DM room access permissions
        4. Add connection to room group
        5. Accept the WebSocket connection
        
        Closes connection if user is not authenticated or lacks room access.
        """
        from django.contrib.auth.models import AnonymousUser
        
        # Extract room name from URL and replace spaces with underscores
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_name = self.room_name.replace(' ', '_')
        
        # Create unique group name for this chat room
        self.room_group_name = f'chat_{self.room_name}'
        
        # Get the user from the WebSocket scope
        user = self.scope.get('user')
        
        # Reject connection if user is not authenticated
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return
        
        # For direct message rooms, verify user is a participant
        if self.room_name.startswith('dm_'):
            # Extract usernames from DM room name (format: dm_user1_user2)
            users_in_room = self.room_name.replace('dm_', '').split('_')
            # Close connection if user is not one of the two participants
            if user.username not in users_in_room:
                await self.close()
                return
        
        # Add this connection to the room's channel group for broadcasting
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the WebSocket connection
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        
        Args:
            close_code: The WebSocket close code indicating reason for disconnection
        
        Removes the connection from the room's channel group to stop receiving messages.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Handle incoming messages from WebSocket client.
        
        Args:
            text_data: JSON string containing message and username
        
        Process:
        1. Parse incoming JSON data
        2. Save message to database
        3. Broadcast message to all users in the room group
        """
        from .models import Message
        
        # Parse JSON data from client
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        
        # Save message to database for persistence
        await Message.objects.acreate(
            room_name=self.room_name,
            username=username,
            content=message
        )
        
        # Broadcast message to all connections in the room group
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "sendMessage",  # Calls sendMessage method below
                "message": message,
                "username": username,
            }
        )
    
    async def sendMessage(self, event):
        """
        Handle message broadcasting to WebSocket client.
        
        Args:
            event: Dictionary containing message, username, and optional timestamp
        
        This method is called when a message is broadcast to the room group.
        Sends the message data as JSON to the connected client.
        """
        message = event["message"]
        username = event["username"]
        timestamp = event.get("timestamp", "")
        
        # Send message to WebSocket client as JSON
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "timestamp": timestamp
        }))