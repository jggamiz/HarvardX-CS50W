# Generated by Django 5.1.1 on 2024-11-20 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_remove_auctionlisting_watchers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auctionlisting',
            name='watchlist',
        ),
    ]