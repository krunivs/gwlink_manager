# Generated by Django 3.2.20 on 2023-10-15 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gwlink_migration', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='migrationrequest',
            name='end_date',
            field=models.CharField(max_length=50, null=True, verbose_name='end date(timestamp)'),
        ),
        migrations.AlterField(
            model_name='migrationrequest',
            name='issued_date',
            field=models.CharField(max_length=50, verbose_name='issued date(timestamp)'),
        ),
        migrations.AlterField(
            model_name='migrationrequest',
            name='start_date',
            field=models.CharField(max_length=50, null=True, verbose_name='start date(timestamp)'),
        ),
        migrations.AlterField(
            model_name='migrationrequest',
            name='updated_date',
            field=models.CharField(max_length=50, null=True, verbose_name='update date(timestamp)'),
        ),
        migrations.AlterField(
            model_name='migrationtask',
            name='end_date',
            field=models.CharField(max_length=50, null=True, verbose_name='end date(timestamp)'),
        ),
        migrations.AlterField(
            model_name='migrationtask',
            name='issued_date',
            field=models.CharField(max_length=50, verbose_name='issue date(timestamp)'),
        ),
        migrations.AlterField(
            model_name='migrationtask',
            name='start_date',
            field=models.CharField(max_length=50, null=True, verbose_name='start date(timestamp)'),
        ),
    ]
