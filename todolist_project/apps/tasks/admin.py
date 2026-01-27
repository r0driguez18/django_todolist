from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'is_done', 'created_at')
    search_fields = ('title', 'owner__username')
    list_filter = ('is_done', 'created_at')
