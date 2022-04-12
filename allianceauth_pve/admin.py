from django.contrib import admin

from .models import Rotation, Entry


@admin.register(Rotation)
class RotationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'priority', 'created_at', 'days_since', 'is_closed', 'closed_at', 'is_paid_out', )
    list_filter = ('is_closed', 'is_paid_out', )
    search_fields = ('name', )


class EntryCharacterInline(admin.TabularInline):
    model = Entry.shares.through
    raw_id_fields = ('user', )


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    raw_id_fields = ('rotation', )
    readonly_fields = ('created_by', )
    inlines = (EntryCharacterInline, )
    search_fields = ('id', )
    list_display = ('pk', 'rotation', 'estimated_total', 'created_by', 'created_at', )
    exclude = ('total_shares_count', )
