#!/usr/bin/env python3

#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0


import os
from aws_cdk import core

from lex_sf_drug_reminder_blog.lex_sf_drug_reminder_stack import LexSFDCDrugReminderStack

params = {
    "connectInstanceID": os.getenv("CONNECT_INSTANCE_ID"),
    "project_prefix": os.getenv("PROJECT_PREFIX"),
    "time_zone": os.getenv("TIME_ZONE"),
    "sfdc_consumer_key": os.getenv("CONSUMER_KEY"),
    "sfdc_consumer_secret": os.getenv("CONSUMER_SECRET"),
    "sfdc_user_name": os.getenv("USER_NAME"),
    "sfdc_user_password": os.getenv("PASSWORD"),
    "sfdc_user_security_token": os.getenv("SECURITY_TOKEN"),
    "sfdc_endpoint": os.getenv("ENDPOINT")
}

app = core.App()

LexSFDCDrugReminderStack(app, "lex-sfdc-drug-reminder-blog", params=params)


app.synth()
