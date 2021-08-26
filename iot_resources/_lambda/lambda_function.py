#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import os
import boto3
from botocore.exceptions import ClientError
import time
import re
import datetime as dt
from pytz import timezone
import time_list
import pytz



import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)



# Setting the timezone
time_zone = str(os.environ['time_zone'])
dynamodb_table_name = os.environ['TableName']

if str(time_zone) not in time_list.time_zones:
    raise ValueError('Not a valid timezone: {} please refer to list below {}'.format(time_zone,time_list.time_zones))


dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])


def getPutDynamo(key_name, operation, key_value=None):
    logger.info("Check or update data Dynamo")
    table = dynamodb.Table(dynamodb_table_name)
    if operation == 'GET':
        try:
            response = table.get_item(
                Key={
                    'Customer_Phone_Number': key_name
                }
            )
            return response
        except ClientError as e:
            logger.info(e)
    elif operation == 'UPDATE':
        try:
            response= table.update_item(
                Key={
                    'Customer_Phone_Number': key_name
                },
                UpdateExpression='SET Calling_flag = :val1',
                ExpressionAttributeValues={
                    ':val1': key_value
                }
            )
            return response
        except ClientError as e:
            logger.info(e)




def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end



def lambda_handler(event, context):
    logging.info("event for debug")
    logging.info(event)
    timestamp_device = event['time']
    box_status_int = int(event['box_close'])
    customer_phone_number = str(event['Customer_Phone_Number'])

    #phone regex check
    regex_pattern = '^\++\d{1,15}'
    match = re.search(regex_pattern, customer_phone_number)
    if match:
        logger.info("Number valid proceed further")
    else:
       raise ValueError('Number provided by Medicine box: {} does not follow format, example: +1234567892')

    # Set wait time for minus 5 mins
    wait_time = 300
    now = dt.datetime.now()
    time_in_zone = now.astimezone(pytz.timezone(time_zone))
    now_minus_wait_time = time_in_zone - dt.timedelta(seconds=int(wait_time))

    # Get record from dynamo
    customer_record_dict = getPutDynamo(customer_phone_number,'GET')
    if len(customer_record_dict) == 0 or  'Item' not in customer_record_dict:
        logger.error("Record does not exist for customer")
        return {
            'statusCode': 500,
            'message': "Check record in Salesforce or Dynamo"
        }
    
    reminder_time_sf = str(customer_record_dict['Item']['Reminder_Time']).split('T')
    reminder_time_sf_dt = reminder_time_sf[0]
    reminder_time_sf_time = list(str(reminder_time_sf[1]).split('.'))[0]
    reminder_time_sf_comp = reminder_time_sf_dt+" "+reminder_time_sf_time
    reminder_time_pre = dt.datetime.fromisoformat(reminder_time_sf_comp)
    #reminder_time = reminder_time_pre.replace(tzinfo=timezone(str(time_zone)))
    reminder_time = reminder_time_pre.astimezone(pytz.timezone(time_zone))

    # Check if current time is withing 5 mins of reminder time
    print(reminder_time)
    print(now_minus_wait_time)
    print(time_in_zone)
    #print(now)
    modify_dynamo = time_in_range(now_minus_wait_time,time_in_zone,reminder_time)
    print(modify_dynamo)

    if modify_dynamo:
        logger.info("Check if box was opened")
        #check if calling flag is yes
        calling_flag = bool(customer_record_dict['Item']['Calling_flag'])
        #if calling_flag.upper() == 'TRUE':
        if calling_flag :
            logger.info("Call flag already set")
        else :
            logger.info("Call flag is not checked")
            # look for box was opened
            if box_status_int == 0:
                logger.info("Box has been opened")
            elif box_status_int == 1:
                logger.info("Box has not been opened, set calling flag")
                response = getPutDynamo(customer_phone_number,'UPDATE',True)
                return {
                        'statusCode': 200,
                        'message': 'Customer calling flag was set, initiate call flow'
                    }
    else:
        logger.info("Exit the function and reset the calling flag")
        response = getPutDynamo(customer_phone_number,'UPDATE',False)
        logger.info(response)
        return {
            'statusCode': 200,
            'message': "Check box status within 5 mins of reminder time"
        }

    
