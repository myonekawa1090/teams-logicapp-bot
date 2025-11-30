#!/usr/bin/env python3
"""
Teams Handler
Manages Teams-specific operations (Adaptive Card creation, user info extraction)
"""

import logging
from botbuilder.core import TurnContext
from botbuilder.core.teams import TeamsInfo
from botbuilder.schema import Attachment
from config import DefaultConfig


class TeamsHandler:
    """Manages Teams operations"""

    def __init__(self):
        pass

    async def get_team_details(self, turn_context: TurnContext) -> dict:
        """
        Get team details using TeamsInfo API

        Args:
            turn_context: Bot Framework turn context

        Returns:
            Dictionary with tenant_id, group_id, team_id, channel_id, service_url
        """
        try:
            team_details = await TeamsInfo.get_team_details(turn_context)

            teams_info = {
                "tenant_id": getattr(team_details, 'tenant_id', ''),
                "group_id": getattr(team_details, 'aad_group_id', ''),
                "team_id": getattr(team_details, 'id', ''),
                "name": getattr(team_details, 'name', ''),
                "channel_id": getattr(turn_context.activity.conversation, 'id', ''),
                "service_url": getattr(turn_context.activity, 'service_url', '')
            }

            return teams_info

        except Exception as e:
            logging.warning(f"TeamsInfo.get_team_details failed: {e}")
            return {
                "tenant_id": "",
                "group_id": "",
                "team_id": "",
                "channel_id": "",
                "service_url": ""
            }

    def extract_command(self, text: str) -> str:
        """
        Remove bot name to extract command

        Args:
            text: User message text

        Returns:
            Command part without bot name
        """
        parts = text.strip().split(' ', 1)
        if len(parts) > 1:
            return parts[1].strip()
        else:
            return ""

    def create_input_card(self) -> Attachment:
        """
        Create simple Adaptive Card for title and description input

        Returns:
            Adaptive Card Attachment object
        """
        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "Create New Item",
                    "weight": "Bolder",
                    "size": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": "Title:",
                    "wrap": True
                },
                {
                    "type": "Input.Text",
                    "id": "title",
                    "placeholder": "Enter title"
                },
                {
                    "type": "TextBlock",
                    "text": "Description:",
                    "wrap": True
                },
                {
                    "type": "Input.Text",
                    "id": "description",
                    "placeholder": "Enter description",
                    "isMultiline": True
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "Submit"
                },
                {
                    "type": "Action.Submit",
                    "title": "Cancel",
                    "data": {"action": "cancel"}
                }
            ]
        }
        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive",
            content=card
        )

    def create_success_card(self) -> Attachment:
        """
        Create success message Adaptive Card

        Returns:
            Success card Attachment object
        """
        card = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "✅ Success",
                    "weight": "Bolder",
                    "color": "Good",
                    "size": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": "Your submission was successful!",
                    "wrap": True
                }
            ]
        }

        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive",
            content=card
        )

    def extract_user_info(self, turn_context: TurnContext) -> dict:
        """
        Extract user information from Teams context

        Args:
            turn_context: Bot Framework turn context

        Returns:
            Dictionary with user_name, user_aad_id, user_upn
        """
        user_name = getattr(turn_context.activity.from_property, 'name', "")
        user_aad_id = getattr(turn_context.activity.from_property, 'aad_object_id', "")

        return {
            "user_name": user_name,
            "user_aad_id": user_aad_id,
            "user_upn": user_name or "Unknown User"
        }

    def extract_activity_ids(self, turn_context: TurnContext) -> dict:
        """
        Extract message IDs and conversation ID from activity

        Args:
            turn_context: Bot Framework turn context

        Returns:
            Dictionary with channel_id, message_id, user_id
        """
        channel_id = getattr(turn_context.activity.conversation, 'id', "")
        message_id = getattr(turn_context.activity, 'id', "")
        user_id = getattr(turn_context.activity.from_property, 'id', "")

        return {
            "channel_id": channel_id,
            "message_id": message_id,
            "user_id": user_id
        }
