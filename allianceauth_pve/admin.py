from django import forms
from django.contrib import admin
from django.utils.translation import gettext as _

from .models import (
    Entry,
    EntryCharacter,
    FundingProject,
    GeneralRole,
    PveButton,
    RoleSetup,
    Rotation,
    RotationPreset,
)
from .utils import ensure_rotation_presets_applied


class LockRolesSetupForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("lock_roles_setup"):
            # roles_setups is not a form field when it is readonly
            roles_setups = (
                cleaned_data.get("roles_setups")
                if "roles_setups" in self.fields
                else self.instance.roles_setups.all()
            )
            if roles_setups is not None and roles_setups.count() != 1:
                self.add_error(
                    "lock_roles_setup",
                    _("Locking the roles setup requires exactly 1 roles setup."),
                )

        return cleaned_data


class LockRolesSetupAdminMixin:
    form = LockRolesSetupForm

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj is not None and obj.lock_roles_setup:
            return (*readonly_fields, "roles_setups")
        return readonly_fields


@admin.register(Rotation)
class RotationAdmin(LockRolesSetupAdminMixin, admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "priority",
        "created_at",
        "days_since",
        "is_closed",
        "closed_at",
    )
    list_filter = ("is_closed",)
    search_fields = ("name",)
    readonly_fields = ("closed_at",)

    def save_model(self, *args, **kwargs):
        super().save_model(*args, **kwargs)
        ensure_rotation_presets_applied()

    def delete_queryset(self, *args, **kwargs):
        super().delete_queryset(*args, **kwargs)
        ensure_rotation_presets_applied()

    def delete_model(self, *args, **kwargs):
        super().delete_model(*args, **kwargs)
        ensure_rotation_presets_applied()


class EntryCharacterInline(admin.TabularInline):
    model = EntryCharacter
    raw_id_fields = (
        "user",
        "user_character",
    )
    can_delete = False
    readonly_fields = (
        "role",
        "user",
        "user_character",
        "first_site",
        "last_site",
        "helped_setup",
        "estimated_share_total",
        "actual_share_total",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).with_totals()

    def estimated_share_total(self, obj):
        return obj.estimated_share_total

    def actual_share_total(self, obj):
        return obj.actual_share_total


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    readonly_fields = (
        "rotation",
        "estimated_total",
        "site_scaling",
        "site_scaling_coefficient",
        "created_by",
        "created_at",
        "updated_at",
    )
    inlines = (EntryCharacterInline,)
    list_display = (
        "pk",
        "rotation",
        "estimated_total",
        "created_by",
        "created_at",
    )


@admin.register(PveButton)
class PveButtonAdmin(admin.ModelAdmin):
    search_fields = ("text",)
    list_display = (
        "text",
        "amount",
    )


class GeneralRoleInline(admin.TabularInline):
    model = GeneralRole


@admin.register(RoleSetup)
class RoleSetupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = (
        "name",
        "roles__name",
    )
    inlines = (GeneralRoleInline,)


@admin.register(FundingProject)
class FundingProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "goal",
        "is_active",
        "created_at",
        "completed_at",
    )
    search_fields = ("name",)
    list_filter = ("is_active",)
    readonly_fields = ("completed_at",)


@admin.register(RotationPreset)
class RotationPresetAdmin(LockRolesSetupAdminMixin, admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    def save_model(self, *args, **kwargs):
        super().save_model(*args, **kwargs)
        ensure_rotation_presets_applied()
