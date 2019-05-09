# Generated by Django 2.0.6 on 2019-05-09 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20190509_2045'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_type', models.CharField(choices=[('close', 'close'), ('open', 'open')], default='close', max_length=128)),
                ('open_answer', models.CharField(blank=True, max_length=512, null=True)),
                ('close_answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.Variant')),
            ],
        ),
        migrations.RemoveField(
            model_name='useranswer',
            name='variant',
        ),
        migrations.AlterField(
            model_name='useranswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.StoreQuestion'),
        ),
        migrations.AddField(
            model_name='useranswer',
            name='answer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='blog.StoreAnswer'),
        ),
    ]