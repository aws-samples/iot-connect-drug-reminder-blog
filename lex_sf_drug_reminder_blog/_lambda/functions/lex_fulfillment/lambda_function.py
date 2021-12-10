#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import logging
import os

from lambda_helper import sfdc_update_refill_required_flag

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
LOG_FORMAT = "%(levelname)s:%(lineno)s:%(message)s"
handler = logging.StreamHandler()

_logger = logging.getLogger()
_logger.setLevel(LOG_LEVEL)


def lambda_handler(event, context):
    _logger.debug("incoming event: {}".format(event))

    intent_name = event["currentIntent"]["name"]
    slots = event["currentIntent"]["slots"]

    if intent_name == "update_sfdc_record" and slots.get("customer_id"):
        sfdc_customer_id = slots.get("customer_id")

        try:
            update_response = sfdc_update_refill_required_flag(customer_id=sfdc_customer_id)
        except Exception as e:
            raise Exception(
                "error happened requesting OAuth token from Salesforce: {}".format(e)
            )

        _logger.debug("SFDC update result: {}".format(json.dumps(update_response, indent=4)))

        return update_response
