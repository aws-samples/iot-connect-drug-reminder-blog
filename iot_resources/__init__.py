#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import os

from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_iam as iam,
    aws_iot as iot
)


class IoTStack(core.Construct):
    def __init__(self, scope: core.Construct, id: str, project_prefix_obj, time_zone_obj, dynamoTable_obj, **kwargs):
        super().__init__(scope, id, **kwargs)

        prefix_project_string = project_prefix_obj + "-"
        time_zone_string = time_zone_obj

        update_dynamo_table_lambda = _lambda.Function(self, "IoTUpdatePatientTable",
                                                      runtime=_lambda.Runtime.PYTHON_3_8,
                                                      handler="lambda_function.lambda_handler",
                                                      function_name=prefix_project_string + 'iot-update-patient-table',
                                                      environment={"TableName": dynamoTable_obj.table_name,
                                                      "time_zone": time_zone_string},
                                                      timeout=core.Duration.minutes(2),
                                                      code=_lambda.Code.asset('iot_resources/_lambda')
                                                      )

        # grant permission to dynamodb
        dynamoTable_obj.grant_read_write_data(update_dynamo_table_lambda)
        # Creating the IoT Topic
        iot_topic_sub_rule_action_property = iot.CfnTopicRule.LambdaActionProperty(
            function_arn=update_dynamo_table_lambda.function_arn)
        iot_topic_sub_rule_action = iot.CfnTopicRule.ActionProperty(lambda_=iot_topic_sub_rule_action_property)
        iot_topic_sub_rule_payload = iot.CfnTopicRule.TopicRulePayloadProperty(actions=[iot_topic_sub_rule_action],
                                                                               sql="SELECT * FROM 'esp32/pub'",
                                                                               error_action=iot_topic_sub_rule_action,
                                                                               rule_disabled=False,aws_iot_sql_version='2016-03-23')
        iot_topic_sub = iot.CfnTopicRule(self, 'iotTopic', topic_rule_payload=iot_topic_sub_rule_payload)
