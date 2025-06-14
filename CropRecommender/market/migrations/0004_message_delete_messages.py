# Generated by Django 5.1.4 on 2025-03-24 20:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Social', '0007_alter_post_file'),
        ('market', '0003_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='market.productlisting')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='Social.userprofile')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='Social.userprofile')),
            ],
        ),
        migrations.DeleteModel(
            name='messages',
        ),
    ]
