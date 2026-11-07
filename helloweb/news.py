from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import News

MAX_PENDING_PER_USER = 5
PER_PAGE = 6


class NewsRequestForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ("title", "summary", "content", "source_url")
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 9}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


def news_list(request):
    qs = News.objects.filter(status=News.Status.PUBLISHED).order_by("-published_at", "-id")
    page = Paginator(qs, PER_PAGE).get_page(request.GET.get("page"))
    return render(request, "helloweb/news.html", {"page": page})


def news_detail(request, pk):
    qs = News.objects.all() if request.user.is_staff else News.objects.filter(status=News.Status.PUBLISHED)
    article = get_object_or_404(qs, pk=pk)
    return render(request, "helloweb/news_detail.html", {"article": article})


@login_required
def news_submit(request):
    pending = News.objects.filter(submitted_by=request.user, status=News.Status.PENDING).count()

    if request.method == "POST":
        if pending >= MAX_PENDING_PER_USER:
            messages.error(request, "You already have too many requests waiting for review. Please wait for the administrator.")
            return redirect("news_mine")

        form = NewsRequestForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.submitted_by = request.user
            item.status = News.Status.PENDING
            item.save()
            messages.success(request, "Thanks! Your news was sent to the administrator for review.")
            return redirect("news_mine")
    else:
        form = NewsRequestForm()

    return render(request, "helloweb/news_submit.html", {
        "form": form, "pending": pending, "limit": MAX_PENDING_PER_USER,
    })


@login_required
def news_mine(request):
    items = News.objects.filter(submitted_by=request.user).order_by("-created_at")
    return render(request, "helloweb/news_mine.html", {"items": items})