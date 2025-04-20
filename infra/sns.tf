resource "aws_sns_topic" "glue_failure_notifications" {
  name = "${local.name-prefix}-glue-failure-topic"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.glue_failure_notifications.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
