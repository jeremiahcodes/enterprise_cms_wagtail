# Deploy Wagtail CMS to Azure App Service (Free/Low-Cost Tier)

This guide will help you deploy your Wagtail CMS application to Azure using Azure App Service with the lowest cost tiers, PostgreSQL, and Blob Storage.

## Prerequisites

1. Azure subscription
2. Azure Developer CLI (azd) installed
3. Docker installed and running
4. Azure CLI installed

## Architecture Overview

Your Wagtail application will be deployed with:

- **Azure App Service (Free Tier)**: Hosts the containerized Django/Wagtail application
- **Azure Database for PostgreSQL (Burstable Tier)**: Managed PostgreSQL database - lowest cost tier
- **Azure Blob Storage (Standard LRS)**: Stores static files and media uploads - most cost-effective storage
- **Azure Key Vault**: Securely stores database connection strings and secrets
- **Azure Container Registry (Basic Tier)**: Stores your Docker images - lowest cost tier
- **Application Insights**: Application monitoring and logging

## Cost Breakdown (Estimated Monthly)

- **App Service (F1 Free Tier)**: $0/month (limited to 60 minutes/day, 1GB storage)
- **PostgreSQL (Burstable B1ms)**: ~$12-15/month
- **Storage Account (Standard LRS)**: ~$1-3/month (depending on usage)
- **Container Registry (Basic)**: ~$5/month (includes 10GB storage)
- **Application Insights**: Free tier available (limited data retention)
- **Key Vault**: ~$0.03/month for operations

**Total estimated cost: ~$18-23/month**

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
2. Provision all Azure resources (App Service, PostgreSQL, Storage, etc.)
3. Deploy your application to App Service
4. Run database migrations
5. Set up all necessary configurations

## Step 5: Create a Superuser (After Deployment)

After deployment, you'll need to create a superuser for the Wagtail admin:

1. Get the app service name from the deployment output
2. Use Azure CLI to run commands in the app service:

```bash
# Enable SSH access to the container
az webapp ssh --name <your-app-service-name> --resource-group <your-resource-group>
```

Then inside the container:

```bash
python manage.py createsuperuser
```

Alternatively, you can use the Azure portal's "Console" feature in your App Service.

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
- **App Service logs**: Application and system logs
- **PostgreSQL metrics**: Database performance monitoring

Access monitoring through the Azure Portal or use `azd logs` for quick access.

## Security Features

- Database connection strings stored in Azure Key Vault
- Managed identity for secure access to Azure services
- HTTPS enforcement
- Security headers configured
- Network security through Azure App Service

## Free Tier Limitations

The Azure App Service Free tier has some limitations:

- **60 minutes of compute time per day**: Your app will stop after 60 minutes of cumulative usage
- **1GB storage**: Limited disk space for your application
- **No custom domains**: You'll use the azurewebsites.net domain
- **No SSL certificates**: HTTPS is available but only on the default domain
- **No auto-scaling**: Fixed to 1 instance

For production use, consider upgrading to a Basic (B1) tier (~$13/month) which removes these limitations.

## Troubleshooting

### Check application logs

```bash
azd logs
```

### Access app service shell

```bash
az webapp ssh --name <app-service-name> --resource-group <resource-group>
```

### Check resource status

```bash
az resource list --resource-group <resource-group> --output table
```

### Database connection issues

- Verify database firewall rules allow Azure services
- Check Key Vault access policies
- Verify managed identity permissions

### Free tier timeout issues

If your app stops due to the 60-minute daily limit:

- Wait until the next day (resets at midnight UTC)
- Consider upgrading to Basic tier for production
- Monitor usage through Azure portal

## Cost Optimization

- App Service Free tier: $0/month (with limitations)
- PostgreSQL Burstable tier: Lowest cost database option
- Storage account Standard LRS: Most cost-effective storage
- Consider pausing/stopping resources during development
- Monitor usage to avoid unexpected charges

## Upgrading from Free Tier

To upgrade your App Service to remove limitations:

```bash
az appservice plan update --name <app-service-plan-name> --resource-group <resource-group> --sku B1
```

This will cost approximately $13/month but removes the 60-minute limit and adds more features.

## Next Steps

1. Configure email backend for password resets
2. Set up custom domain and SSL
3. Configure backup strategies
4. Set up CI/CD pipeline for automated deployments
5. Configure monitoring alerts
