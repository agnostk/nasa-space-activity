resource "aws_cloudwatch_event_rule" "glue_job_failure_rule" {
  name        = "${local.name-prefix}-glue-failure-rule"
  description = "Triggers on AWS Glue job failures"
  event_pattern = jsonencode({
    "source" : ["aws.glue"],
    "detail-type" : ["Glue Job State Change"],
    "detail" : {
      "state" : ["FAILED"]
    }
  })
}

resource "aws_cloudwatch_event_target" "send_to_sns" {
  rule      = aws_cloudwatch_event_rule.glue_job_failure_rule.name
  target_id = "SendGlueFailureNotification"
  arn       = aws_sns_topic.glue_failure_notifications.arn
}
