variable "account_name" {}
variable "region" {}
variable "alert_logic_api_key" {}
variable "alert_logic_cid" {}
variable "alert_logic_dc" {}
variable "alert_logic_replace_tag" {
  default = "True"
}
variable "alert_logic_lambda_source_bucket_prefix" {
  default = "al-deployment-services"
}
variable "alert_logic_lambda_source_object_key" {
  default = "lambda_packages/al_aws_tag_import.zip"
}
