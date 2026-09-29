resource "random_password" "postgres_admin" {
  length  = 24
  special = true
}

resource "azurerm_private_dns_zone" "postgresql" {
  name                = "aws-azure-migration.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.migration.name

  tags = {
    Project     = var.project_name
    Environment = "migration-target"
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgresql" {
  name                  = "postgresql-vnet-link"
  private_dns_zone_name = azurerm_private_dns_zone.postgresql.name
  virtual_network_id    = azurerm_virtual_network.migration.id
  resource_group_name   = azurerm_resource_group.migration.name

  depends_on = [
    azurerm_virtual_network.migration
  ]
}

resource "azurerm_postgresql_flexible_server" "migration" {
  name                = "psql-aws-azure-doc-migration"
  resource_group_name = azurerm_resource_group.migration.name
  location            = azurerm_resource_group.migration.location
  version             = "15"

  public_network_access_enabled = false

  delegated_subnet_id = azurerm_subnet.postgresql.id
  private_dns_zone_id = azurerm_private_dns_zone.postgresql.id

  administrator_login    = "migrationadmin"
  administrator_password = random_password.postgres_admin.result

  zone       = "1"
  storage_mb = 32768
  sku_name   = "B_Standard_B1ms"

  depends_on = [
    azurerm_subnet.postgresql,
    azurerm_private_dns_zone_virtual_network_link.postgresql
  ]

  tags = {
    Project     = var.project_name
    Environment = "migration-target"
    ManagedBy   = "Terraform"
  }
}

resource "azurerm_postgresql_flexible_server_database" "documents" {
  name      = "document_metadata"
  server_id = azurerm_postgresql_flexible_server.migration.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}