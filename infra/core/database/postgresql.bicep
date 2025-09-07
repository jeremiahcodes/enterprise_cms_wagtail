param name string
param location string = resourceGroup().location
param tags object = {}

param keyVaultName string
param databaseName string = 'wagtaildb'
param administratorLogin string = 'wagtailadmin'
param administratorLoginPassword string = newGuid()

resource postgresqlServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  location: location
  tags: tags
  name: name
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '15'
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }

  resource database 'databases@2022-12-01' = {
    name: databaseName
    properties: {
      charset: 'utf8'
      collation: 'en_US.utf8'
    }
  }

  resource firewallRules 'firewallRules@2022-12-01' = {
    name: 'AllowAllWindowsAzureIps'
    properties: {
      // Allow access from Azure services
      startIpAddress: '0.0.0.0'
      endIpAddress: '0.0.0.0'
    }
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: keyVaultName
}

resource postgresqlAdminPasswordSecret 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = {
  parent: keyVault
  name: 'postgresql-admin-password'
  properties: {
    value: administratorLoginPassword
  }
}

resource postgresqlConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2022-07-01' = {
  parent: keyVault
  name: 'postgresql-connection-string'
  properties: {
    value: 'postgresql://${administratorLogin}:${administratorLoginPassword}@${postgresqlServer.properties.fullyQualifiedDomainName}:5432/${databaseName}?sslmode=require'
  }
}

output name string = postgresqlServer.name
output databaseName string = databaseName
output connectionStringSecretName string = postgresqlConnectionStringSecret.name
