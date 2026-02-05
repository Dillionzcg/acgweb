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

        if self.user.is_authenticated:
            # Join user specific group
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send history
        await self.send_history()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            # Leave user specific group
            await self.channel_layer.group_discard(
                f"user_{self.user.id}",
                self.channel_name
            )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message') # Default to chat_message

        if not self.user.is_authenticated:
             # Send error message back to the user
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '请先登录后再发言 (｡•́︿•̀｡)'
            }))
            return

        if message_type == 'chat_message':
            message = text_data_json['message']
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
        elif message_type == 'call_request':
            target_user_id = text_data_json.get('target_user_id')
            if target_user_id:
                group_name = f"user_{target_user_id}"
                # Send notification to the target user's personal group
                await self.channel_layer.group_send(
                    group_name,
                    {
                        'type': 'call_notification',
                        'room_name': self.room_name,
                        'sender': self.user.username,
                        'sender_id': self.user.id
                    }
                )

        elif message_type in ['video_offer', 'video_answer', 'new_ice_candidate', 'ready_for_call']:
            # Broadcast signaling message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'signal_message',
                    'message_type': message_type,
                    'data': text_data_json.get('data'),
                    'sender': self.user.username
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event.get('sender', 'Anonymous')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender
        }))

    async def call_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_notification',
            'room_name': event['room_name'],
            'sender': event['sender'],
            'sender_id': event['sender_id']
        }))

    # Handle signaling messages
    async def signal_message(self, event):
        message_type = event['message_type']
        data = event['data']
        sender = event['sender']

        # Send message to WebSocket (skip if sender is self - handled in client mostly, but good practice)
        if sender != self.user.username:
             await self.send(text_data=json.dumps({
                'type': message_type,
                'data': data,
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