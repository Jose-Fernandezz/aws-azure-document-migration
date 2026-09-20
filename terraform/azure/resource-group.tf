resource "azurerm_resource_group" "migration" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Project     = var.project_name
    Environment = "migration-target"
    ManagedBy   = "Terraform"
  }
}