#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import os

import boto3
import requests
from botocore.exceptions import ClientError

from lambda_helper import connect_flow

SUCCESS = "SUCCESS"
FAILED = "FAILED"

CONNECT_LAMBDA_ARN = os.environ['CONNECT_LAMBDA_ARN']


def get_required_prompts(flow):
    # with open('{}/{}.json'.format(FLOWS_DIRECTORY, flow_name)) as f:
    #   flow = json.load(f)

    # Content is stored as string
    content = flow['Content']

    required_prompts = []

    for action_id in content['Metadata']['ActionMetadata'].keys():

        action = content['Metadata']['ActionMetadata'][action_id]
        if 'promptName' in action.keys():
            prompt_name = content['Metadata']['ActionMetadata'][action_id]['promptName']
            required_prompts.append(prompt_name)

    return required_prompts


def lambda_handler(event, context):
    responseData = {}

    connect_client = boto3.client('connect')

    # cloudformation delete
    if event['RequestType'] == 'Delete':
        pass

    #     # todo get names from json
    #     # delete bot
    #     try:
    #         response = client.delete_bot(
    #             name='MakeAppointment'
    #         )
    #
    #     except ClientError as e:
    #         print("lex-bot-delete-error: {}".format(e))
    #
    #     else:
    #         print("lex-bot-delete-result: {}".format(response))
    #
    #     time.sleep(10)
    #
    #     # delete intent
    #     try:
    #         response = client.delete_intent(
    #             name='MakeAppointment'
    #         )
    #
    #     except ClientError as e:
    #         print("lex-intent-delete-error: {}".format(e))
    #
    #     else:
    #         print("lex-intent-delete-result: {}".format(response))
    #
    #     time.sleep(10)
    #
    #     # delete slot_type
    #     try:
    #         response = client.delete_slot_type(
    #             name='AppointmentTypeValue'
    #         )
    #
    #     except ClientError as e:
    #         print("lex-slot-type-delete-error: {}".format(e))
    #
    #     else:
    #         print("lex-slot-type-delete-result: {}".format(response))
    #
    #     send(event, context, SUCCESS, responseData)
    #     return {
    #         'statusCode': 200,
    #         'body': json.dumps('Lambda deleted')
    #     }

    if event['RequestType'] == 'Create':
        # todo provided flows via url
        # flows = load_flows_from_backup()
        # flows = {'myflow': ''}
        flows = connect_flow

        # create_empty_flows(instance_id, flows)

        # todo necessary?
        prompts = get_prompts_by_name(instance_id)
        prompts = []

        for flow in flows.keys():

            # todo flow needs to be passed
            required_prompts = get_required_prompts(flow)

            # Confirm all required prompts exist
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
                    # update_flow(instance_id, flow_id, json.dumps(content))
                    response = connect_client.update_contact_flow_content(
                        InstanceId=instance_id,
                        ContactFlowId=flow_id,
                        Content=content
                    )

                except ClientError as err:
                    print(err)
                    print('ERROR: Failed to create flow {}'.format(flow))
                    # error_count += 1

            else:
                print('ERROR: {} was not imported due to missing prompts'.format(flow))
                # error_count += 1

    # url = LEX_SCHEMA
    # response = requests.get(url)
    # data = response.json()
    # # data = data.replace("LambdaURI", LEX_LAMBDA_ARN)
    # data['resource']['intents'][0]['fulfillmentActivity']['codeHook']['uri'] = LEX_LAMBDA_ARN
    # data['resource']['intents'][0]['dialogCodeHook']['uri'] = LEX_LAMBDA_ARN
    #
    # os.chdir('/tmp')
    #
    # with open("output.json", "w") as text_file:
    #     text_file.write(json.dumps(data))
    #
    # os.chdir('/tmp')
    # zf = zipfile.ZipFile('updatedbot.zip', mode='w')
    # try:
    #     zf.write('output.json')
    # finally:
    #     zf.close()
    #
    # f = open('updatedbot.zip', 'rb')
    # file_content = f.read()
    # print(file_content)
    # f.close()
    #
    # with open('output.json') as bot_def:
    #     bot_schema = json.load(bot_def)
    #     bot_schema_resource = bot_schema['resource']
    #
    # lambda_client = boto3.client('lambda')
    # try:
    #     lambda_client.add_permission(FunctionName=LEX_LAMBDA_ARN.split(":")[6],
    #                                  StatementId="{}-intents".format(bot_schema_resource['name']),
    #                                  Action="lambda:invokeFunction",
    #                                  Principal="lex.amazonaws.com",
    #                                  SourceArn="arn:aws:lex:{}:{}:intent:*".format(LEX_LAMBDA_ARN.split(":")[3],
    #                                                                                LEX_LAMBDA_ARN.split(":")[4]))
    # except ClientError as e:
    #     print("add-permission-error: {}".format(e))
    #
    # client = boto3.client('lex-models')
    #
    # try:
    #     response = client.start_import(
    #         payload=file_content,
    #         resourceType='BOT',
    #         mergeStrategy='OVERWRITE_LATEST'
    #     )
    # except ClientError as e:
    #     print("lex-model-create-error: {}".format(e))
    #
    # else:
    #     print("lex-model-create: {}".format(response))
    #
    # import_id = response['importId']
    #
    # for i in range(0, 5):
    #     try:
    #         import_status = client.get_import(
    #             importId=import_id
    #         )
    #     except ClientError as e:
    #         print("import-status-error: {}".format(e))
    #
    #     else:
    #         print("import-status: {}".format(import_status))
    #
    #     time.sleep(5)
    #
    # with open('output.json') as lex_schema_file_input:
    #     full_schema = json.load(lex_schema_file_input)
    #
    # schema_resource = full_schema['resource']
    # voice_id = schema_resource['voiceId']
    # bot_name = schema_resource['name']
    # child_directed = schema_resource['childDirected']
    #
    # bot_intents = []
    # for intent in schema_resource['intents']:
    #     intent_name = intent['name']
    #
    #     try:
    #         get_intent_response = client.get_intent(
    #             name=intent_name,
    #             version=LATEST_ALIAS
    #         )
    #     except ClientError as e:
    #         print("get-intent-error:{}".format(e))
    #
    #     else:
    #         print("get-intent-response: {}".format(get_intent_response))
    #
    #     bot_intents.append({
    #         'intentName': intent_name,
    #         'intentVersion': LATEST_ALIAS
    #     })
    #
    # try:
    #     get_bot_response = client.get_bot(
    #         name=bot_name,
    #         versionOrAlias=LATEST_ALIAS
    #     )
    # except ClientError as e:
    #     print("get-bot-response-error: {}".format(e))
    #
    # else:
    #     print("get-bot-response: {}".format(get_bot_response))
    #
    # try:
    #     put_bot_result = client.put_bot(
    #         name=bot_name,
    #         checksum=get_bot_response['checksum'],
    #         childDirected=child_directed,
    #         locale=schema_resource['locale'],
    #         abortStatement=schema_resource['abortStatement'],
    #         clarificationPrompt=schema_resource['clarificationPrompt'],
    #         intents=bot_intents,
    #         processBehavior='BUILD',
    #         voiceId=voice_id
    #     )
    # except ClientError as e:
    #     print("put-bot-error: {}".format(e))
    #
    # else:
    #     print("put-bot-result: {}".format(put_bot_result))
    #
    # send(event, context, SUCCESS, responseData, context.invoked_function_arn)
    #
    # # todo if error happens - cloud formation stack is just pending till timeout
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps('Lex Bot Deployed')
    # }


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
