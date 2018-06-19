# Module to deploy Lambda function to import AWS tag to AlertLogic console
# only 1 function required per Alert Logic Customer ID (CID)

resource "aws_iam_role" "iam_for_lambda_alert_logic_import_tags_role" {
  name = "via-${var.account_name}-lambda-alert-logic-import-tags"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_alert_logic_import_tags_policy" {
  name = "via-${var.account_name}-lambda-alert-logic-import-tags-policy"
  policy = <<EOF
{
  "Statement": [
    {
      "Action": [
        "logs:*"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:logs:*:*:*",
      "Sid": "AllowLambdaImportTagsToWriteLogs"
    },
    {
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeRegions",
        "ec2:DescribeTags"
      ],
      "Effect": "Allow",
      "Resource": [
        "*"
      ],
      "Sid": "AllowLambdaImportTagsToAlertLogic"
    },
    {
      "Action": [
        "kms:Decrypt"
      ],
      "Effect": "Allow",
      "Resource": [
        "${aws_kms_key.alert_logic_import_tags_kms_key.arn}"
      ],
      "Sid": "AllowLambdaImportTagsToDecryptKey"
    }
  ],
  "Version": "2012-10-17"
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_alert_logic_import_tags_policy_attachment" {
  role = "${aws_iam_role.iam_for_lambda_alert_logic_import_tags_role.name}"
  policy_arn = "${aws_iam_policy.lambda_alert_logic_import_tags_policy.arn}"
  depends_on = ["aws_iam_role.iam_for_lambda_alert_logic_import_tags_role", "aws_iam_policy.lambda_alert_logic_import_tags_policy"]
}

resource "aws_cloudwatch_event_rule" "run_hourly" {
  name        = "${var.account_name}-run-hourly"
  description = "Invoke AWS Import Tag Lambda for AlertLogic"
  schedule_expression = "cron(0 * * * ? *)"
}

resource "aws_lambda_function" "alert_logic_import_tags" {
  function_name = "${var.account_name}-lambda-alert-logic-import-tags"
  description = "Alert Logic Import Tags Lambda to ensure ec2 instances are tagged properly in Alert Logic"
  s3_bucket = "${var.alert_logic_lambda_source_bucket_prefix}.${var.region}"
  s3_key = "${var.alert_logic_lambda_source_object_key}"
  runtime = "python2.7"
  timeout = "300"
  memory_size = "512"
  handler = "import_tags.lambda_handler"
  role = "${aws_iam_role.iam_for_lambda_alert_logic_import_tags_role.arn}"
  environment {
    variables = {
      API_KEY = "${data.aws_kms_ciphertext.defender_api_key.ciphertext_blob}"
      CID = "${var.alert_logic_cid}"
      DC = "${var.alert_logic_dc}"
      REPLACE = "${var.alert_logic_replace_tag}"
    }
  }
  depends_on = ["aws_iam_role.iam_for_lambda_alert_logic_import_tags_role"]
}

resource "aws_cloudwatch_event_target" "lambda_alert_logic_import_tags_target" {
  target_id = "${var.account_name}-lambda-alert-logic-import-tags-target"
  rule      = "${aws_cloudwatch_event_rule.run_hourly.name}"
  arn       = "${aws_lambda_function.alert_logic_import_tags.arn}"
  depends_on = ["aws_cloudwatch_event_rule.run_hourly", "aws_lambda_function.alert_logic_import_tags"]
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id   = "AllowExecutionFromCloudWatch"
  action         = "lambda:InvokeFunction"
  function_name  = "${aws_lambda_function.alert_logic_import_tags.function_name}"
  principal      = "events.amazonaws.com"
  source_arn     = "${aws_cloudwatch_event_rule.run_hourly.arn}"
  depends_on = ["aws_cloudwatch_event_rule.run_hourly", "aws_lambda_function.alert_logic_import_tags"]
}

resource "aws_sns_topic" "alert_logic_import_tags_alarm" {
  name = "${var.account_name}-lambda-alert-logic-import-tags-alarm"
}

resource "aws_cloudwatch_metric_alarm" "alert_logic_import_tags_error" {
  alarm_name                = "${var.account_name}-lambda-alert-logic-import-tags-error"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  metric_name               = "Errors"
  namespace                 = "AWS/Lambda"
  dimensions {
    FunctionName = "${aws_lambda_function.alert_logic_import_tags.function_name}"
    Resource = "${aws_lambda_function.alert_logic_import_tags.function_name}"
  }
  period                    = "3600"
  statistic                 = "Sum"
  threshold                 = "1"
  alarm_description         = "Monitor error rate of lambda function"
  alarm_actions             = ["${aws_sns_topic.alert_logic_import_tags_alarm.arn}"]
  insufficient_data_actions = []
}

resource "aws_kms_key" "alert_logic_import_tags_kms_key" {
  description             = "${var.account_name}-lambda-alert-logic-import-tags-kms-key"
  deletion_window_in_days = 14
}

data "aws_kms_ciphertext" "defender_api_key" {
  key_id = "${aws_kms_key.alert_logic_import_tags_kms_key.key_id}"
  plaintext = "${var.alert_logic_api_key}"
}
