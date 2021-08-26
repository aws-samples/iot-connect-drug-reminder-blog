#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import base64
import json
import logging
import os
from urllib.parse import urljoin

import boto3
import requests
from botocore.exceptions import ClientError
from dynamodb_json import json_util
from simple_salesforce import format_soql, Salesforce

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
        # todo remove
        # credentials[param] = key
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
        url=urljoin(credentials["SALESFORCE_ENDPOINT"], "/services/oauth2/token"),
        data=payload,
    )

    if result.status_code == requests.codes.ok:
        return result.json()

    else:
        raise Exception(
            "error happened loading access token from salesforce: {}".format(result.content)
        )


def remove_sfdc_custom_field_notation(sfdc_record):
    record = {}
    for custom_key in list(sfdc_record.keys()):
        record[custom_key.replace('__c', '')] = sfdc_record[custom_key]

    return record


def sfdc_query_patients_reminder():
    query = """
        SELECT Id, Name, OwnerId, Customer_Phone_Number__c, 
        Calling_Customer_First_Name__c, Calling_Customer_Last_Name__c, Customer_DOB__c, Customer_SSN_Last4__c, 
        Number_Dosages__c, Time_Dosage__c, Name_Dosage__c, Medicine_Color__c, Medicine_Shape__c, Medicine_Size__c, 
        Medicine_Location__c, Reminder_Time__c, MRI_Scan_Date__c, MRI_Scan_Time__c, Reminder_Required__c,
        Calling_flag__c, Refill_Required__c 
        FROM Account 
        WHERE Calling_flag__c = TRUE AND Reminder_Required__c = TRUE 
        ORDER BY LastModifiedDate DESC
    """
    interpolated_query = format_soql(query)
    return sf().query(interpolated_query)


def sf() -> Salesforce:
    token = get_salesforce_oauth_token()
    return Salesforce(
        instance_url=token["instance_url"], session_id=token["access_token"]
    )


def upload_records_dynamodb_table(records: list):
    result = []
    print(records)
    dynamodb_client = session.client(service_name='dynamodb',
                                     region_name=session.region_name)
    table = os.getenv("DYNAMO_DB_TABLE")
    for record in records:
        record_raw = json.loads(json_util.dumps(record))
        record_dynamo = remove_sfdc_custom_field_notation(record_raw)
        try:
            result += [dynamodb_client.put_item(TableName=table,
                                                Item=record_dynamo)]
        except ClientError as e:
            raise e

    return result
