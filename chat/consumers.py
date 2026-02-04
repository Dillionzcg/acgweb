import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope["user"]

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send history
        await self.send_history()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.user.is_authenticated:
            # Send error message back to the user
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '请先登录后再发言 (｡•́︿•̀｡)'
            }))
            return

        # Save to DB
        await self.save_message(self.user, self.room_name, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event.get('sender', 'Anonymous')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    @database_sync_to_async
    def save_message(self, user, room, content):
        return Message.objects.create(sender=user, room_name=room, content=content)

    @database_sync_to_async
    def get_history(self):
        # Get last 50 messages
        return list(Message.objects.filter(room_name=self.room_name).select_related('sender').order_by('-timestamp')[:50])

    async def send_history(self):
        history = await self.get_history()
        # Reverse to show oldest first
        for msg in reversed(history):
            await self.send(text_data=json.dumps({
                'message': msg.content,
                'sender': msg.sender.username,
                'is_history': True
            }))