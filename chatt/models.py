from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Conversation(models.Model):
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="buy_conversations",
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sell_conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("vehicle", "buyer", "seller")

    def __str__(self):
        return f"Conv #{self.pk} veh={self.vehicle_id} buyer={self.buyer_id} seller={self.seller_id}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("created_at",)

    @property
    def is_read(self):
        return self.read_at is not None

    def mark_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save(update_fields=["read_at"])
