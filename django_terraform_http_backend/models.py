from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from simple_history.models import HistoricalRecords

DEFAULT_STATE = {
    "version": 4,
    "serial": 0,
    "lineage": "",
    "outputs": {},
    "resources": [],
}


class TerraformState(models.Model):
    history = HistoricalRecords(table_name="django_terraform_http_backend_historical_terraform_states")

    state_id = models.CharField(max_length=255, primary_key=True)
    state_data = models.JSONField()
    lock_id = models.CharField(max_length=255, null=True)
    locked_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "django_terraform_http_backend_terraform_states"

    @property
    def is_locked(self):
        return self.lock_id is not None

    @classmethod
    def get(self, state_id: str) -> "TerraformState":
        return self.objects.get(state_id=state_id)

    @classmethod
    def get_or_create(self, state_id: str) -> "TerraformState":
        state, _ = self.objects.get_or_create(state_id=state_id, defaults={"state_data": DEFAULT_STATE})
        return state

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    def clean(self):
        if self.lock_id is not None and self.locked_at is None:
            raise ValidationError({"locked_at": _("Locked at is required when lock id is set.")})
        if self.lock_id is None and self.locked_at is not None:
            raise ValidationError({"locked_at": _("Locked at is not required when lock id is not set.")})

    def lock(self, lock_id):
        self.lock_id = lock_id
        self.locked_at = timezone.now()
        self.save()

    def update_state(self, state_data: dict):
        self.state_data = state_data
        self.save()

    def unlock(self):
        self.lock_id = None
        self.locked_at = None
        self.save()
