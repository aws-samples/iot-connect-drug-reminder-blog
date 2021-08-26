#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import logging
import os

from lambda_helper import sfdc_query_patients_reminder, upload_records_dynamodb_table

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
LOG_FORMAT = "%(levelname)s:%(lineno)s:%(message)s"
handler = logging.StreamHandler()

_logger = logging.getLogger()
_logger.setLevel(LOG_LEVEL)


def lambda_handler(event, context):
    _logger.debug("incoming event: {}".format(event))

    try:
        payment_due = sfdc_query_patients_reminder()
    except Exception as e:
        raise Exception(
            "error happened requesting OAuth token from Salesforce: {}".format(e)
        )

    records = payment_due['records']
    print("SFDC result: {}".format(json.dumps(records, indent=4)))

    return upload_records_dynamodb_table(records)
