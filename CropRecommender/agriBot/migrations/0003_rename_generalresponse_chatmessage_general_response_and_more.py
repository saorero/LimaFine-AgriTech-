# Generated by Django 5.1.4 on 2025-04-22 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agriBot', '0002_rename_conversationid_chatmessage_conversation_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatmessage',
            old_name='generalResponse',
            new_name='general_response',
        ),
        migrations.RenameField(
            model_name='chatmessage',
            old_name='ragResponse',
            new_name='rag_response',
        ),
    ]
