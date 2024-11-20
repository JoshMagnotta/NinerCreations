# Generated by Django 5.1.2 on 2024-11-17 22:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NinerCreations', '0008_topic_post_topics'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='joined_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]