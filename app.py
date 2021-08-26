#!/usr/bin/env python3

#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import os

from aws_cdk import core

from lex_sf_drug_reminder_blog.lex_sf_drug_reminder_stack import LexSFDCDrugReminderStack

# from iot_resources import IoTStack


app = core.App()
# stack_env = core.Environment(account=os.environ['STACK_REGION'],
#                              region=os.environ['STACK_ACCOUNT'])  # os.environ['STACK_REGION'] and "STACK_ACCOUNT"

# david please make a note of CDK deployment parameters below in LexSFDCDrugReminderStack

# project_prefix = core.CfnParameter(self,"projectPrefix", type="String",default='dev',
#            description="prefix for all the resources in the project")
#
# time_zone = core.CfnParameter(self,"timeZone", type="String",default='EST',
#            description="timezone to be used for the entire project")

LexSFDCDrugReminderStack(app, "lex-sfdc-drug-reminder-blog")
# IoTStack(app, "iot-resources")

app.synth()
