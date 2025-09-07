param name string
param location string = resourceGroup().location
param tags object = {}

param allowBlobPublicAccess bool = false
param containers array = [
  {
    name: 'static'
    publicAccess: 'Blob'
  }
  {
    name: 'media'
    publicAccess: 'Blob'
  }
]
param kind string = 'StorageV2'
param minimumTlsVersion string = 'TLS1_2'
param sku object = { name: 'Standard_LRS' }

resource storage 'Microsoft.Storage/storageAccounts@2022-05-01' = {
  name: name
  location: location
  tags: tags
  kind: kind
  sku: sku
  properties: {
    minimumTlsVersion: minimumTlsVersion
    allowBlobPublicAccess: allowBlobPublicAccess
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }

  resource blobServices 'blobServices@2022-05-01' = {
    name: 'default'

    resource container 'containers@2022-05-01' = [for container in containers: {
      name: container.name
      properties: {
        publicAccess: container.publicAccess
      }
    }]
  }
}

output name string = storage.name
output primaryEndpoints object = storage.properties.primaryEndpoints
