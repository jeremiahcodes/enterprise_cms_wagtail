param name string
param location string = resourceGroup().location
param tags object = {}

param sku object = {
  name: 'F1'
  tier: 'Free'
}

param kind string = 'linux'
param reserved bool = true

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  kind: kind
  properties: {
    reserved: reserved
  }
}

output name string = appServicePlan.name
output id string = appServicePlan.id
