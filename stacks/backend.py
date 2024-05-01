import aws_cdk as cdk

from components.static_website import StaticWebsite
from constructs import Construct

class BackendStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, *, stage_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        static_website = StaticWebsite(self, f"{stage_name}Website", stage_name=stage_name)

        self.cdn_output = cdk.CfnOutput(self, "CloudFrontUrl", value=f"http://{static_website.domain_name}")