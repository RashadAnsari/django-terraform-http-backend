from django.urls import path

from . import views

urlpatterns = [
    path("states/<str:state_id>", views.state, name="state"),
    path("states/<str:state_id>/lock", views.lock, name="lock"),
    path("states/<str:state_id>/unlock", views.unlock, name="unlock"),
]
