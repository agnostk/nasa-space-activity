resource "aws_sns_topic_policy" "sns_policy" {
  arn    = aws_sns_topic.glue_failure_notifications.arn

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "events.amazonaws.com"
        },
        Action = "sns:Publish",
        Resource = aws_sns_topic.glue_failure_notifications.arn
      }
    ]
  })
}
