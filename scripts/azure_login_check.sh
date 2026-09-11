#!/bin/bash
set -e

echo "========================================"
echo " Azure Login & Environment Check"
echo "========================================"

echo ""
echo "1. Checking Azure CLI installation..."
az version --query '"azure-cli"' --output tsv

echo ""
echo "2. Checking active Azure subscription..."
az account show --query "{Name:name,State:state,IsDefault:isDefault}" --output table

echo ""
echo "3. Checking required resource providers..."
az provider show --namespace Microsoft.App --query "{Provider:namespace,Status:registrationState}" --output table
az provider show --namespace Microsoft.DBforPostgreSQL --query "{Provider:namespace,Status:registrationState}" --output table
az provider show --namespace Microsoft.ContainerRegistry --query "{Provider:namespace,Status:registrationState}" --output table
az provider show --namespace Microsoft.Storage --query "{Provider:namespace,Status:registrationState}" --output table
az provider show --namespace Microsoft.Network --query "{Provider:namespace,Status:registrationState}" --output table
az provider show --namespace Microsoft.OperationalInsights --query "{Provider:namespace,Status:registrationState}" --output table
az provider show --namespace Microsoft.ManagedIdentity --query "{Provider:namespace,Status:registrationState}" --output table

echo ""
echo "Azure environment check complete."