@description('Base name for all resources')
param baseName string

@description('Location for all resources')
param location string = resourceGroup().location

@description('App Service Plan SKU')
param appServicePlanSku string

@description('Storage Account SKU')
param storageAccountSku string = 'Standard_LRS'

// Variables
var uniqueSuffix = uniqueString(resourceGroup().id)
var webAppName = '${baseName}-${uniqueSuffix}'
var appServicePlanName = '${baseName}-plan'
var botName = '${baseName}-bot'
var identityName = '${baseName}-identity'
var logicAppStandardName = '${baseName}-logicstd-${uniqueSuffix}'
var storageAccountName = toLower('${replace(baseName, '-', '')}${take(uniqueSuffix, 6)}st')


// User Assigned Managed Identity
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

// Storage Account for Logic App Standard
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: {
    'SecurityControl': 'ignore'
  }
  sku: {
    name: storageAccountSku
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    publicNetworkAccess: 'Enabled'
  }
}






// App Service Plan for Logic App Standard
resource logicAppServicePlan 'Microsoft.Web/serverfarms@2024-11-01' = {
  name: '${logicAppStandardName}-plan'
  location: location
  sku: {
    name: 'WS1'
    tier: 'WorkflowStandard'
  }
  kind: 'elastic'
  properties: {
    targetWorkerCount: 1
    maximumElasticWorkerCount: 20
    isSpot: false
    reserved: false
    isXenon: false
    hyperV: false
    targetWorkerSizeId: 0
    perSiteScaling: false
    elasticScaleEnabled: true
    zoneRedundant: false
  }
}

// Logic App Standard with Regional VNet Integration
resource logicAppStandard 'Microsoft.Web/sites@2024-11-01' = {
  name: logicAppStandardName
  location: location
  kind: 'functionapp,workflowapp'
  tags: {
    'azd-service-name': 'logicapp'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: logicAppServicePlan.id
    reserved: false
    isXenon: false
    hyperV: false
    publicNetworkAccess: 'Enabled'
    siteConfig: {
      netFrameworkVersion: 'v4.0'
      vnetRouteAllEnabled: false
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=core.windows.net;AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=core.windows.net;AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(logicAppStandardName)
        }
        {
          name: 'AzureFunctionsJobHost__extensionBundle__id'
          value: 'Microsoft.Azure.Functions.ExtensionBundle.Workflows'
        }
        {
          name: 'AzureFunctionsJobHost__extensionBundle__version'
          value: '[1.*, 2.0.0)'
        }
        {
          name: 'APP_KIND'
          value: 'workflowApp'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'dotnet'
        }
        {
          name: 'WEBSITE_NODE_DEFAULT_VERSION'
          value: '~20'
        }
      ]
      use32BitWorkerProcess: false
      ftpsState: 'FtpsOnly'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }
}



// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2024-11-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: appServicePlanSku
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// Web App
resource webApp 'Microsoft.Web/sites@2024-11-01' = {
  name: webAppName
  location: location
  tags: {
    'azd-service-name': 'bot'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appCommandLine: 'python3 -m pip install -r requirements.txt && python3 app.py'
      appSettings: [
        {
          name: 'MicrosoftAppId'
          value: managedIdentity.properties.clientId
        }
        {
          name: 'MicrosoftAppPassword'
          value: ''
        }
        {
          name: 'MicrosoftAppType'
          value: 'UserAssignedMSI'
        }
        {
          name: 'MicrosoftAppTenantId'
          value: managedIdentity.properties.tenantId
        }
        {
          name: 'Port'
          value: '8000'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'ENABLE_ORYX_BUILD'
          value: 'false'
        }
        {
          name: 'PYTHON_VERSION'
          value: '3.11'
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'true'
        }
      ]
      httpLoggingEnabled: true
      detailedErrorLoggingEnabled: true
      requestTracingEnabled: true
      logsDirectorySizeLimit: 35
    }
  }
}


// Bot Service
resource botService 'Microsoft.BotService/botServices@2022-09-15' = {
  name: botName
  location: 'global'
  sku: {
    name: 'F0'
  }
  kind: 'azurebot'
  properties: {
    displayName: botName
    endpoint: 'https://${webApp.properties.defaultHostName}/api/messages'
    msaAppId: managedIdentity.properties.clientId
    msaAppMSIResourceId: managedIdentity.id
    msaAppTenantId: managedIdentity.properties.tenantId
    msaAppType: 'UserAssignedMSI'
  }
}

// Teams Channel for Bot
resource teamsChannel 'Microsoft.BotService/botServices/channels@2022-09-15' = {
  parent: botService
  location: 'global'
  name: 'MsTeamsChannel'
  properties: {
    channelName: 'MsTeamsChannel'
    properties: {
      isEnabled: true
    }
  }
}

// Role assignments for Web App managed identity to access Logic App
// Logic App Contributor role for workflow management
resource logicAppContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(logicAppStandard.id, managedIdentity.id, 'b24988ac-6180-42a0-ab88-20f7382dd24c')
  scope: logicAppStandard
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b24988ac-6180-42a0-ab88-20f7382dd24c') // Contributor role
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Logic App Standard Operator role for trigger execution
resource logicAppOperatorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(logicAppStandard.id, managedIdentity.id, '515c2055-d9d4-4321-b1b9-bd0c9a0f79fe')
  scope: logicAppStandard
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '515c2055-d9d4-4321-b1b9-bd0c9a0f79fe') // Logic App Standard Operator
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs for azd
output WEB_APP_URL string = 'https://${webApp.properties.defaultHostName}'
output BOT_ENDPOINT string = 'https://${webApp.properties.defaultHostName}/api/messages'
output MANAGED_IDENTITY_CLIENT_ID string = managedIdentity.properties.clientId
output MANAGED_IDENTITY_ID string = managedIdentity.id
output WEB_APP_NAME string = webApp.name
output BOT_NAME string = botService.name
output LOGICAPP_ENDPOINT string = 'PLEASE_SET_MANUALLY: Get from Logic App HTTP trigger in Azure Portal'

// Logic App Standard outputs
output LOGIC_APP_STANDARD_NAME string = logicAppStandard.name
output LOGIC_APP_STANDARD_URL string = 'https://${logicAppStandard.properties.defaultHostName}'
output LOGIC_APP_STANDARD_IDENTITY_ID string = logicAppStandard.identity.principalId
output STORAGE_ACCOUNT_NAME string = storageAccount.name
output LOGIC_APP_SERVICE_PLAN_NAME string = logicAppServicePlan.name
