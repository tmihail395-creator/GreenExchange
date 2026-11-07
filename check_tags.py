from django.db import IntegrityError, transaction
from helloweb.models import Post, Tag

# 3 тега
tag_django, _ = Tag.objects.get_or_create(name="django")
tag_python, _ = Tag.objects.get_or_create(name="python")
tag_tutorial, _ = Tag.objects.get_or_create(name="tutorial")

# 2 публикации
post1, _ = Post.objects.get_or_create(
    title="Getting started with Django",
    defaults={"content": "First steps with models and migrations."},
)
post2, _ = Post.objects.get_or_create(
    title="Django tips",
    defaults={"content": "Short practical tips."},
)

# у первой несколько тегов, у второй один, и он общий для обеих
post1.tags.set([tag_django, tag_python, tag_tutorial])
post2.tags.set([tag_django])

print("Post 1:", list(post1.tags.all()))
print("Post 2:", list(post2.tags.all()))
print("Posts with tag 'django':", list(tag_django.posts.all()))
print("Posts with tag 'python':", list(tag_python.posts.all()))

# unique=True: дубликат тега должен отклоняться
try:
    with transaction.atomic():
        Tag.objects.create(name="django")
    print("ERROR: duplicate was created")
except IntegrityError:
    print("Duplicate tag rejected (unique works)")