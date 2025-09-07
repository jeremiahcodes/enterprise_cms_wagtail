# Deploy Wagtail CMS to Azure Container Apps

This guide will help you deploy your Wagtail CMS application to Azure using Azure Container Apps, PostgreSQL, and Blob Storage.

## Prerequisites

1. Azure subscription
2. Azure Developer CLI (azd) installed
3. Docker installed and running
4. Azure CLI installed

## Architecture Overview

Your Wagtail application will be deployed with:

- **Azure Container Apps**: Hosts the containerized Django/Wagtail application
- **Azure Database for PostgreSQL**: Managed PostgreSQL database
- **Azure Blob Storage**: Stores static files and media uploads
- **Azure Key Vault**: Securely stores database connection strings and secrets
- **Azure Container Registry**: Stores your Docker images
- **Application Insights**: Application monitoring and logging

## Step 1: Install Azure Developer CLI

### macOS (using Homebrew)

```bash
brew tap azure/azd && brew install azd
```

### Alternative installation methods

Visit: https://docs.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd

## Step 2: Login to Azure

```bash
azd auth login
```

## Step 3: Initialize the Azure Environment

```bash
azd init
```

When prompted:

- Choose "Use code in the current directory"
- Set environment name (e.g., "wagtail-prod")
- Select your Azure subscription
- Choose your preferred Azure region (e.g., "East US")

## Step 4: Deploy to Azure

```bash
azd up
```

This command will:

1. Build and push your Docker image to Azure Container Registry
2. Provision all Azure resources (Container Apps, PostgreSQL, Storage, etc.)
3. Deploy your application
4. Run database migrations
5. Set up all necessary configurations

## Step 5: Create a Superuser (After Deployment)

After deployment, you'll need to create a superuser for the Wagtail admin:

1. Get the container app name from the deployment output
2. Use Azure CLI to run commands in the container:

```bash
az containerapp exec --name <your-container-app-name> --resource-group <your-resource-group> --command "/bin/bash"
```

Then inside the container:

```bash
python manage.py createsuperuser
```

## Step 6: Access Your Application

After deployment, `azd up` will output the URL of your deployed application. You can access:

- **Main site**: `https://<your-app-url>`
- **Admin panel**: `https://<your-app-url>/admin`
- **Wagtail admin**: `https://<your-app-url>/cms-admin`

## Managing Your Deployment

### View deployment status

```bash
azd show
```

### Update your application

```bash
azd deploy
```

### View logs

```bash
azd logs
```

### Clean up resources

```bash
azd down
```

## Environment Variables

The following environment variables are automatically configured:

- `DJANGO_SETTINGS_MODULE=cms.settings.production`
- `DATABASE_URL`: PostgreSQL connection string (from Key Vault)
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Configured for your domain
- `AZURE_STORAGE_ACCOUNT_NAME`: Storage account name
- `AZURE_STORAGE_ACCOUNT_KEY`: Storage account key
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Application monitoring

## Custom Domain (Optional)

To use a custom domain:

1. Configure your domain's DNS to point to the Container App
2. Update the `ALLOWED_HOSTS` environment variable
3. Configure SSL certificate in Azure Container Apps

## Monitoring

Your application includes:

- **Application Insights**: Performance monitoring and error tracking
- **Container Apps logs**: Application and system logs
- **PostgreSQL metrics**: Database performance monitoring

Access monitoring through the Azure Portal or use `azd logs` for quick access.

## Security Features

- Database connection strings stored in Azure Key Vault
- Managed identity for secure access to Azure services
- HTTPS enforcement
- Security headers configured
- Network security through Azure Container Apps environment

## Troubleshooting

### Check application logs

```bash
azd logs
```

### Access container shell

```bash
az containerapp exec --name <container-app-name> --resource-group <resource-group> --command "/bin/bash"
```

### Check resource status

```bash
az resource list --resource-group <resource-group> --output table
```

### Database connection issues

- Verify database firewall rules allow Azure services
- Check Key Vault access policies
- Verify managed identity permissions

## Cost Optimization

- Container Apps uses consumption-based pricing
- PostgreSQL uses Burstable tier for cost efficiency
- Storage account uses Standard LRS for cost-effectiveness
- Consider scaling down resources for development environments

## Next Steps

1. Configure email backend for password resets
2. Set up custom domain and SSL
3. Configure backup strategies
4. Set up CI/CD pipeline for automated deployments
5. Configure monitoring alerts
