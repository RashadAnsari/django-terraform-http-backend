from django.urls import path

from . import views

urlpatterns = [
    path("state/<str:state_id>", views.state, name="state"),
    path("lock/<str:state_id>", views.lock, name="lock"),
    path("unlock/<str:state_id>", views.unlock, name="unlock"),
]
