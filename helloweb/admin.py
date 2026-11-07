from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from .models import News

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_active", "is_staff", "date_joined", "last_login")
    list_editable = ("is_active",)          # блокировка прямо из списка, одним кликом
    list_filter = ("is_active", "is_staff", "is_superuser", "date_joined")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)
    actions = ["activate_users", "deactivate_users"]

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"Activated users: {count}")

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        queryset = queryset.exclude(pk=request.user.pk)   # себя заблокировать нельзя
        count = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated users: {count}") # удобный выбор нескольких тегов


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "submitted_by", "created_at", "published_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "summary", "content", "submitted_by__username")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    raw_id_fields = ("submitted_by",)
    readonly_fields = ("created_at", "published_at")
    actions = ["publish_selected", "reject_selected"]

    fieldsets = (
        (None, {"fields": ("title", "summary", "content", "source_url")}),
        ("Moderation", {"fields": ("status", "admin_note", "submitted_by", "created_at", "published_at")}),
    )

    def get_changeform_initial_data(self, request):
        # новость, созданная админом вручную, по умолчанию сразу публикуется
        return {"status": News.Status.PUBLISHED}

    def save_model(self, request, obj, form, change):
        if not change and not obj.submitted_by:
            obj.submitted_by = request.user
        if obj.status == News.Status.PUBLISHED and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.action(description="Publish selected news")
    def publish_selected(self, request, queryset):
        count = queryset.exclude(status=News.Status.PUBLISHED).update(
            status=News.Status.PUBLISHED, published_at=timezone.now()
        )
        self.message_user(request, f"Published: {count}")

    @admin.action(description="Reject selected news")
    def reject_selected(self, request, queryset):
        count = queryset.exclude(status=News.Status.REJECTED).update(
            status=News.Status.REJECTED
        )
        self.message_user(request, f"Rejected: {count}")