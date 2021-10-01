#!/usr/bin/env python3

#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import os

from aws_cdk import core

from lex_sf_drug_reminder_blog.lex_sf_drug_reminder_stack import LexSFDCDrugReminderStack



app = core.App()

LexSFDCDrugReminderStack(app, "lex-sfdc-drug-reminder-blog")


app.synth()
