output "container_registry_login_server" {
  description = "Login server for the Azure Container Registry"
  value       = azurerm_container_registry.migration.login_server
}

output "postgresql_fqdn" {
  description = "Fully qualified domain name of the Azure PostgreSQL server"
  value       = azurerm_postgresql_flexible_server.migration.fqdn
}

output "postgresql_database_name" {
  description = "Name of the Azure PostgreSQL database"
  value       = azurerm_postgresql_flexible_server_database.documents.name
}

output "storage_account_name" {
  description = "Name of the Azure Storage Account"
  value       = azurerm_storage_account.migration.name
}

output "storage_container_name" {
  description = "Name of the Azure Blob Storage container"
  value       = azurerm_storage_container.documents.name
}

output "container_app_fqdn" {
  description = "Public FQDN of the Azure Container App"
  value       = azurerm_container_app.migration.latest_revision_fqdn
}