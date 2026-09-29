resource "azurerm_container_registry" "migration" {
  name                = "acrawsazuredocmigration"
  resource_group_name = azurerm_resource_group.migration.name
  location            = azurerm_resource_group.migration.location
  sku                 = "Basic"
  admin_enabled       = false

  tags = {
    Project     = var.project_name
    Environment = "migration-target"
    ManagedBy   = "Terraform"
  }
}