resource "azurerm_storage_account" "migration" {
  name                     = "stawsazuredocmigration"
  resource_group_name      = azurerm_resource_group.migration.name
  location                 = azurerm_resource_group.migration.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false

  tags = {
    Project     = var.project_name
    Environment = "migration-target"
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_storage_container" "documents" {
  name                  = "documents"
  storage_account_id    = azurerm_storage_account.migration.id
  container_access_type = "private"
}