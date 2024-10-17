from django.contrib import admin

from .models import Rotation, Entry, EntryCharacter, PveButton, RoleSetup, GeneralRole, FundingProject, RotationPreset
from .actions import ensure_rotation_presets_applied


@admin.register(Rotation)
class RotationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'priority', 'created_at', 'days_since', 'is_closed', 'closed_at', )
    list_filter = ('is_closed', )
    search_fields = ('name', )
    readonly_fields = ('closed_at',)

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
    raw_id_fields = ('user', 'user_character',)
    can_delete = False
    readonly_fields = (
        'role',
        'user',
        'user_character',
        'site_count',
        'helped_setup',
        'estimated_share_total',
        'actual_share_total',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).with_totals()

    def estimated_share_total(self, obj):
        return obj.estimated_share_total

    def actual_share_total(self, obj):
        return obj.actual_share_total


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    readonly_fields = ('rotation', 'estimated_total', 'created_by', 'created_at', 'updated_at', )
    inlines = (EntryCharacterInline, )
    list_display = ('pk', 'rotation', 'estimated_total', 'created_by', 'created_at', )


@admin.register(PveButton)
class PveButtonAdmin(admin.ModelAdmin):
    search_fields = ('text',)
    list_display = ('text', 'amount',)


class GeneralRoleInline(admin.TabularInline):
    model = GeneralRole


@admin.register(RoleSetup)
class RoleSetupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'roles__name',)
    inlines = (GeneralRoleInline,)


@admin.register(FundingProject)
class FundingProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal', 'is_active', 'created_at', 'completed_at',)
    search_fields = ('name',)
    list_filter = ('is_active',)
    readonly_fields = ('completed_at',)


@admin.register(RotationPreset)
class RotationPresetAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )

    def save_model(self, *args, **kwargs):
        super().save_model(*args, **kwargs)
        ensure_rotation_presets_applied()
