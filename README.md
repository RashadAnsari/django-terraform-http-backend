# django-terraform-http-backend

A Django app that implements Terraform's [HTTP state backend](https://developer.hashicorp.com/terraform/language/backend/http). Terraform state is stored in your Django database, with locking, a change history for every state, and a read-only view in the Django admin.

## Install

Requires Python 3.11+, Django 4+, [Django REST framework](https://www.django-rest-framework.org/) and [django-simple-history](https://django-simple-history.readthedocs.io/).

```bash
pip install git+https://github.com/RashadAnsari/django-terraform-http-backend.git@v0.1.0
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "rest_framework",
    "simple_history",
    "django_terraform_http_backend",
]
```

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path("terraform/", include("django_terraform_http_backend.urls")),
]
```

```bash
python manage.py migrate
```

## Endpoints

`<state_id>` is any string; each one is a separate state.

| Method | Path | What it does |
|---|---|---|
| `GET` | `states/<state_id>` | Return the state. An empty state is created on first read. |
| `POST` | `states/<state_id>?ID=<lock_id>` | Replace the state. The lock ID must match the current lock. |
| `DELETE` | `states/<state_id>` | Delete the state. Refused while it is locked. |
| `LOCK` | `states/<state_id>/lock` | Lock the state. Returns `423 Locked` if it is already locked. |
| `UNLOCK` | `states/<state_id>/unlock` | Unlock the state. The lock ID must match. |

These match Terraform's defaults, so no method overrides are needed in the backend config.

## Terraform config

```hcl
terraform {
  backend "http" {
    address        = "https://example.com/terraform/states/my-project"
    lock_address   = "https://example.com/terraform/states/my-project/lock"
    unlock_address = "https://example.com/terraform/states/my-project/unlock"
    username       = "terraform"
    password       = "..."
  }
}
```

## Authentication and permissions

The views use DRF authentication and permission classes, configured as dotted paths:

```python
TERRAFORM_HTTP_BACKEND_AUTHENTICATION_CLASSES = [
    "rest_framework.authentication.BasicAuthentication",
]
TERRAFORM_HTTP_BACKEND_PERMISSION_CLASSES = [
    "rest_framework.permissions.IsAuthenticated",
]
```

If you leave either setting out, the views fall back to DRF's `DEFAULT_AUTHENTICATION_CLASSES` and `DEFAULT_PERMISSION_CLASSES`. DRF's own default permission is `AllowAny`, so set at least one of the two permission settings, or anyone who can reach the endpoints can read and overwrite your state.

Terraform sends `username` and `password` with HTTP basic auth, so `BasicAuthentication` with a dedicated Django user is the simplest match.

## Admin and history

The `TerraformState` model is registered in the Django admin with the lock ID and timestamps visible. The state data itself is hidden there, and states can't be added from the admin. Every change is recorded by django-simple-history in `django_terraform_http_backend_historical_terraform_states`, so you can recover an earlier state.

## Development

```bash
poetry install
make local   # lock, isort, black
make lint    # flake8, isort --check, black --check
```

## License

[MIT](LICENSE)
