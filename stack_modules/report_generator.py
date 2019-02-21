from troposphere import Ref, Parameter, If, Equals, Condition, GetAtt
from stack_modules.common_modules.common import Stack, StackConfig
from stack_modules.common_modules.helpers import NestedDict, dictConvert
import json

def generator(stack=None):
    if not stack:
        print "This module requires a config file and doesn't have a default"
        exit(1)
    stack.description('Template for Reporting Stack')
    stack.capabilities = ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
    reporting_params = {
        "env": Parameter(
            "DeploymentEnvironment",
            Type="String",
            Default="DEV",
            Description="Environment you are building",
        ),
        "lambda_version": Parameter(
            "LambdaVersion",
            Type="String",
            Default="",
            Description="Version of your Lambda function. Optional"
        )
    }

    for p in reporting_params.values():
        stack.template.add_parameter(p)
    
    # need this condition for lambda. Basically if not set, deploy latest. But allows for a parameter to change later. 
    stack.template.add_condition("Version", Equals("", Ref("LambdaVersion")))
    
    # need all the stuff below for roles for lambda. 
    assume_role = dictConvert(NestedDict(stack.config).get("iam_role/assume_role_policy"))
    assume_role['Statement'][0]['Principal']['Service'].append(NestedDict(stack.config).get("iam_role/service_type"))

    custom_policy = stack.iam_policy_adder("SalesReportingPolicy", dictConvert(NestedDict(stack.config).get("iam_role/policies/custom")))
    iam_role = stack.iam_adder("SalesReportingRole", NestedDict(stack.config).get("iam_role/policies/managed"), assume_role)
    iam_role.ManagedPolicyArns.append(Ref(custom_policy))
    iam_role.DependsOn = "SalesReportingPolicy"
    stack.lambda_adder("AthenaReporting", "SalesReportingRole", "Version", **stack.config['lambda'])
    stack.lambda_policy_adder(NestedDict(stack.config).get("lambda/name"), "logs.amazonaws.com")

    #cloudtrail/cloudwatch stuff below. Won't be necessary for plain ol' lambda stuff. Probably makes sense to put it in a decorator
    #gonna keep it ugly for now.
    metrics_filter = (NestedDict(stack.config).get("cloudwatch/metric_filter") % "*SalesReportingRole*").rstrip()
    log_group = stack.cloudwatch_log_adder("CloudTrailAthena", metrics_filter, "AthenaReporting")
    log_group.DependsOn = "AthenaReporting"
    ct_assume_role = dictConvert(NestedDict(stack.config).get("cloud_trail_iam_role/assume_role_policy"))
    ct_assume_role['Statement'][0]['Principal']['Service'].append(NestedDict(stack.config).get("cloud_trail_iam_role/service_type"))
    ct_iam_role = stack.iam_adder("CloudTrailRole", NestedDict(stack.config).get("cloud_trail_iam_role/policies/managed"), ct_assume_role)
    stack.s3_policy_adder("S3Policy", stack.config['log_bucket'], dictConvert(NestedDict(stack.config).get("log_bucket_policy")))
    cloudtrail = stack.cloudtrail_adder("CloudTrailCloudWatch", stack.config['log_bucket'], GetAtt(log_group, "Arn"), GetAtt(ct_iam_role, "Arn"))
    cloudtrail.DependsOn = "CloudTrailAthena"



if __name__ == '__main__':
    stackconfig = StackConfig()
    stackconfig.loadlocalconfig("reporting.yml")
    mystack = Stack(stackconfig)
    mystack.description('Template for Quicksight Reporting Stack')
    generator(mystack)
