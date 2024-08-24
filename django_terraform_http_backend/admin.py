from django.contrib import admin

from .models import TerraformState


@admin.register(TerraformState)
class OrganizationAdmin(admin.ModelAdmin):
    readonly_fields = ("state_id",)
    list_display_links = ("state_id",)
    list_display = ("state_id", "lock_id", "locked_at", "created_at", "updated_at")
    search_fields = ("state_id", "lock_id")
    exclude = ("state_data",)

    def has_add_permission(self, request):
        return False
