#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0import boto3
import json
import os
import time
import logging
from botocore.exceptions import ClientError
import requests


LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
LOG_FORMAT = "%(levelname)s:%(lineno)s:%(message)s"
handler = logging.StreamHandler()

_logger = logging.getLogger()
_logger.setLevel(LOG_LEVEL)


FLOWS_DIRECTORY='./connect'

ACCOUNT_ID = os.environ['ACCOUNT_ID']
REGION = os.environ['AWS_REGION']
CONNECT_INSTANCE_ID = os.environ['CONNECT_INSTANCE_ID']


SUCCESS = "SUCCESS"
FAILED = "FAILED"

connect_client = boto3.client('connect')
lex_client = boto3.client('lex-models')

error_count = 0

_logger = logging.getLogger()




def get_required_prompts(flow_name):

    with open('{}/{}.json'.format(FLOWS_DIRECTORY, flow_name)) as f:
      flow = json.load(f)

    # Content is stored as string
    content = flow['Content']

    required_prompts = []

    for action_id in content['Metadata']['ActionMetadata'].keys():

        action = content['Metadata']['ActionMetadata'][action_id]
        if 'promptName' in action.keys():
            prompt_name = content['Metadata']['ActionMetadata'][action_id]['promptName']
            required_prompts.append(prompt_name)

    return required_prompts


def update_flow(instance_id, flow_id, content):
    response = connect_client.update_contact_flow_content(
        InstanceId=instance_id,
        ContactFlowId=flow_id,
        Content=content
    )

def create_flow(instance_id, flow_type, flow_name, flow_content):
    response = connect_client.create_contact_flow(
        InstanceId=instance_id,
        Name=flow_name,
        Type=flow_type,
        Content=flow_content
    )


def get_flows(instance_id, NextToken=''):

    list_args = {
        'InstanceId':instance_id,
        'MaxResults':100
    }

    if NextToken != '':
        list_args['NextToken'] = NextToken

    response = connect_client.list_contact_flows(**list_args)

    flows = response['ContactFlowSummaryList']

    if 'NextToken' in response and response['NextToken'] != '':
        flows = flows + get_flows(instance_id, NextToken=response['NextToken'])

    return flows



def get_prompts(instance_id, NextToken=''):
    list_args = {
        'InstanceId':instance_id,
        'MaxResults':100
    }

    if NextToken != '':
        list_args['NextToken'] = NextToken

    response = connect_client.list_prompts(**list_args)

    prompts = response['PromptSummaryList']

    if 'NextToken' in response and response['NextToken'] != '':
        prompts = prompts + get_prompts(instance_id, NextToken=response['NextToken'])

    return prompts

def get_prompts_by_name(instance_id):

    prompts = get_prompts(instance_id)

    prompt_names = {}
    for prompt in prompts:
        prompt_names[prompt['Name']] = prompt['Id']

    return prompt_names

def get_flow_id(instance_id, flow_name):
    flows = get_flows(instance_id)

    for flow in flows:
        if flow_name == flow['Name']:
            return flow['Id']

    return False

def render_updated_flow(instance_id, flow_name):

    with open('{}/{}.json'.format(FLOWS_DIRECTORY, flow_name)) as f:
      flow = json.load(f)

    # Content is stored as string
    content = flow['Content']

    # id_map is updated during processing of metadata and referenced later when updating actions
    # actions do not always have the details needed that are stored in the metadata section
    # and this provides a lookup mechanism to lookup key attributes
    id_map = {}

    # Get current list of prompts to lookup id when updating action
    prompts = get_prompts_by_name(instance_id)


    for action_id in content['Metadata']['ActionMetadata'].keys():

        action = content['Metadata']['ActionMetadata'][action_id]
        if 'ContactFlow' in action.keys():

            dependency_flow_name = action['ContactFlow']['text']
            updated_dependency_flow_id = get_flow_id(instance_id, dependency_flow_name)
            updated_dependency_arn = 'arn:aws:connect:{}:{}:instance/{}/contact-flow/{}'.format(REGION, ACCOUNT_ID, instance_id, updated_dependency_flow_id)
            id_map[action_id] = updated_dependency_arn
            content['Metadata']['ActionMetadata'][action_id]['ContactFlow']['id'] = updated_dependency_arn

        if 'promptName' in action.keys():

            id_map[action_id] = action['promptName']

    index = 0

    for action in content['Actions']:

        action_id = action['Identifier']

        if 'Parameters' in action.keys() and 'ContactFlowId' in action['Parameters'].keys():

            content['Actions'][index]['Parameters']['ContactFlowId']=id_map[action_id]

        if 'Parameters' in action.keys() and 'LambdaFunctionARN' in action['Parameters'].keys():

            dependency_arn = content['Actions'][index]['Parameters']['LambdaFunctionARN']
            function_name = dependency_arn.split(':')[-1]
            updated_dependency_arn = 'arn:aws:lambda:{}:{}:function:{}'.format(REGION,ACCOUNT_ID, function_name)
            content['Actions'][index]['Parameters']['LambdaFunctionARN']=updated_dependency_arn

        if 'Parameters' in action.keys() and 'PromptId' in action['Parameters'].keys() and 'LexBot' not in action['Parameters'].keys() :

            prompt_name = id_map[action_id]
            updated_prompt_id = prompts[prompt_name]
            updated_prompt_arn = 'arn:aws:connect:{}:{}:instance/{}/prompt/{}'.format(REGION, ACCOUNT_ID, instance_id, updated_prompt_id)
            content['Actions'][index]['Parameters']['PromptId']=updated_prompt_arn
        
        if 'Parameters' in action.keys() and 'LexBot' in action['Parameters'].keys() :
#
            content['Actions'][index]['Parameters']['LexBot']['Region']=REGION
#
        index += 1

    return content




def create_empty_flows(instance_id, flows):
    # To handle dependecies make sure all flows exist before restoring
    for flow in flows.keys():
        flow_name = flow
        flow_type = flows[flow]['Type']
        empty_flow = {
            "Version":"2019-10-30",
            "StartAction":"09127987-9dab-420c-b9ac-fb6a4bd35810",
            "Metadata":{
                "entryPointPosition":{"x":19,"y":20},
                "snapToGrid":False,
                "ActionMetadata":{
                    "09127987-9dab-420c-b9ac-fb6a4bd35810":{
                        "position":{"x":241,"y":102}
                    }
                }
            },
            "Actions":[
                {
                    "Identifier":"09127987-9dab-420c-b9ac-fb6a4bd35810",
                    "Type":"DisconnectParticipant",
                    "Parameters":{},
                    "Transitions":{}
                }
            ]
        }

        try:
            create_flow(instance_id, flow_type, flow_name, json.dumps(empty_flow))
        except connect_client.exceptions.DuplicateResourceException as error:
            # Fails with DuplicateResourceException when flow already exists.
            pass


def load_flows_from_backup():
    global error_count

    flows = {}

    files = os.listdir(FLOWS_DIRECTORY)

    for file in files:
        with open('{}/{}'.format(FLOWS_DIRECTORY, file)) as f:
            try:
                flow = json.load(f)
                content = flow['Content']
                flows[file.split('.')[0]]=flow
            except json.decoder.JSONDecodeError:
                print('ERROR: Failed to load {} due to invalid JSON'.format(file))
                error_count += 1

    return flows



def import_flows(instance_id):
    global error_count

    if not os.path.exists(FLOWS_DIRECTORY):
        print('ERROR: Unable to locate directory {}'.format(FLOWS_DIRECTORY))
        return

    flows = load_flows_from_backup()
    create_empty_flows(instance_id, flows)

    prompts = get_prompts_by_name(instance_id)

    for flow in flows.keys():

        required_prompts = get_required_prompts(flow)

        # Conirm all required prompts exist
        prompt_validation = True
        for required_prompt in required_prompts:
            if required_prompt not in prompts:
                prompt_validation = False
                print('ERROR: Missing prompt {} for flow {}'.format(required_prompt, flow))

        if prompt_validation:

            print('Importing flow {}'.format(flow))
            content = render_updated_flow(instance_id, flow)
            flow_id = get_flow_id(instance_id, flow)
            try:
                update_flow(instance_id, flow_id, json.dumps(content))
            except Exception as err:
                print(err)
                print('ERROR: Failed to create flow {}'.format(flow))
                error_count += 1

        else:
            print('ERROR: {} was not imported due to missing prompts'.format(flow))
            error_count += 1

def list_bots(nextToken=''):
    response = lex_client.get_bots(
        nextToken=nextToken,
        maxResults=50
    )

    bots = response['bots']

    if 'nextToken' in response and response['nextToken'] != '':
        bots = bots + list_bots(nextToken=response['nextToken'])

    return bots

def grant_lex_access(instance_id, bot):
    # This API method is in preview as of 12/23/2020 and may change
    response = connect_client.associate_lex_bot(
        InstanceId=instance_id,
        LexBot={
            'Name': bot,
            'LexRegion': REGION
        }
    )

def update_bot_access(instance_id, retry=0):
    global error_count

    print('Updating connect permissions for all Lex bots')
    bots = list_bots()
    for bot in bots:
        if "Drug_Reminder_Bot" in bot['name']:
            bot_name = bot['name']
            try:
                grant_lex_access(instance_id, bot_name)
            except:
                retry += 1
                if retry < 3:
                    print('AssociateLexBot operation failed, pausing for 5 seconds before retrying')
                    time.sleep(5)
                    update_bot_access(instance_id, retry)
                else:
                    print('Error: Exceeded max retries for AssociateLexBot')
                    error_count += 1

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']

    print(responseUrl)

    responseBody = {
        'Status': responseStatus,
        'Reason': 'See the details in CloudWatch Log Stream: {}'.format(context.log_stream_name),
        'PhysicalResourceId': physicalResourceId or context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'NoEcho': noEcho,
        'Data': responseData
    }

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {
        'content-type': '',
        'content-length': str(len(json_responseBody))
    }

    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))

def lambda_handler(event, context):
    _logger.debug("incoming event: {}".format(event))
    responseData = {}
    if event['RequestType'] == 'Create':
        import_flows(CONNECT_INSTANCE_ID)
        update_bot_access(CONNECT_INSTANCE_ID)
        responseData = {}

        send(event, context, SUCCESS, responseData, context.invoked_function_arn)


        return {
                'statusCode': 200,
                'body': json.dumps('Connect updated')
            }
    if event['RequestType'] == 'Delete':

        send(event, context, SUCCESS, responseData, context.invoked_function_arn)


        return {
                'statusCode': 200,
                'body': json.dumps('Connect Delete Flow Called')
            }


#if __name__ == '__main__':
#
#    import_flows(CONNECT_INSTANCE_ID)
#    update_bot_access(CONNECT_INSTANCE_ID)