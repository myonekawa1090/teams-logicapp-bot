#!/usr/bin/env python3
"""
Logic App Handler
Manages communication with Logic App and payload creation
"""

import logging
import requests
import json
from config import DefaultConfig


class LogicAppHandler:
    """Manages communication with Logic App"""

    def __init__(self):
        pass

    async def send_to_logic_app(self, payload: dict) -> dict:
        """
        Send data to Logic App

        Args:
            payload: Data to send to Logic App

        Returns:
            Dictionary with success flag and response
        """
        url = DefaultConfig.LOGICAPP_ENDPOINT

        if not url:
            return {"success": False, "error": "LOGICAPP_ENDPOINT not configured"}

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            res = requests.post(url, json=payload, headers=headers)

            if res.status_code == 200:
                return {
                    "success": True,
                    "response": res.text
                }
            else:
                error_msg = f"Logic App request failed (HTTP {res.status_code}): {res.text}"
                logging.error(error_msg)
                return {"success": False, "error": error_msg}

        except Exception as e:
            error_msg = f"Logic App connection error: {e}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}

    def create_payload(self, teams_info: dict, user_info: dict, activity_ids: dict,
                      form_data: dict) -> dict:
        """
        Create payload to send to Logic App

        Args:
            teams_info: Teams information (tenant_id, group_id, team_id, etc.)
            user_info: User information (UPN, AAD ID, etc.)
            activity_ids: Activity IDs (channel_id, message_id, etc.)
            form_data: Form data (title, description)

        Returns:
            JSON payload to send to Logic App
        """
        payload = {
            "teamId": teams_info.get('team_id', ''),
            "channelId": activity_ids.get('channel_id', ''),
            "messageId": activity_ids.get('message_id', ''),
            "userId": activity_ids.get('user_id', ''),
            "userName": user_info.get('user_name', ''),
            "title": form_data.get("title", ""),
            "description": form_data.get("description", ""),
            "timestamp": ""
        }

        return payload
