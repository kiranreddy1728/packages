https://github.com/terraform-aws-modules/terraform-aws-rds/tree/master/examples/complete-mysql

https://github.com/terraform-providers/terraform-provider-aws/tree/master/examples/rds

https://github.com/terraform-aws-modules/terraform-aws-rds



# Variables
variable "myregion" {
  default = "us-eat-1"
}

variable "accountId" {
  default = "223751785022"
}

# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = "myapi"
}

resource "aws_api_gateway_resource" "resource" {
  path_part   = "resource"
  parent_id   = "${aws_api_gateway_rest_api.api.root_resource_id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = "${aws_api_gateway_rest_api.api.id}"
  resource_id   = "${aws_api_gateway_resource.resource.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.api.id}"
  resource_id             = "${aws_api_gateway_resource.resource.id}"
  http_method             = "${aws_api_gateway_method.method.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.myregion}:lambda:path/2015-03-31/functions/${aws_lambda_function.lambda.arn}/invocations"
}

resource "aws_api_gateway_deployment" "Deployment" {
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  stage_name  = "test"
}

resource "aws_api_gateway_api_key" "ApiKey" {
  name = "demo"

  stage_key {
    rest_api_id = "${aws_api_gateway_rest_api.api.id}"
    stage_name  = "${aws_api_gateway_deployment.Deployment.stage_name}"
  }
}

resource "aws_api_gateway_usage_plan" "myusageplan" {
  name = "my_usage_plan"
}

resource "aws_api_gateway_usage_plan_key" "plan" {
  key_id        = "${aws_api_gateway_api_key.ApiKey.id}"
  key_type      = "API_KEY"
  usage_plan_id = "${aws_api_gateway_usage_plan.myusageplan.id}"
}

# Lambda
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda.arn}"
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.myregion}:${var.accountId}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.method.http_method}${aws_api_gateway_resource.resource.path}"
}

# Archive a single file.

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "C:/Users/KiranReddy/Desktop/ihub/lambda/script.py"
  output_path = "C:/Users/KiranReddy/Desktop/ihub/lambda.zip"
}

resource "aws_lambda_function" "lambda" {
  filename         = "lambda.zip"
  function_name    = "mylambda"
  role             = "${aws_iam_role.role.arn}"
  handler          = "script.lambda_handler"
  source_code_hash = "${base64sha256(file("{data.archive_file.lambda.output_path}"))}"
  #source_code_hash = "{base64sha256(file("{data.archive_file.lambda.output_path}"))}"
  runtime          = "python2.7"
  #publish = true
}

# IAM
resource "aws_iam_role" "role" {
  name = "myrole"

  assume_role_policy = <<POLICY
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
POLICY
}




