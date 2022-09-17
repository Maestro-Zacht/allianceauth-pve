from django.contrib import admin

from .models import Rotation, Entry, EntryCharacter, PveButton, RoleSetup, GeneralRole


@admin.register(Rotation)
class RotationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'priority', 'created_at', 'days_since', 'is_closed', 'closed_at', 'is_paid_out', )
    list_filter = ('is_closed', 'is_paid_out', )
    search_fields = ('name', )
    readonly_fields = ('closed_at',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        for entry in obj.entries.all():
            entry.update_share_totals()


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
