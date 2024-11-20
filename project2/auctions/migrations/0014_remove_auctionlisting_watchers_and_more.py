# Generated by Django 5.1.1 on 2024-11-20 09:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_remove_auctionlisting_watchlist_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auctionlisting',
            name='watchers',
        ),
        migrations.AddField(
            model_name='auctionlisting',
            name='watchlist',
            field=models.ManyToManyField(blank=True, related_name='watched_listings', to=settings.AUTH_USER_MODEL),
        ),
    ]