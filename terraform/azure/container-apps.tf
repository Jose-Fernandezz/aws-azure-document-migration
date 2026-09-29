resource "azurerm_user_assigned_identity" "container_app" {
  name                = "id-aws-azure-doc-migration-app"
  location            = azurerm_resource_group.migration.location
  resource_group_name = azurerm_resource_group.migration.name

  tags = {
    Project     = var.project_name
    Environment = "migration-target"
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_role_assignment" "container_app_acr_pull" {
  scope                = azurerm_container_registry.migration.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.container_app.principal_id
}

resource "azurerm_log_analytics_workspace" "migration" {
  name                = "log-aws-azure-doc-migration-eastus2"
  location            = "eastus2"
  resource_group_name = azurerm_resource_group.migration.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = {
    Project     = var.project_name
    Environment = "migration-target"
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_container_app_environment" "migration" {
  name                       = "cae-aws-azure-doc-migration"
  location                   = "centralus"
  resource_group_name        = azurerm_resource_group.migration.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.migration.id

  tags = {
    Project     = var.project_name
    Environment = "migration-target"
    ManagedBy   = "Terraform"
  }

  lifecycle {
    ignore_changes = [
      infrastructure_subnet_id,
      workload_profile
    ]
  }
}

resource "azurerm_container_app" "migration" {
  name                         = "cae-aws-azure-doc-migration-app"
  container_app_environment_id = azurerm_container_app_environment.migration.id
  resource_group_name          = azurerm_resource_group.migration.name
  revision_mode                = "Single"

  identity {
    type = "UserAssigned"

    identity_ids = [
      azurerm_user_assigned_identity.container_app.id
    ]
  }

  registry {
    server   = azurerm_container_registry.migration.login_server
    identity = azurerm_user_assigned_identity.container_app.id
  }

  secret {
    name = "database-url"

    value = "postgresql://${azurerm_postgresql_flexible_server.migration.administrator_login}:${urlencode(random_password.postgres_admin.result)}@${azurerm_postgresql_flexible_server.migration.fqdn}:5432/${azurerm_postgresql_flexible_server_database.documents.name}?sslmode=require"
  }

  ingress {
    external_enabled = true
    target_port      = 5001

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "document-management-app"
      image  = "${azurerm_container_registry.migration.login_server}/aws-azure-document-migration-app:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "APP_ENV"
        value = "production"
      }

      env {
        name  = "STORAGE_PROVIDER"
        value = "azure"
      }

      env {
        name  = "AZURE_STORAGE_ACCOUNT"
        value = azurerm_storage_account.migration.name
      }

      env {
        name  = "AZURE_STORAGE_CONTAINER"
        value = azurerm_storage_container.documents.name
      }

      env {
        name        = "DATABASE_URL"
        secret_name = "database-url"
      }
    }
  }

  tags = {
    Project     = var.project_name
    Environment = "migration-target"
    ManagedBy   = "Terraform"
  }

  depends_on = [
    azurerm_role_assignment.container_app_acr_pull
  ]
}

resource "azurerm_role_assignment" "container_app_blob_access" {
  scope                = azurerm_storage_account.migration.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.container_app.principal_id
}