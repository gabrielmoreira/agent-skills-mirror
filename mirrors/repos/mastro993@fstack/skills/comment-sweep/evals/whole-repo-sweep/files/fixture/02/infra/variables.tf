# The region
variable "region" {
  type    = string
  default = "eu-west-1"
}

variable "env" {
  type        = string
  description = "Deployment environment: staging or production."

  validation {
    condition     = contains(["staging", "production"], var.env)
    error_message = "env must be staging or production."
  }
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "report_retention_days" {
  type    = number
  default = 400
}

# tflint-ignore: terraform_unused_declarations
variable "legacy_vpc_id" {
  type        = string
  default     = ""
  description = "Read by the network module in the platform repo; unused here."
}
