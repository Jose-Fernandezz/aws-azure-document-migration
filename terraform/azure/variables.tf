variable "location" {
  description = "Azure region used for the migration destination resources."
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Name of the Azure resource group for the migration destination."
  type        = string
  default     = "rg-aws-azure-document-migration"
}

variable "project_name" {
  description = "Common project name used when naming Azure resources."
  type        = string
  default     = "aws-azure-document-migration"
}