from django.db import models
from django.conf import settings


class Tag(models.Model):
    name = models.CharField("Name", max_length=30, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # новое поле: один пост может иметь много тегов, тег может быть у многих постов
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
        verbose_name="Tags",
    )

    def __str__(self):
        return self.title

class News(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"

    title = models.CharField("Title", max_length=200)
    summary = models.CharField("Short summary", max_length=300)
    content = models.TextField("Text")
    source_url = models.URLField("Source link", blank=True)
    status = models.CharField(
        "Status", max_length=10, choices=Status.choices,
        default=Status.PENDING, db_index=True,
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="news_requests",
        verbose_name="Submitted by",
    )
    admin_note = models.CharField(
        "Note for the author", max_length=300, blank=True,
        help_text="Shown to the author, for example the reason for rejection.",
    )
    created_at = models.DateTimeField("Created", auto_now_add=True)
    published_at = models.DateTimeField("Published", null=True, blank=True)

    class Meta:
        verbose_name = "News article"
        verbose_name_plural = "News"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
