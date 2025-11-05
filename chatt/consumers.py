import json
from typing import List, Sequence

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Grupo por conversation_id: chatt_conversation_{conversation_id}
    Permisos: solo buyer o seller asociados.
    Eventos:
      - receive 'message': {text}
      - receive 'typing': {is_typing: bool}
      - receive 'read': {message_ids: [..]}
    Broadcast:
      - 'message' con mensaje serializado
      - 'typing' con user_id y estado
      - 'read' con ids marcados
      - 'presence' con status: online/reconnecting/offline (simple)
    """

    async def connect(self):
        self.user = self.scope.get("user", AnonymousUser())
        self.conversation_id = int(self.scope["url_route"]["kwargs"]["conversation_id"])
        self.group_name = f"chatt_conversation_{self.conversation_id}"

        convo = await self._get_conversation(self.conversation_id)
        if (
            not self.user.is_authenticated
            or convo is None
            or self.user.id not in (convo.buyer_id, convo.seller_id)
        ):
            await self.close()
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "presence",
                "payload": {"user_id": self.user.id, "status": "online"},
            },
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "presence",
                "payload": {"user_id": self.user.id, "status": "offline"},
            },
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data or "{}")
        kind = data.get("type")

        if kind == "message":
            text = (data.get("text") or "").strip()
            if text:
                try:
                    msg = await self._create_message(
                        self.user.id, self.conversation_id, text
                    )
                except PermissionError:
                    return
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat.message",
                        "payload": msg,
                    },
                )

        elif kind == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.typing",
                    "payload": {
                        "user_id": self.user.id,
                        "is_typing": bool(data.get("is_typing")),
                    },
                },
            )

        elif kind == "read":
            ids = data.get("message_ids") or []
            marked = await self._mark_read(self.user.id, self.conversation_id, ids)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.read",
                    "payload": {"user_id": self.user.id, "message_ids": marked},
                },
            )

    # Handlers de grupo
    async def chat_message(self, event):
        await self.send_json({"type": "message", **event["payload"]})

    async def chat_typing(self, event):
        await self.send_json({"type": "typing", **event["payload"]})

    async def chat_read(self, event):
        await self.send_json({"type": "read", **event["payload"]})

    async def presence(self, event):
        await self.send_json({"type": "presence", **event["payload"]})

    # Utils
    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def _get_conversation(self, conversation_id: int) -> Conversation | None:
        try:
            return Conversation.objects.select_related("vehicle").get(
                pk=conversation_id
            )
        except Conversation.DoesNotExist:
            return None

    @staticmethod
    def _create_payload(msg: Message) -> dict:
        return {
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "sender_id": msg.sender_id,
            "text": msg.text,
            "created_at": msg.created_at.isoformat(),
            "read": msg.read_at is not None,
        }

    @database_sync_to_async
    def _create_message(self, user_id: int, conversation_id: int, text: str) -> dict:
        try:
            convo = Conversation.objects.select_related("vehicle").get(pk=conversation_id)
        except Conversation.DoesNotExist as exc:
            raise PermissionError("Conversación no encontrada.") from exc
        if user_id not in (convo.buyer_id, convo.seller_id):
            raise PermissionError("Usuario sin acceso a la conversación.")
        msg = Message.objects.create(conversation=convo, sender_id=user_id, text=text)
        return self._create_payload(msg)

    @database_sync_to_async
    def _mark_read(
        self, user_id: int, conversation_id: int, ids: Sequence[int]
    ) -> List[int]:
        try:
            convo = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return []
        if user_id not in (convo.buyer_id, convo.seller_id):
            return []
        qs = Message.objects.filter(conversation=convo, id__in=ids).exclude(
            sender_id=user_id
        )
        now = timezone.now()
        qs.update(read_at=now)
        return list(qs.values_list("id", flat=True))
