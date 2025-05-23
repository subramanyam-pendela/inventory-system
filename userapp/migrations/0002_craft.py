# Generated by Django 5.0.3 on 2024-03-22 09:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Craft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('materials_used', models.CharField(blank=True, max_length=255)),
                ('category', models.CharField(choices=[('Textiles', 'Textiles'), ('Paintings', 'Paintings'), ('Stone Craft', 'Stone Craft'), ('Accessories', 'Accessories'), ('Jewelry', 'Jewelry'), ('Handmade Crafts', 'Handmade Crafts'), ('Leather Work', 'Leather Work'), ('Pottery and Ceramics', 'Pottery and Ceramics'), ('Metalwork', 'Metalwork'), ('Others', 'Others')], default='Others', max_length=50)),
                ('image', models.ImageField(blank=True, null=True, upload_to='craft_images/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userapp.user')),
            ],
        ),
    ]
