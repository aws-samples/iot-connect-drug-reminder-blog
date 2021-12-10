
#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import logging
import os


import boto3

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
CONNECT_INSTANCE_ID = os.environ['CONNECT_INSTANCE_ID']
FLOW_ID = os.environ['FLOW_ID']
QueueId_ENV = os.environ['QueueId']

_logger = logging.getLogger()
_logger.setLevel(LOG_LEVEL)

print(os.getenv('PATIENT_RECORDS'))


from boto3.dynamodb.conditions import Key


# import requests
def lambda_handler(event, context):
    _logger.debug("incoming event: {}".format(event))
    response = {}
    for record in event.get('Records'):
        if record['eventName'] != 'INSERT':
            mobile_number = record['dynamodb']['NewImage']['Customer_Phone_Number']['S']
            print(mobile_number)
            Flag = record['dynamodb']['NewImage']['Calling_flag']['BOOL']
            print(Flag)
    
            if Flag:
                client = boto3.client('connect')
                dynamodb = boto3.resource('dynamodb')
    
                table = dynamodb.Table(os.environ['PATIENT_RECORDS'])
                resp = table.get_item(
                    Key={
                        'Customer_Phone_Number': mobile_number
                    }
                )
                #print(resp)
                #print(type(resp))
                #print(resp.get('Item',{}).get('Customer_Phone_Number'))
                Customer_Phone_Number = resp.get('Item',{}).get('Customer_Phone_Number')
                #print(Customer_Phone_Number)
    
                columns = ['Calling_Customer_Last_Name','Calling_Customer_First_Name','Customer_SSN_Last4','Customer_DOB','Number_Dosages','Time_Dosage','Name_Dosage,Medicine_Color','Medicine_Shape','Medicine_Size','Medicine_Location','Reminder_Time','MRI_Scan_Date','MRI_Scan_Time','Reminder_Required','Calling_flag','Refill_Required']
                Item_req = resp['Item']
                for col in columns:
                    if str(col) in Item_req:
                        Calling_Customer_First_Name = '' if not resp.get('Item',{}).get('Calling_Customer_First_Name') else resp.get('Item',{}).get('Calling_Customer_First_Name')
    
                        print(Calling_Customer_First_Name)
                        Calling_Customer_Last_Name = '' if not resp.get('Item',{}).get('Calling_Customer_Last_Name') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Customer_DOB = '' if not resp.get('Item',{}).get('Customer_DOB') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Customer_SSN_Last4 = '' if not resp.get('Item',{}).get('Customer_SSN_Last4') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Number_Dosages = '' if not resp.get('Item',{}).get('Number_Dosages') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Time_Dosage = '' if not resp.get('Item',{}).get('Time_Dosage') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Name_Dosage = '' if not resp.get('Item',{}).get('Name_Dosage')  else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Medicine_Color = '' if not resp.get('Item',{}).get('Medicine_Color') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Medicine_Shape = '' if not resp.get('Item',{}).get('Medicine_Shape') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Medicine_Size = '' if not resp.get('Item',{}).get('Medicine_Size') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Medicine_Location = '' if not resp.get('Item',{}).get('Medicine_Location') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Reminder_Time = '' if not resp.get('Item',{}).get('Reminder_Time') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        MRI_Scan_Date = '' if not resp.get('Item',{}).get('MRI_Scan_Date') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        MRI_Scan_Time = '' if not resp.get('Item',{}).get('MRI_Scan_Time') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Reminder_Required = '' if not resp.get('Item',{}).get('Reminder_Required') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Calling_flag = '' if not resp.get('Item',{}).get('Calling_flag') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                        Refill_Required = '' if not resp.get('Item',{}).get('Refill_Required') else resp.get('Item',{}).get('Calling_Customer_First_Name')
                    else:
                        print("This column {} is null ".format(col))
                # Dip please make sure that FlowID, InstanceID and QueueID has to be dynamic[update]
                response = client.start_outbound_voice_contact(
                    DestinationPhoneNumber=Customer_Phone_Number,
                    ContactFlowId=str(FLOW_ID),
                    InstanceId=str(CONNECT_INSTANCE_ID),
                    QueueId=str(QueueId_ENV),
                    Attributes={
                        'Calling_Customer_First_Name': Calling_Customer_First_Name,
                        'Calling_Customer_Last_Name': Calling_Customer_Last_Name,
                        'Customer_DOB': Customer_DOB,
                        'Customer_SSN_Last4': Customer_SSN_Last4,
                        'Number_Dosages': Number_Dosages,
                        'Name_Dosage': Name_Dosage,
                        'Medicine_Color': Medicine_Color,
                        'Medicine_Shape': Medicine_Shape,
                        'Medicine_Size': Medicine_Size,
                        'Medicine_Location': Medicine_Location,
                        'MRI_Scan_Date': MRI_Scan_Date,
                        'MRI_Scan_Time': MRI_Scan_Time,
                    }
                )
    
    print(response)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": response,
            # "location": ip.text.replace("\n", "")
        }),
    }
