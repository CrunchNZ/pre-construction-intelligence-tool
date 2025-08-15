@description('The name of the Pre-Construction Intelligence Tool deployment')
param deploymentName string = 'precon-intelligence'

@description('The location for all resources')
param location string = resourceGroup().location

@description('Environment (dev, staging, prod)')
param environment string = 'dev'

@description('Django backend app service plan SKU')
param backendAppServicePlanSku string = 'B1'

@description('Frontend app service plan SKU')
param frontendAppServicePlanSku string = 'F1'

@description('PostgreSQL server admin username')
param dbAdminUsername string = 'preconadmin'

@description('PostgreSQL server admin password')
@secure()
param dbAdminPassword string

@description('Redis cache SKU')
param redisCacheSku string = 'Basic'

@description('Key Vault SKU')
param keyVaultSku string = 'standard'

// Variables
var backendAppName = '${deploymentName}-backend-${environment}'
var frontendAppName = '${deploymentName}-frontend-${environment}'
var dbServerName = '${deploymentName}-db-${environment}'
var redisCacheName = '${deploymentName}-redis-${environment}'
var keyVaultName = '${deploymentName}-kv-${environment}'
var storageAccountName = '${deploymentName}storage${environment}'

// App Service Plans
resource backendAppServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${backendAppName}-plan'
  location: location
  sku: {
    name: backendAppServicePlanSku
    tier: backendAppServicePlanSku == 'F1' ? 'Free' : 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource frontendAppServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${frontendAppName}-plan'
  location: location
  sku: {
    name: frontendAppServicePlanSku
    tier: frontendAppServicePlanSku == 'F1' ? 'Free' : 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// PostgreSQL Database
resource postgresServer 'Microsoft.DBforPostgreSQL/servers@2023-06-01-preview' = {
  name: dbServerName
  location: location
  sku: {
    name: 'B_Gen5_1'
    tier: 'Basic'
    capacity: 1
    family: 'Gen5'
  }
  properties: {
    administratorLogin: dbAdminUsername
    administratorLoginPassword: dbAdminPassword
    version: '15'
    storageProfile: {
      storageMB: 5120
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    sslEnforcement: 'Enabled'
    minimalTlsVersion: 'TLS1_2'
  }
}

resource postgresDatabase 'Microsoft.DBforPostgreSQL/servers/databases@2023-06-01-preview' = {
  parent: postgresServer
  name: 'preconstruction_intelligence'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Redis Cache
resource redisCache 'Microsoft.Cache/Redis@2023-08-01' = {
  name: redisCacheName
  location: location
  sku: {
    name: redisCacheSku
    family: 'C'
    capacity: 0
  }
  properties: {
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: keyVaultSku
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false
  }
}

// Storage Account for static files and media
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

// Backend Web App
resource backendWebApp 'Microsoft.Web/sites@2023-01-01' = {
  name: backendAppName
  location: location
  kind: 'linux'
  properties: {
    serverFarmId: backendAppServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DB_HOST'
          value: postgresServer.properties.fullyQualifiedDomainName
        }
        {
          name: 'DB_NAME'
          value: postgresDatabase.name
        }
        {
          name: 'DB_USER'
          value: dbAdminUsername
        }
        {
          name: 'DB_PASSWORD'
          value: dbAdminPassword
        }
        {
          name: 'REDIS_HOST'
          value: redisCache.properties.hostName
        }
        {
          name: 'REDIS_PORT'
          value: string(redisCache.properties.port)
        }
        {
          name: 'REDIS_SSL'
          value: 'true'
        }
        {
          name: 'AZURE_STORAGE_ACCOUNT'
          value: storageAccount.name
        }
      ]
    }
  }
}

// Frontend Web App
resource frontendWebApp 'Microsoft.Web/sites@2023-01-01' = {
  name: frontendAppName
  location: location
  kind: 'linux'
  properties: {
    serverFarmId: frontendAppServicePlan.id
    siteConfig: {
      linuxFxVersion: 'NODE|18-lts'
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'REACT_APP_API_BASE_URL'
          value: 'https://${backendWebApp.properties.defaultHostName}'
        }
      ]
    }
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${deploymentName}-ai-${environment}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: ''
  }
}

// Outputs
output backendUrl string = 'https://${backendWebApp.properties.defaultHostName}'
output frontendUrl string = 'https://${frontendWebApp.properties.defaultHostName}'
output databaseServer string = postgresServer.properties.fullyQualifiedDomainName
output redisHost string = redisCache.properties.hostName
output keyVaultUri string = keyVault.properties.vaultUri
output storageAccountName string = storageAccount.name
output appInsightsKey string = appInsights.properties.InstrumentationKey
