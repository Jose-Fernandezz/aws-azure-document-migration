variable "project_name" {
  description = "Name used to identify resources created for this project"
  type        = string
  default     = "aws-azure-document-migration"
}

variable "aws_region" {
  description = "AWS region where the source infrastructure will be deployed"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the AWS source VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_1_cidr" {
  description = "CIDR block for the first private subnet"
  type        = string
  default     = "10.0.10.0/24"
}

variable "private_subnet_2_cidr" {
  description = "CIDR block for the second private subnet"
  type        = string
  default     = "10.0.20.0/24"
}



variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "document_management"
}

variable "db_username" {
  description = "Master username for the PostgreSQL database"
  type        = string
  default     = "dbadmin"
}

variable "db_instance_class" {
  description = "AWS RDS instance class used for the PostgreSQL database"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Storage allocated to the PostgreSQL database in GB"
  type        = number
  default     = 20
}


variable "container_port" {
  description = "Port exposed by the Flask application container"
  type        = number
  default     = 5001
}

variable "ecs_cpu" {
  description = "CPU units allocated to the ECS Fargate task"
  type        = number
  default     = 256
}

variable "ecs_memory" {
  description = "Memory in MiB allocated to the ECS Fargate task"
  type        = number
  default     = 512
}


variable "db_password" {
  description = "Master password for the PostgreSQL database"
  type        = string
  sensitive   = true
}