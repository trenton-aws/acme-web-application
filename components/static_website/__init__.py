import constants
import pathlib
import aws_cdk as cdk

from aws_cdk import (
    aws_s3 as _s3,
    aws_s3_deployment as _deployment,
    aws_iam as _iam,
    aws_cloudfront as _cfnt,
    aws_apigatewayv2 as _httpgw
)
from constructs import Construct

class StaticWebsite(Construct):

    def __init__(self, scope: Construct, id: str, stage_name: str) -> None:
        super().__init__(scope, id)

        if stage_name == constants.QA_ENV_NAME:
            behavior = _cfnt.Behavior(
                is_default_behavior=True,
                default_ttl=cdk.Duration.seconds(0),
                compress=True
            )
            logging_config = None

        elif stage_name == constants.PROD_ENV_NAME:
            behavior = _cfnt.Behavior(
                is_default_behavior=True,
                min_ttl=cdk.Duration.minutes(10),
                max_ttl=cdk.Duration.minutes(20),
                default_ttl=cdk.Duration.minutes(10),
                compress=True
            )
            logging_config = _cfnt.LoggingConfiguration(
                bucket=_s3.Bucket(
                    self,
                    "LoggingBucket",
                    removal_policy=cdk.RemovalPolicy.DESTROY,
                    versioned=True,
                    object_ownership=_s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
                    auto_delete_objects=True
                ),
                include_cookies=True
            )

        bucket = _s3.Bucket(
            self,
            "WebsiteBucket",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        origin = _cfnt.OriginAccessIdentity(
            self,
            "BucketOrigin",
            comment=f"Origin associated with ACME website static content Bucket, in the '{stage_name}' pipeline stage."
        )

        bucket.grant_read(
            _iam.CanonicalUserPrincipal(
                origin.cloud_front_origin_access_identity_s3_canonical_user_id
            )
        )

        self.cdn = _cfnt.CloudFrontWebDistribution(
            self,
            "CloudFrontCDN",
            comment=f"CDN for the ACME Website, in the '{stage_name}' pipeline stage.",
            origin_configs=[
                _cfnt.SourceConfiguration(
                    s3_origin_source=_cfnt.S3OriginConfig(
                        s3_bucket_source=bucket,
                        origin_access_identity=origin
                    ),
                    behaviors=[behavior]
                )
            ],
            default_root_object="index.html",
            enable_ip_v6=True,
            http_version=_cfnt.HttpVersion.HTTP2,
            logging_config=logging_config,
            price_class=_cfnt.PriceClass.PRICE_CLASS_100,
            viewer_protocol_policy=_cfnt.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
        )
        
        _deployment.BucketDeployment(
            self,
            "WebsiteDeployment",
            sources=[
                _deployment.Source.asset(
                    path=str(pathlib.Path(__file__).parent.joinpath("www").resolve())
                )
            ],
            destination_bucket=bucket,
            distribution=self.cdn,
            retain_on_delete=False
        )
    
    @property
    def domain_name(self):
        return self.cdn.distribution_domain_name