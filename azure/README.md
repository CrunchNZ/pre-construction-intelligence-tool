# Azure Configuration and Deployment

This directory contains Azure infrastructure configuration and deployment scripts for the Pre-Construction Intelligence Tool.

## Files Overview

### Infrastructure
- **`main.bicep`** - Azure Bicep template defining all infrastructure resources
- **`deploy.ps1`** - PowerShell deployment script for automated infrastructure deployment

### CI/CD
- **`azure-pipelines.yml`** - Azure DevOps pipeline configuration for automated builds and deployments

## Infrastructure Components

The Bicep template creates the following Azure resources:

### Compute
- **App Service Plans**: Separate plans for backend (Django) and frontend (React)
- **Web Apps**: Django backend and React frontend applications

### Database
- **PostgreSQL Server**: Managed database for the Django application
- **Database**: `preconstruction_intelligence` database

### Caching & Storage
- **Redis Cache**: For session storage and Celery task queuing
- **Storage Account**: For static files and media uploads

### Security & Monitoring
- **Key Vault**: For secure storage of secrets and configuration
- **Application Insights**: For application monitoring and telemetry

## Prerequisites

1. **Azure CLI**: Install and authenticate with `az login`
2. **Azure Subscription**: Active subscription with sufficient permissions
3. **PowerShell**: For running deployment scripts (Windows/macOS/Linux)

## Deployment

### Quick Start

1. **Authenticate with Azure:**
   ```bash
   az login
   az account set --subscription "Your Subscription Name"
   ```

2. **Deploy infrastructure:**
   ```powershell
   .\deploy.ps1 -ResourceGroupName "precon-rg" -Location "East US" -Environment "dev" -AdminPassword (ConvertTo-SecureString "YourSecurePassword" -AsPlainText -Force)
   ```

3. **Deploy with applications:**
   ```powershell
   .\deploy.ps1 -ResourceGroupName "precon-rg" -Location "East US" -Environment "dev" -AdminPassword (ConvertTo-SecureString "YourSecurePassword" -AsPlainText -Force) -DeployBackend -DeployFrontend
   ```

### Manual Deployment

1. **Create resource group:**
   ```bash
   az group create --name precon-rg --location "East US"
   ```

2. **Deploy infrastructure:**
   ```bash
   az deployment group create \
     --resource-group precon-rg \
     --template-file main.bicep \
     --parameters environment=dev dbAdminPassword=YourSecurePassword
   ```

## Environment Variables

After deployment, configure these environment variables in Azure App Service:

### Backend (Django)
- `DJANGO_SECRET_KEY`
- `DEBUG` (set to False in production)
- `ALLOWED_HOSTS`
- `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_SSL`
- `AZURE_STORAGE_ACCOUNT`
- `AZURE_STORAGE_ACCESS_KEY`

### Frontend (React)
- `REACT_APP_API_BASE_URL`

## CI/CD Pipeline

The Azure DevOps pipeline (`azure-pipelines.yml`) provides:

1. **Build Stage**: Compiles and tests backend, frontend, and mobile applications
2. **Deploy Stage**: Deploys applications to Azure infrastructure
3. **Automated Testing**: Runs Django tests and validates builds

### Pipeline Setup

1. **Create Azure DevOps Project**
2. **Import Repository**: Connect your GitHub repository
3. **Create Pipeline**: Use the `azure-pipelines.yml` file
4. **Configure Variables**: Set required pipeline variables
5. **Run Pipeline**: Trigger manual or automatic builds

## Cost Optimization

### Development Environment
- Use `F1` (Free) tier for frontend
- Use `B1` (Basic) tier for backend
- Use `Basic` Redis cache tier

### Production Environment
- Scale up App Service Plans as needed
- Use `Standard` Redis cache tier
- Enable geo-redundancy for critical resources

## Security Considerations

1. **Network Security**: All resources use private endpoints where possible
2. **Authentication**: Key Vault with RBAC for secret management
3. **Encryption**: TLS 1.2+ enforced, encrypted storage
4. **Access Control**: Principle of least privilege applied

## Monitoring & Alerting

1. **Application Insights**: Built-in application monitoring
2. **Azure Monitor**: Infrastructure and performance monitoring
3. **Log Analytics**: Centralized logging and analysis
4. **Alerts**: Configure alerts for critical metrics

## Troubleshooting

### Common Issues

1. **Deployment Failures**: Check Azure CLI authentication and permissions
2. **Database Connection**: Verify firewall rules and connection strings
3. **App Service Issues**: Check application logs and configuration
4. **Pipeline Failures**: Validate build artifacts and deployment settings

### Support Resources

- [Azure Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Azure DevOps Documentation](https://docs.microsoft.com/en-us/azure/devops/)

## Next Steps

After successful deployment:

1. **Configure Domain Names**: Set up custom domains for production
2. **Set Up Monitoring**: Configure alerts and dashboards
3. **Implement Backup Strategy**: Regular database and file backups
4. **Security Hardening**: Additional security measures and compliance
5. **Performance Optimization**: Load testing and optimization
