variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nombre corto del proyecto"
  type        = string
  default     = "worldbank-mr"
}

variable "environment" {
  description = "Etiqueta de entorno"
  type        = string
  default     = "dev"
}

variable "my_ip_cidr" {
  description = "Tu IP pública en formato CIDR para SSH (ej: 1.2.3.4/32)"
  type        = string
}

variable "ec2_key_name" {
  description = "Nombre del key pair de EC2 que ya tienes creado en AWS (para SSH)"
  type        = string
  default     = "EMR"
}

variable "emr_release_label" {
  description = "Versión de EMR"
  type        = string
  default     = "emr-6.15.0"
}

variable "emr_master_instance_type" {
  description = "Tipo de instancia del nodo master"
  type        = string
  default     = "m5.xlarge"
}

variable "emr_core_instance_type" {
  description = "Tipo de instancia de los nodos core"
  type        = string
  default     = "m5.xlarge"
}

variable "emr_core_instance_count" {
  description = "Número de nodos core"
  type        = number
  default     = 2
}

variable "emr_service_role_arn" {
  description = "ARN del rol de servicio EMR (por ejemplo, EMR_DefaultRole) ya existente en la cuenta"
  type        = string
}

variable "emr_ec2_instance_profile_arn" {
  description = "ARN del instance profile de EC2 para EMR (por ejemplo, EMR_EC2_DefaultRole) ya existente en la cuenta"
  type        = string
}
