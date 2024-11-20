# Generated by Django 5.1.1 on 2024-11-19 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_alter_auctionlisting_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='category',
            field=models.CharField(blank=True, choices=[('fashion', 'Fashion'), ('toys', 'Toys'), ('electronics', 'Electronics'), ('home', 'Home'), ('other', 'Other')], max_length=50, null=True),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]