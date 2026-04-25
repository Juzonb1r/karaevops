output "api_url" {
  description = "Paste this URL into ai-chat-widget.html as API_URL"
  value       = "${aws_apigatewayv2_stage.prod.invoke_url}/chat"
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.chat.function_name
}

output "lambda_log_group" {
  description = "CloudWatch log group for debugging"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}
