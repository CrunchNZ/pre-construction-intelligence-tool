#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Deploy Pre-Construction Intelligence Tool to Azure

.DESCRIPTION
    This script deploys the Pre-Construction Intelligence Tool infrastructure to Azure
    using Azure Bicep templates and Azure CLI.

.PARAMETER ResourceGroupName
    Name of the resource group to create or use

.PARAMETER Location
    Azure region for deployment

.PARAMETER Environment
    Environment name (dev, staging, prod)

.PARAMETER AdminPassword
    PostgreSQL admin password

.PARAMETER DeployBackend
    Deploy Django backend application

.PARAMETER DeployFrontend
    Deploy React frontend application

.EXAMPLE
    .\deploy.ps1 -ResourceGroupName "precon-rg" -Location "East US" -Environment "dev" -AdminPassword "SecurePassword123!"

.NOTES
    Requires Azure CLI to be installed and authenticated
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [string]$Location,
    
    [Parameter(Mandatory = $true)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment,
    
    [Parameter(Mandatory = $true)]
    [SecureString]$AdminPassword,
    
    [switch]$DeployBackend,
    
    [switch]$DeployFrontend
)

# Convert secure string to plain text for Bicep
$AdminPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($AdminPassword))

Write-Host "Starting deployment of Pre-Construction Intelligence Tool..." -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Yellow
Write-Host "Location: $Location" -ForegroundColor Yellow
Write-Host "Environment: $Environment" -ForegroundColor Yellow

# Check if Azure CLI is installed and authenticated
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "Azure CLI version: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Error "Azure CLI is not installed or not accessible. Please install Azure CLI first."
    exit 1
}

# Check if user is logged in
$account = az account show --output json | ConvertFrom-Json
if (-not $account) {
    Write-Error "Not logged in to Azure. Please run 'az login' first."
    exit 1
}

Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green

# Create resource group if it doesn't exist
Write-Host "Creating/updating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location --output none

# Deploy infrastructure using Bicep
Write-Host "Deploying infrastructure..." -ForegroundColor Yellow
$deploymentName = "precon-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

$deployment = az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file "main.bicep" `
    --name $deploymentName `
    --parameters environment=$Environment dbAdminPassword=$AdminPasswordPlain `
    --output json | ConvertFrom-Json

if ($deployment.provisioningState -eq "Succeeded") {
    Write-Host "Infrastructure deployment successful!" -ForegroundColor Green
    
    # Output deployment results
    Write-Host "`nDeployment Outputs:" -ForegroundColor Cyan
    Write-Host "Backend URL: $($deployment.properties.outputs.backendUrl.value)" -ForegroundColor White
    Write-Host "Frontend URL: $($deployment.properties.outputs.frontendUrl.value)" -ForegroundColor White
    Write-Host "Database Server: $($deployment.properties.outputs.databaseServer.value)" -ForegroundColor White
    Write-Host "Redis Host: $($deployment.properties.outputs.redisHost.value)" -ForegroundColor White
    Write-Host "Key Vault URI: $($deployment.properties.outputs.keyVaultUri.value)" -ForegroundColor White
    Write-Host "Storage Account: $($deployment.properties.outputs.storageAccountName.value)" -ForegroundColor White
    Write-Host "App Insights Key: $($deployment.properties.outputs.appInsightsKey.value)" -ForegroundColor White
} else {
    Write-Error "Infrastructure deployment failed with state: $($deployment.provisioningState)"
    exit 1
}

# Deploy backend application if requested
if ($DeployBackend) {
    Write-Host "`nDeploying Django backend..." -ForegroundColor Yellow
    
    # Build and deploy backend
    Set-Location "../backend"
    
    # Create deployment package
    if (Test-Path "deploy") { Remove-Item "deploy" -Recurse -Force }
    New-Item -ItemType Directory -Name "deploy" | Out-Null
    
    # Copy necessary files
    Copy-Item "*.py" -Destination "deploy/" -Recurse
    Copy-Item "requirements.txt" -Destination "deploy/"
    Copy-Item "manage.py" -Destination "deploy/"
    Copy-Item "core" -Destination "deploy/" -Recurse
    Copy-Item "integrations" -Destination "deploy/" -Recurse
    Copy-Item "ai_models" -Destination "deploy/" -Recurse
    Copy-Item "analytics" -Destination "deploy/" -Recurse
    Copy-Item "preconstruction_intelligence" -Destination "deploy/" -Recurse
    
    # Create startup command file
    @"
cd /home/site/wwwroot
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind=0.0.0.0 --timeout 600 preconstruction_intelligence.wsgi
"@ | Out-File -FilePath "deploy/startup.sh" -Encoding UTF8
    
    # Deploy to Azure Web App
    $backendAppName = $deployment.properties.outputs.backendUrl.value.Split('.')[0].Split('//')[1]
    az webapp deployment source config-zip --resource-group $ResourceGroupName --name $backendAppName --src "deploy.zip"
    
    Write-Host "Backend deployment completed!" -ForegroundColor Green
    Set-Location "../azure"
}

# Deploy frontend application if requested
if ($DeployFrontend) {
    Write-Host "`nDeploying React frontend..." -ForegroundColor Yellow
    
    # Build frontend
    Set-Location "../frontend"
    npm run build
    
    # Deploy to Azure Static Web App or Web App
    $frontendAppName = $deployment.properties.outputs.frontendUrl.value.Split('.')[0].Split('//')[1]
    
    # For now, deploy as regular web app (can be changed to Static Web App)
    az webapp deployment source config-zip --resource-group $ResourceGroupName --name $frontendAppName --src "build.zip"
    
    Write-Host "Frontend deployment completed!" -ForegroundColor Green
    Set-Location "../azure"
}

Write-Host "`nDeployment completed successfully!" -ForegroundColor Green
Write-Host "Your Pre-Construction Intelligence Tool is now running on Azure!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Configure environment variables in Azure App Service" -ForegroundColor White
Write-Host "2. Set up custom domain names if needed" -ForegroundColor White
Write-Host "3. Configure monitoring and alerting" -ForegroundColor White
Write-Host "4. Set up CI/CD pipeline with Azure DevOps" -ForegroundColor White
