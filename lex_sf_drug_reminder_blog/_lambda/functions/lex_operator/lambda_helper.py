#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

drug_reminder_lex_bot = {
  "metadata": {
    "schemaVersion": "1.0",
    "importType": "LEX",
    "importFormat": "JSON"
  },
  "resource": {
    "name": "Drug_Reminder_Bot",
    "version": "3",
    "intents": [
      {
        "name": "Dose_Confirm",
        "version": "2",
        "fulfillmentActivity": {
          "type": "ReturnIntent"
        },
        "sampleUtterances": [
          "Okay  I took it.",
          "I took it"
        ],
        "slots": []
      },
      {
        "name": "Dose_Quantity",
        "version": "2",
        "fulfillmentActivity": {
          "type": "ReturnIntent"
        },
        "sampleUtterances": [
          "How many do I need to take"
        ],
        "slots": []
      },
      {
        "name": "Auth",
        "version": "1",
        "fulfillmentActivity": {
          "type": "ReturnIntent"
        },
        "sampleUtterances": [
          "Yes"
        ],
        "slots": [
          {
            "sampleUtterances": [],
            "slotType": "AMAZON.DATE",
            "obfuscationSetting": "NONE",
            "slotConstraint": "Required",
            "valueElicitationPrompt": {
              "messages": [
                {
                  "contentType": "PlainText",
                  "content": "Great. Can you confirm your date of birth?"
                }
              ],
              "maxAttempts": 2
            },
            "priority": 1,
            "name": "DOB"
          },
          {
            "sampleUtterances": [],
            "slotType": "AMAZON.NUMBER",
            "obfuscationSetting": "NONE",
            "slotConstraint": "Required",
            "valueElicitationPrompt": {
              "messages": [
                {
                  "contentType": "PlainText",
                  "content": "And what are the last four digits of your social security number?"
                }
              ],
              "maxAttempts": 2
            },
            "priority": 2,
            "name": "SSN"
          }
        ]
      },
      {
        "name": "MRI_Scan",
        "version": "3",
        "fulfillmentActivity": {
          "codeHook": {
            "uri": None,
            "messageVersion": "1.0"
          },
          "type": "CodeHook"
        },
        "sampleUtterances": [
          "Yes when do I need to get my MRI scan done"
        ],
        "slots": []
      },
      {
        "name": "Dose_Appearance",
        "version": "3",
        "fulfillmentActivity": {
          "type": "ReturnIntent"
        },
        "sampleUtterances": [
          "not sure. What does it look like",
          "What does it look like"
        ],
        "slots": []
      },
      {
        "name": "Close_Intent",
        "version": "3",
        "fulfillmentActivity": {
          "type": "ReturnIntent"
        },
        "sampleUtterances": [
          "No"
        ],
        "slots": []
      }
    ],
    "voiceId": "Joanna",
    "childDirected": False,
    "locale": "en-US",
    "idleSessionTTLInSeconds": 300,
    "clarificationPrompt": {
      "messages": [
        {
          "contentType": "PlainText",
          "content": "Sorry, can you please repeat that?"
        }
      ],
      "maxAttempts": 5
    },
    "abortStatement": {
      "messages": [
        {
          "contentType": "PlainText",
          "content": "Sorry, I could not understand. Goodbye."
        }
      ]
    },
    "detectSentiment": False,
    "enableModelImprovements": False
  }
}