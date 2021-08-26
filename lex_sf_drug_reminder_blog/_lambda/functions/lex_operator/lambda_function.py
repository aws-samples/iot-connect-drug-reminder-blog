#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import json
import logging
import os
import time
import zipfile

import boto3
import requests
from botocore.exceptions import ClientError

from lambda_helper import drug_reminder_lex_bot

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
LOG_FORMAT = "%(levelname)s:%(lineno)s:%(message)s"
handler = logging.StreamHandler()

_logger = logging.getLogger()
_logger.setLevel(LOG_LEVEL)

SUCCESS = "SUCCESS"
FAILED = "FAILED"

LATEST_ALIAS = '$LATEST'
LEX_LAMBDA_ARN = os.environ['LEX_LAMBDA_ARN']


def lambda_handler(event, context):
    _logger.debug("event: {}".format(event))

    responseData = {}

    # cloudformation delete
    if event['RequestType'] == 'Delete':

        client = boto3.client('lex-models')

        # delete bot
        try:
            response = client.delete_bot(
                name=drug_reminder_lex_bot['resource']['name']
            )

        except ClientError as e:
            print("lex-bot-delete-error: {}".format(e))

        else:
            print("lex-bot-delete-result: {}".format(response))

        time.sleep(30)

        # delete intent
        intents = [intent['name'] for intent in drug_reminder_lex_bot['resource'].get('intents', [])]

        for intent in intents:
            try:
                response = client.delete_intent(
                    name=intent
                )

            except ClientError as e:
                print("lex-intent-delete-error: {}".format(e))

            else:
                print("lex-intent-delete-result: {}".format(response))

            time.sleep(10)

        time.sleep(30)

        # delete slot_type
        slots_types = [slot_type['name'] for slot_type in drug_reminder_lex_bot['resource'].get('slotTypes', [])]
        for slot_type in slots_types:
            try:
                response = client.delete_slot_type(
                    name=slot_type
                )

            except ClientError as e:
                print("lex-slot-type-delete-error: {}".format(e))

            else:
                print("lex-slot-type-delete-result: {}".format(response))

        send(event, context, SUCCESS, responseData)
        return {
            'statusCode': 200,
            'body': json.dumps('Lambda deleted')
        }

    if event['RequestType'] == 'Create':

        data = drug_reminder_lex_bot
        data['resource']['intents'][3]['fulfillmentActivity']['codeHook']['uri'] = LEX_LAMBDA_ARN

        os.chdir('/tmp')

        with open("output.json", "w") as text_file:
            text_file.write(json.dumps(data))

        os.chdir('/tmp')
        zf = zipfile.ZipFile('updatedbot.zip', mode='w')
        try:
            zf.write('output.json')
        finally:
            zf.close()

        f = open('updatedbot.zip', 'rb')
        file_content = f.read()
        print(file_content)
        f.close()

        with open('output.json') as bot_def:
            bot_schema = json.load(bot_def)
            bot_schema_resource = bot_schema['resource']

        lambda_client = boto3.client('lambda')
        try:
            lambda_client.add_permission(FunctionName=LEX_LAMBDA_ARN.split(":")[6],
                                         StatementId="{}-intents".format(bot_schema_resource['name']),
                                         Action="lambda:invokeFunction",
                                         Principal="lex.amazonaws.com",
                                         SourceArn="arn:aws:lex:{}:{}:intent:*".format(LEX_LAMBDA_ARN.split(":")[3],
                                                                                       LEX_LAMBDA_ARN.split(":")[4]))
        except ClientError as e:
            print("add-permission-error: {}".format(e))

        client = boto3.client('lex-models')

        try:
            response = client.start_import(
                payload=file_content,
                resourceType='BOT',
                mergeStrategy='OVERWRITE_LATEST'
            )
        except ClientError as e:
            print("lex-model-create-error: {}".format(e))

        else:
            print("lex-model-create: {}".format(response))

        import_id = response['importId']

        for i in range(0, 5):
            try:
                import_status = client.get_import(
                    importId=import_id
                )
            except ClientError as e:
                print("import-status-error: {}".format(e))

            else:
                print("import-status: {}".format(import_status))

            time.sleep(5)

        with open('output.json') as lex_schema_file_input:
            full_schema = json.load(lex_schema_file_input)

        schema_resource = full_schema['resource']
        voice_id = schema_resource['voiceId']
        bot_name = schema_resource['name']
        child_directed = schema_resource['childDirected']

        bot_intents = []
        for intent in schema_resource['intents']:
            intent_name = intent['name']

            try:
                get_intent_response = client.get_intent(
                    name=intent_name,
                    version=LATEST_ALIAS
                )
            except ClientError as e:
                print("get-intent-error:{}".format(e))

            else:
                print("get-intent-response: {}".format(get_intent_response))

            bot_intents.append({
                'intentName': intent_name,
                'intentVersion': LATEST_ALIAS
            })

        try:
            get_bot_response = client.get_bot(
                name=bot_name,
                versionOrAlias=LATEST_ALIAS
            )
        except ClientError as e:
            print("get-bot-response-error: {}".format(e))

        else:
            print("get-bot-response: {}".format(get_bot_response))

        try:
            put_bot_result = client.put_bot(
                name=bot_name,
                checksum=get_bot_response['checksum'],
                childDirected=child_directed,
                locale=schema_resource['locale'],
                abortStatement=schema_resource['abortStatement'],
                clarificationPrompt=schema_resource['clarificationPrompt'],
                intents=bot_intents,
                processBehavior='BUILD',
                voiceId=voice_id
            )
        except ClientError as e:
            print("put-bot-error: {}".format(e))

        else:
            print("put-bot-result: {}".format(put_bot_result))

        send(event, context, SUCCESS, responseData, context.invoked_function_arn)

        # todo if error happens - cloud formation stack is just pending till timeout
        return {
            'statusCode': 200,
            'body': json.dumps('Lex Bot Deployed')
        }


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
