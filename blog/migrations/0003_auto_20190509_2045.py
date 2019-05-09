# Generated by Django 2.0.6 on 2019-05-09 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20190509_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storequestion',
            name='close_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.Question'),
        ),
        migrations.AlterField(
            model_name='storequestion',
            name='open_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.OpenQuestion'),
        ),
    ]