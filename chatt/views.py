from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from vehicles.models import Vehicle


@login_required
def open_conversation(request, vehicle_id: int):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    seller = vehicle.usuario
    buyer = request.user

    if seller is None:
        return HttpResponseForbidden("El vehículo no tiene vendedor asignado.")
    if buyer == seller:
        return HttpResponseForbidden("El vendedor no puede chatear consigo mismo.")

    convo, _ = Conversation.objects.get_or_create(
        vehicle=vehicle,
        buyer=buyer,
        seller=seller,
    )
    return JsonResponse({"conversation_id": convo.id})


@login_required
def history(request, conversation_id: int):
    convo = get_object_or_404(Conversation, pk=conversation_id)
    if request.user not in (convo.buyer, convo.seller):
        return HttpResponseForbidden("Sin permiso.")

    data = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "text": m.text,
            "image": m.image.url if m.image else None,
            "created_at": m.created_at.isoformat(),
            "read": m.is_read,
        }
        for m in convo.messages.select_related("sender")
    ]
    return JsonResponse({"messages": data})
