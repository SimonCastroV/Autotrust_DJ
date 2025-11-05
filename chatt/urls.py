from django.urls import path

from . import views

app_name = "chatt"

urlpatterns = [
    path("open/<int:vehicle_id>/", views.open_conversation, name="open"),
    path("history/<int:conversation_id>/", views.history, name="history"),
]
