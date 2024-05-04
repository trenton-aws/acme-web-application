import boto3

ACCOUNT = boto3.client("sts").get_caller_identity()["Account"]
REGION = ""
GITHUB_USER = ""
GITHUB_REPOSITORY = ""
CONNECTION_ARN = ""
CDK_VERSION = "2.140.0"
QA_ENV_NAME = "Test-Deployment"
PROD_ENV_NAME = "Production-Deployment"