# Generated by Django 5.0.3 on 2024-04-08 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0015_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='aadhar_card_image',
            field=models.ImageField(blank=True, null=True, upload_to='aadhar_cards/'),
        ),
    ]
