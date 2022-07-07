# Generated by Django 4.0.6 on 2022-07-07 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store', models.CharField(max_length=25)),
                ('name', models.CharField(max_length=350)),
                ('brand', models.CharField(max_length=50)),
                ('link', models.CharField(default='', max_length=2083, unique=True)),
                ('normal_price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('sale_price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2)),
                ('num_of_ratings', models.IntegerField()),
                ('shipping', models.DecimalField(decimal_places=2, max_digits=7)),
                ('promotion', models.CharField(max_length=150)),
                ('out_of_stock', models.BooleanField()),
            ],
        ),
    ]
