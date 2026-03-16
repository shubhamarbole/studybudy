import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from base.models import Message, Room
from studybud.utils.toxicity_checker import toxicity_checker

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print("[WebSocket] Received:", text_data)
    
        message = data.get('message', '').strip()
        username = data.get('username')
        room_id = data.get('room')
        temp_id = data.get('temp_id')  # ⬅️ New: optional field from frontend
    
        if not message:
            return
    
        # Check for toxicity
        if toxicity_checker.is_toxic(message):
            await self.send(text_data=json.dumps({
                'type': 'blocked',
                'message': message,
                'temp_id': temp_id  # ⬅️ Send temp_id back so it can be removed
            }))
            return
    
        # Save the message to DB
        await self.save_message(username, room_id, message)
    
        # Broadcast message to group
        await self.channel_layer.group_send(
           self.room_group_name,
           {
                'type': 'chat_message',
               'message': message,
               'username': username,
               'temp_id': temp_id,  # ⬅️ Optional: forward temp_id to all clients if needed
           }
       )


    async def chat_message(self, event):
        print("[WebSocket] Broadcasting to clients")
        message = event['message']
        username = event['username']

        try:
            user = await database_sync_to_async(User.objects.get)(username=username)
            avatar_url = user.avatar.url if user.avatar else '/static/images/default.png'
        except Exception:
            avatar_url = '/static/images/default.png'

        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message,
            'username': username,
            'avatar_url': avatar_url,
        }))

    @database_sync_to_async
    def save_message(self, username, room_id, message):
        try:
            user = User.objects.get(username=username)
            room = Room.objects.get(id=room_id)
            Message.objects.create(user=user, room=room, body=message)
        except Exception as e:
            print(f"[WebSocket] Error saving message: {e}")
