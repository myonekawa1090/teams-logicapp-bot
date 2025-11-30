"""
Environment Variable Configuration
Manages Bot Framework and Azure service authentication
"""

import os


class DefaultConfig:
    """Default configuration class - loads settings from environment variables"""

    # Bot Framework authentication
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_TYPE = os.environ.get("MicrosoftAppType", "")
    APP_TENANTID = os.environ.get("MicrosoftAppTenantId", "")

    # Logic App endpoint (requires manual configuration)
    LOGICAPP_ENDPOINT = os.environ.get("LOGICAPP_ENDPOINT", "")
