import constants
import aws_cdk as cdk

from aws_cdk import (
    aws_s3 as _s3,
    pipelines as _pipelines,
    aws_ssm as _ssm,
    aws_iam as _iam
)
from stacks.backend import BackendStack
from constructs import Construct


class ToolChainStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, *, github_user: str=None, github_repo: str=None, connection_arn: str=None, cdk_version: str=None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_artifact = _pipelines.CodePipelineSource.connection(
            repo_string=f"{github_user}/{github_repo}",
            branch="main",
            connection_arn=connection_arn
        )

        pipeline = _pipelines.CodePipeline(
            self,
            "Application-Pipeline",
            pipeline_name="ACME-WebApp-Pipeline",
            self_mutation=True,
            cli_version=cdk_version,
            synth=_pipelines.CodeBuildStep(
                "Synth",
                input=source_artifact,
                role=_iam.Role(
                    self,
                    "Synth-Role",
                    assumed_by=_iam.CompositePrincipal(
                        _iam.ServicePrincipal("codebuild.amazonaws.com"),
                        _iam.ServicePrincipal("sagemaker.amazonaws.com")
                    ),
                    managed_policies=[
                        _iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
                    ]
                ),
                install_commands=[
                    "printenv",
                    f"npm install -g aws-cdk@{cdk_version}",
                    "python -m pip install --upgrade pip",
                    "pip install -r requirements.txt",
                ],
                commands=[
                    "cdk synth"
                ]
            )
        )

        ToolChainStack._add_stage(
            pipeline=pipeline,
            stage_name=constants.QA_ENV_NAME,
            stage_account=cdk.Aws.ACCOUNT_ID,
            stage_region=cdk.Aws.REGION
        )

        ToolChainStack._add_stage(
            pipeline=pipeline,
            stage_name=constants.PROD_ENV_NAME,
            stage_account=cdk.Aws.ACCOUNT_ID,
            stage_region=cdk.Aws.REGION
        )


    @staticmethod
    def _add_stage(pipeline: _pipelines.CodePipeline, stage_name: str, stage_account: str, stage_region: str) -> None:
        stage = cdk.Stage(pipeline, stage_name, env=cdk.Environment(
            account=stage_account,
            region=stage_region
            )
        )

        if stage_name == constants.QA_ENV_NAME:
            stack = BackendStack(
                stage,
                "TestBackendStack",
                stage_name=stage_name
            )
            pipeline.add_stage(
                stage,
                post=[
                    _pipelines.ShellStep(
                        "System-Tests",
                        commands=[
                            "pip install -r ./tests/requirements.txt",
                            "pytest ./tests/system_tests.py"
                        ],
                        env_from_cfn_outputs={
                            "WEBSITE_URL": stack.cdn_output
                        }
                    )
                ]
            )
        elif stage_name == constants.PROD_ENV_NAME:
            BackendStack(
                stage,
                "ProdBackendStack",
                stage_name=stage_name
            )
            pipeline.add_stage(stage)
