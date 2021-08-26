#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import os
import boto3
import requests
import base64
import logging

from botocore.exceptions import ClientError
from simple_salesforce import Salesforce
from urllib.parse import urljoin

_logger = logging.getLogger()
session = boto3.session.Session()


def get_secret(secret_name):
    client = session.client(service_name="secretsmanager",
                            region_name=session.region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        _logger.error(
            "exception happened requesting secret from SecretsManager: {}".format(e)
        )
        raise e
    else:
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])

        return secret


def get_sfdc_credentials():
    credentials = {}
    params = [
        "CONSUMER_KEY",
        "CONSUMER_SECRET",
        "USER_NAME",
        "USER_PASSWORD",
        "USER_SECURITY_TOKEN",
        "SALESFORCE_ENDPOINT"
    ]

    for param in params:

        key = os.getenv(param)
        if not key:
            raise Exception(
                "parameter missing for SalesForce OAuth: {}".format(param)
            )

        credentials[param] = get_secret(os.getenv(param))

    return credentials


def get_salesforce_oauth_token():
    try:
        credentials = get_sfdc_credentials()
    except Exception as e:
        raise Exception("An error occurred looking up the SFDC credentials: {}".format(e))

    payload = {
        "grant_type": "password",
        "client_id": credentials["CONSUMER_KEY"],
        "client_secret": credentials["CONSUMER_SECRET"],
        "username": credentials["USER_NAME"],
        "password": "{}{}".format(
            credentials["USER_PASSWORD"], credentials["USER_SECURITY_TOKEN"]
        ),
    }

    result = requests.post(
        url=urljoin(os.getenv("SALESFORCE_ENDPOINT"), "/services/oauth2/token"),
        data=payload,
    )

    if result.status_code == requests.codes.ok:
        return result.json()

    else:
        raise Exception(
            "error happened loading access token from salesforce: {}".format(result.content)
        )


def sfdc_update_refill_required_flag(customer_id: str):
    return sf().Account.update(customer_id, {"Refill_Required__c": True})


def sf() -> Salesforce:
    token = get_salesforce_oauth_token()
    return Salesforce(
        instance_url=token["instance_url"], session_id=token["access_token"]
    )
