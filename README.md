# Simple Teams Bot with Logic App Integration

A minimalist Microsoft Teams bot that demonstrates integration with Azure Logic App. The bot responds to a single command (`create`) and displays an Adaptive Card for collecting title and description input.

**This is a starter template** designed to be extended with your own bot commands and Logic App workflows. Use the provided code structure as a foundation to add custom commands, Adaptive Cards, and business logic processing through Logic Apps.

## Features

- **Single Command**: Respond to `create` or bot mention
- **Simple Adaptive Card**: Collects title and description from users
- **Logic App Integration**: Sends form data to Azure Logic App for processing
- **Clean Architecture**: Minimal, easy-to-understand codebase

## Architecture

```
User → Teams Bot → Adaptive Card → Submit → Logic App → Response
```

## Prerequisites

- Azure subscription
- Azure Developer CLI (azd) - [Install here](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd teams-logicapp-bot
```

### 2. Deploy to Azure

```bash
# Login to Azure
azd auth login

# Initialize Azure Developer CLI
azd init

# Configure bot metadata
./setup-bot-config.sh

# Deploy infrastructure and application
azd up
```

The deployment will automatically:
- Provision all Azure resources
- Deploy the Logic App workflow
- Configure the Logic App endpoint in the App Service
- Deploy the bot application

## Azure Resources

The Bicep template deploys the following Azure resources:

| Resource Type | Purpose | SKU/Tier |
|--------------|---------|----------|
| **User Assigned Managed Identity** | Bot authentication and authorization | - |
| **Storage Account** | Backend storage for Logic App Standard | Standard_LRS |
| **App Service Plan (Linux)** | Hosting plan for Teams Bot | B1 (configurable) |
| **App Service (Web App)** | Runs the Python bot application (Python 3.11) | - |
| **App Service Plan (Workflow)** | Hosting plan for Logic App Standard | WS1 (WorkflowStandard) |
| **Logic App Standard** | Processes form submissions | - |
| **Bot Service** | Azure Bot Service registration | F0 (Free) |

## Project Structure

```
teams-logicapp-bot/
├── src/
│   ├── app.py                    # Main application entry point
│   ├── bot.py                    # Bot logic and command handling
│   ├── config.py                 # Configuration management
│   ├── requirements.txt          # Python dependencies
│   └── handlers/
│       ├── teams_handler.py      # Teams and Adaptive Card operations
│       └── logicapp_handler.py   # Logic App integration
├── templates/
│   ├── logicapp/                 # Logic App workflow templates
│   └── teams-app/                # Teams app manifest templates
├── infra/                        # Azure infrastructure (Bicep)
├── azure.yaml                    # Azure Developer CLI configuration
└── setup-bot-config.sh           # Bot metadata configuration script
```

## How It Works

1. **User Interaction**: User mentions the bot or types `@BotName create`
2. **Adaptive Card**: Bot displays a card with Title and Description input fields
3. **Submission**: User fills the form and clicks Submit
4. **Processing**: Bot sends the data to Logic App endpoint
5. **Response**: Bot updates the card to show success message

## Logic App Payload

The bot sends the following JSON payload to Logic App:

```json
{
  "teamId": "team-id",
  "channelId": "channel-id",
  "messageId": "message-id",
  "userId": "user-id",
  "userName": "User Name",
  "title": "User entered title",
  "description": "User entered description",
  "timestamp": ""
}
```

## Extending This Template

This starter template provides the basic structure for a Teams bot with Logic App integration. You're expected to customize and extend it for your specific use cases:

### Add New Commands

Edit `src/bot.py` and add command handlers in the `on_message_activity` method. Follow the pattern used by the existing `create` command to handle new bot commands.

### Modify Adaptive Cards

Edit the `create_input_card` method in `src/handlers/teams_handler.py` to add new form fields, change layouts, or create entirely new Adaptive Cards for different commands.

### Extend Logic App Workflows

1. Add new workflow definitions in `templates/logicapp/` directory (following the `processItem` structure)
2. Modify `src/handlers/logicapp_handler.py` to change the payload structure or add new Logic App integrations
3. Update the deployment to include your new workflows