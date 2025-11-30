# Simple Teams Bot with Logic App Integration

A minimalist Microsoft Teams bot that demonstrates integration with Azure Logic App. The bot responds to a single command (`create`) and displays an Adaptive Card for collecting title and description input.

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

- Python 3.11+
- Azure subscription
- Azure CLI
- Azure Developer CLI (azd)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd teams-logicapp-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt
```

### 2. Deploy to Azure

```bash
# Login to Azure
azd auth login

# (Optional) Configure bot metadata
./setup-bot-config.sh  # or setup-bot-config.ps1 on Windows

# Deploy infrastructure and application
azd up
```

The deployment will automatically:
- Provision all Azure resources
- Deploy the Logic App workflow
- Configure the Logic App endpoint in the App Service
- Deploy the bot application

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
└── infra/                        # Azure infrastructure (Bicep)
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

## Customization

### Add New Commands

Edit `src/bot.py` and add command handlers in the `on_message_activity` method.

### Modify Adaptive Card

Edit the `create_input_card` method in `src/handlers/teams_handler.py`.

### Change Logic App Integration

Modify `src/handlers/logicapp_handler.py` to change the payload structure or add processing logic.

## Configuration

| Environment Variable | Description | Required |
|---------------------|-------------|----------|
| `MicrosoftAppId` | Bot Framework App ID | Yes |
| `MicrosoftAppPassword` | Bot Framework App Password | Yes |
| `MicrosoftAppType` | Bot type (usually MultiTenant) | Yes |
| `MicrosoftAppTenantId` | Azure AD Tenant ID | Yes |
| `LOGICAPP_ENDPOINT` | Logic App HTTP trigger URL | Yes |

## Development

### Running Tests

```bash
# Add your test commands here
pytest
```

### Debugging

Set logging level in `src/app.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
