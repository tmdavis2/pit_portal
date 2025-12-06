import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth.models import AnonymousUser

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        user = self.scope.get('user')
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return
        
        # For DM rooms, ensure user is a participant
        if self.room_name.startswith('dm_'):
            users_in_room = self.room_name.replace('dm_', '').split('_')
            if user.username not in users_in_room:
                await self.close()
                return
        
        await self.channel_layer.group_add( 
            self.room_group_name ,
            self.channel_name
        )
        await self.accept()
    async def disconnect(self , close_code):
        await self.channel_layer.group_discard(
            self.room_group_name , 
            self.channel_name 
        )
    async def receive(self, text_data):
        from .models import Message

        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        await Message.objects.acreate(room_name=self.room_name, username=username, content=message)
        await self.channel_layer.group_send(
            self.room_group_name,{
                "type" : "sendMessage" ,
                "message" : message , 
                "username" : username ,
            })
    
    async def sendMessage(self , event) : 
        message = event["message"]
        username = event["username"]
        timestamp = event.get("timestamp", "")
        await self.send(text_data = json.dumps({"message":message ,"username":username, "timestamp": timestamp}))