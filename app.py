#!/usr/bin/env python3
import constants
import aws_cdk as cdk

from toolchain import ToolChainStack

app = cdk.App()
ToolChainStack(
    app,
    constants.GITHUB_REPOSITORY,
    env=cdk.Environment(
        account=constants.ACCOUNT,
        region=constants.REGION
    ),
    github_user=constants.GITHUB_USER,
    github_repo=constants.GITHUB_REPOSITORY,
    connection_arn=constants.CONNECTION_ARN,
    cdk_version=constants.CDK_VERSION
)
app.synth()
