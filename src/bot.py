#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Simple Teams Bot with Logic App Integration
Handles basic message interactions and integrates with Logic App
"""

import logging
import sys
import traceback
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import Activity, ActivityTypes

from handlers.teams_handler import TeamsHandler
from handlers.logicapp_handler import LogicAppHandler


class Bot(ActivityHandler):
    """Bot Framework Main Bot Class"""

    def __init__(self):
        super().__init__()
        self.teams_handler = TeamsHandler()
        self.logicapp_handler = LogicAppHandler()

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handle incoming messages

        Args:
            turn_context: Bot Framework turn context
        """
        text = (turn_context.activity.text or "").strip()

        # Remove bot name to extract command
        cleaned_text = self.teams_handler.extract_command(text)

        # Check for Adaptive Card submission
        value = getattr(turn_context.activity, 'value', None)
        if value:
            # Cancel button action
            if value.get("action") == "cancel":
                return await self.handle_cancel_action(turn_context)
            # Submit action
            elif "title" in value and "description" in value:
                return await self.handle_submit(turn_context, value)

        # Process commands
        if cleaned_text == "create" or cleaned_text == "":
            return await self.handle_create_item_command(turn_context)
        else:
            # Default to create item
            return await self.handle_create_item_command(turn_context)

    async def handle_create_item_command(self, turn_context: TurnContext):
        """
        Handle 'create item' command: Show Adaptive Card for input

        Args:
            turn_context: Bot Framework turn context
        """
        attachment = self.teams_handler.create_input_card()
        reply = Activity(
            type=ActivityTypes.message,
            attachments=[attachment]
        )
        await turn_context.send_activity(reply)

    async def handle_submit(self, turn_context: TurnContext, value: dict):
        """
        Handle Adaptive Card submission and POST to Logic App

        Args:
            turn_context: Bot Framework turn context
            value: Adaptive Card form data
        """
        try:
            # Extract Teams context information
            teams_info = await self.teams_handler.get_team_details(turn_context)
            user_info = self.teams_handler.extract_user_info(turn_context)
            activity_ids = self.teams_handler.extract_activity_ids(turn_context)

            # Extract form data
            form_data = {
                "title": value.get("title", ""),
                "description": value.get("description", "")
            }

            # Create payload for Logic App
            payload = self.logicapp_handler.create_payload(
                teams_info, user_info, activity_ids, form_data
            )

            # Send to Logic App
            result = await self.logicapp_handler.send_to_logic_app(payload)

            if result["success"]:
                await self.update_to_success_card(turn_context)
            else:
                await turn_context.send_activity(f"❌ Failed to send to Logic App: {result['error']}")

        except Exception as e:
            logging.error(f"Submission error: {e}")
            await turn_context.send_activity(f"❌ Error during submission: {e}")

    async def update_to_success_card(self, turn_context: TurnContext):
        """
        Update Adaptive Card to show success message

        Args:
            turn_context: Bot Framework turn context
        """
        try:
            attachment = self.teams_handler.create_success_card()

            # Update the original message
            await turn_context.update_activity(
                Activity(
                    type=ActivityTypes.message,
                    id=turn_context.activity.reply_to_id or turn_context.activity.id,
                    conversation=turn_context.activity.conversation,
                    attachments=[attachment]
                )
            )

        except Exception as e:
            logging.warning(f"Failed to update Adaptive Card: {e}")

    async def handle_cancel_action(self, turn_context: TurnContext):
        """
        Handle cancel button: Delete Adaptive Card

        Args:
            turn_context: Bot Framework turn context
        """
        try:
            await turn_context.delete_activity(turn_context.activity.reply_to_id or turn_context.activity.id)
        except Exception as e:
            logging.warning(f"Failed to delete Adaptive Card: {e}")
            await turn_context.send_activity("Cancelled.")

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        """
        Handle members added event

        Args:
            members_added: List of added members
            turn_context: Bot Framework turn context
        """
        pass


async def on_error(context: TurnContext, error: Exception):
    """
    Error handling

    Args:
        context: Bot Framework turn context
        error: Error that occurred
    """
    logging.error(f"Error: {error}")
    try:
        await context.send_activity("An error occurred.")
    except:
        pass
