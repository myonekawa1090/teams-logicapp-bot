#!/bin/bash
# Interactive setup script for Teams Bot configuration
# Run this before 'azd up' to customize your bot settings

echo ""
echo "=========================================="
echo "Teams Bot Configuration Setup"
echo "=========================================="
echo ""
echo "This script will configure your Teams bot metadata."
echo "Press Enter to accept default values shown in [brackets]."
echo ""

# Bot Information
read -p "Bot short name [GenBot]: " botNameShort
botNameShort=${botNameShort:-"GenBot"}

read -p "Bot full name [Generic Teams Bot]: " botNameFull
botNameFull=${botNameFull:-"Generic Teams Bot"}

# Description
echo ""
read -p "Short description (max 80 chars) [Generic Teams bot]: " descriptionShort
descriptionShort=${descriptionShort:-"Generic Teams bot"}

read -p "Full description (max 4000 chars) [Generic Teams bot]: " descriptionFull
descriptionFull=${descriptionFull:-"Generic Teams bot"}

# Organization Information
echo ""
read -p "Developer/Organization name [Your Organization]: " developerName
developerName=${developerName:-"Your Organization"}

read -p "Developer website URL [https://your-website.com]: " developerWebsite
developerWebsite=${developerWebsite:-"https://your-website.com"}

read -p "Privacy policy URL [https://your-website.com/privacy]: " privacyUrl
privacyUrl=${privacyUrl:-"https://your-website.com/privacy"}

read -p "Terms of use URL [https://your-website.com/terms]: " termsUrl
termsUrl=${termsUrl:-"https://your-website.com/terms"}

# Appearance
echo ""
read -p "Accent color (hex code) [#FFFFFF]: " accentColor
accentColor=${accentColor:-"#FFFFFF"}

# Set environment variables using azd
echo ""
echo "Setting environment variables..."

azd env set BOT_NAME_SHORT "$botNameShort"
azd env set BOT_NAME_FULL "$botNameFull"
azd env set DESCRIPTION_SHORT "$descriptionShort"
azd env set DESCRIPTION_FULL "$descriptionFull"
azd env set DEVELOPER_NAME "$developerName"
azd env set DEVELOPER_WEBSITE "$developerWebsite"
azd env set PRIVACY_URL "$privacyUrl"
azd env set TERMS_URL "$termsUrl"
azd env set ACCENT_COLOR "$accentColor"

echo ""
echo "=========================================="
echo "Configuration Summary"
echo "=========================================="
echo "Bot Name: $botNameShort ($botNameFull)"
echo "Description: $descriptionShort"
echo "Developer: $developerName"
echo "Website: $developerWebsite"
echo "Accent Color: $accentColor"
echo ""
echo "Configuration saved! You can now run 'azd up'"
echo ""
