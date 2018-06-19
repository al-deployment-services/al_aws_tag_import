provider "aws" {
   region = "${var.region}"
   profile = "${var.profile}"
   shared_credentials_file = "~/.aws/credentials"
}

#
# Module for Importing AWS tags to Alert Logic Console
# only 1 resource requried per Alert Logic Customer id (CID)
#
module "al_import_tags" {
  source = "./import_tags"
  region = "${var.region}"
  account_name = "${var.account_name}"
  alert_logic_api_key = "${var.alert_logic_api_key}"
  alert_logic_cid = "${var.alert_logic_cid}"
  alert_logic_dc = "${var.alert_logic_dc}"
  alert_logic_replace_tag = "${var.alert_logic_replace_tag}"
  alert_logic_lambda_source_bucket_prefix = "${var.alert_logic_lambda_source_bucket_prefix}"
  alert_logic_lambda_source_object_key = "${var.alert_logic_lambda_source_object_key}"
}
