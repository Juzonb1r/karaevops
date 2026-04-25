variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "karaevops-chat"
}

variable "domain_name" {
  description = "Your portfolio domain for CORS"
  type        = string
  default     = "karaevops.com"
}

variable "anthropic_api_key" {
  description = "Anthropic API key — never hardcode, pass via TF_VAR or tfvars"
  type        = string
  sensitive   = true
}
