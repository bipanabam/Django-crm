from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
import json

class UserOnlineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_authenticated:
            await self.channel_layer.group_add("online_users", self.channel_name)
            await self.channel_layer.group_add("user_status_updates", self.channel_name)
            await self.accept()

            await self.send_status("online")

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard("online_users", self.channel_name)
            await self.channel_layer.group_add("user_status_updates", self.channel_name)
            await self.send_status("offline")

    async def receive(self, text_data):
        data = json.loads(text_data)
        status = data.get("status")

        if self.user.is_authenticated and status in ["online", "idle"]:
            await self.send_status(status)

    async def status_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "status_update",
            "user_id": event["user_id"],
            "username": event["username"],
            "status": event["status"],
        }))

    async def send_status(self, status):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Optionally update DB
        await self.update_last_seen(status)

        await self.channel_layer.group_send(
            "online_users",
            {
                "type": "user_status",
                "status": status,
                "user": self.user.username,
            },
        )

    async def user_status(self, event):
        await self.send(text_data=json.dumps(event))

    async def update_last_seen(self, status):
        from django.utils.timezone import now
        from asgiref.sync import sync_to_async
        from company.models import UserActivityLog 

        @sync_to_async
        def _update():
            self.user.last_seen = now()
            self.user.online_status = status
            self.user.save(update_fields=["last_seen", "online_status"])
            # Log the event
            UserActivityLog.objects.create(user=self.user, status=status)

        await _update()

        # Broadcast to all connected users
        await self.channel_layer.group_send(
            "user_status_updates",
            {
                "type": "status_update",
                "user_id": self.user.id,
                "username": self.user.username,
                "status": status
            }
        )

