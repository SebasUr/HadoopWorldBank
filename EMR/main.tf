########################
# Configuración básica
########################
terraform {
  required_version = ">= 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

########################
# RED DE VPC + SUBNET
########################

# VPC dedicada para el cluster EMR
resource "aws_vpc" "emr_vpc" {
  cidr_block           = "10.10.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "emr_igw" {
  vpc_id = aws_vpc.emr_vpc.id

  tags = {
    Name        = "${var.project_name}-igw"
    Environment = var.environment
  }
}

# Subnet pública para el cluster
resource "aws_subnet" "emr_subnet" {
  vpc_id                  = aws_vpc.emr_vpc.id
  cidr_block              = "10.10.1.0/24"
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.project_name}-subnet"
    Environment = var.environment
  }
}

# Route table con salida a internet
resource "aws_route_table" "emr_rt" {
  vpc_id = aws_vpc.emr_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.emr_igw.id
  }

  tags = {
    Name        = "${var.project_name}-rt"
    Environment = var.environment
  }
}

# Asociación de la subnet con la route table
resource "aws_route_table_association" "emr_rta" {
  subnet_id      = aws_subnet.emr_subnet.id
  route_table_id = aws_route_table.emr_rt.id
}

########################
# SECURITY GROUP
########################

resource "aws_security_group" "emr_sg" {
  name        = "${var.project_name}-emr-sg"
  description = "Security group for EMR cluster (HDFS only)"
  vpc_id      = aws_vpc.emr_vpc.id

  # SSH desde tu IP
  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  # Todo el tráfico dentro del mismo SG (entre nodos EMR)
  ingress {
    description = "All traffic inside SG"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    self        = true
  }

  # Salida a internet
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-emr-sg"
    Environment = var.environment
  }
}

########################
# IAM ROLES PARA EMR (YA EXISTENTES)
########################

# Nota: No creamos roles nuevos. Usamos los roles por defecto ya
# existentes en la cuenta (EMR_DefaultRole y EMR_EC2_DefaultRole)
# pasados por variables.

########################
# CLUSTER EMR (HDFS + MR)
########################

resource "aws_emr_cluster" "this" {
  name          = "${var.project_name}-emr-cluster"
  release_label = var.emr_release_label

  # Solo Hadoop → HDFS + MapReduce
  applications = ["Hadoop"]

  # Usamos el rol de servicio EMR existente (por ejemplo, EMR_DefaultRole)
  service_role = var.emr_service_role_arn

  ec2_attributes {
    # Usamos el instance profile de EC2 para EMR ya existente
    # (por ejemplo, asociado a EMR_EC2_DefaultRole)
    instance_profile = var.emr_ec2_instance_profile_arn
    subnet_id        = aws_subnet.emr_subnet.id

    emr_managed_master_security_group = aws_security_group.emr_sg.id
    emr_managed_slave_security_group  = aws_security_group.emr_sg.id

    # Clave SSH existente en tu cuenta de AWS para entrar al master
    key_name = var.ec2_key_name
  }

  master_instance_group {
    name           = "master"
    instance_type  = var.emr_master_instance_type
    instance_count = 1
  }

  core_instance_group {
    name           = "core"
    instance_type  = var.emr_core_instance_type
    instance_count = var.emr_core_instance_count
  }

  keep_job_flow_alive_when_no_steps = true
  termination_protection            = false
  
  tags = {
    Name        = "${var.project_name}-emr-cluster"
    Environment = var.environment
  }
}

########################
# OUTPUTS
########################

output "emr_cluster_id" {
  value       = aws_emr_cluster.this.id
  description = "ID del cluster EMR"
}

output "emr_master_public_dns" {
  value       = aws_emr_cluster.this.master_public_dns
  description = "DNS público del nodo master (para SSH)"
}

output "vpc_id" {
  value       = aws_vpc.emr_vpc.id
  description = "VPC creada para el cluster"
}

output "subnet_id" {
  value       = aws_subnet.emr_subnet.id
  description = "Subnet pública donde vive el cluster"
}
