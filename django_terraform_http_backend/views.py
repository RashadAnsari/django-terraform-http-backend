from django.conf import settings
from django.utils.module_loading import import_string

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from .models import TerraformState


def get_authentication_classes():
    auth_classes = getattr(settings, "TERRAFORM_HTTP_BACKEND_PERMISSION_CLASSES", [])
    return [import_string(auth_class) for auth_class in auth_classes]


def get_permission_classes():
    perm_classes = getattr(settings, "TERRAFORM_HTTP_BACKEND_PERMISSION_CLASSES", [])
    return [import_string(perm_class) for perm_class in perm_classes]


@api_view(["GET", "POST", "DELETE"])
@permission_classes(get_permission_classes())
@authentication_classes(get_authentication_classes())
def state(request: Request, state_id: str) -> Response:
    if request.method == "GET":
        terraform_state = TerraformState.get_or_create(state_id=state_id)
        return Response(terraform_state.state_data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        try:
            lock_id = request.query_params.get("ID", None)
            terraform_state = TerraformState.get(state_id=state_id)
            if terraform_state.lock_id != lock_id:
                raise PermissionDenied("Lock ID does not match.")
            terraform_state.update_state(request.data)
            return Response("state updated.", status=status.HTTP_200_OK)
        except TerraformState.DoesNotExist:
            raise NotFound("State does not exist.")
    elif request.method == "DELETE":
        try:
            terraform_state = TerraformState.get(state_id=state_id)
            if terraform_state.is_locked:
                raise PermissionDenied("State is locked")
            terraform_state.delete()
        except TerraformState.DoesNotExist:
            raise NotFound("State does not exist.")


@api_view(["LOCK"])
@permission_classes(get_permission_classes())
@authentication_classes(get_authentication_classes())
def lock(request: Request, state_id: str) -> Response:
    lock_id = request.data.get("ID", None)
    if not lock_id:
        raise ValidationError("Lock ID is required.")

    terraform_state = TerraformState.get_or_create(state_id=state_id)
    if terraform_state.is_locked:
        return Response("State is already locked.", status=status.HTTP_423_LOCKED)

    terraform_state.lock(lock_id)
    return Response("Locked.", status=status.HTTP_200_OK)


@api_view(["UNLOCK"])
@permission_classes(get_permission_classes())
@authentication_classes(get_authentication_classes())
def unlock(request: Request, state_id: str) -> Response:
    lock_id = request.data.get("ID", None)
    if not lock_id:
        raise ValidationError("Lock ID is required.")

    try:
        terraform_state = TerraformState.get(state_id=state_id)
        if terraform_state.lock_id != lock_id:
            raise PermissionDenied("Lock ID does not match.")
        terraform_state.unlock()
        return Response("Unlocked.", status=status.HTTP_200_OK)
    except TerraformState.DoesNotExist:
        raise NotFound("State does not exist.")
