#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

import setuptools

with open("README.md") as fp:
    long_description = fp.read()

CDK_VERSION = '1.90.0'

setuptools.setup(
    name="lex_sf_drug_reminder_blog",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "lex_sf_drug_reminder_blog"},
    packages=setuptools.find_packages(where="lex_sf_drug_reminder_blog"),

    install_requires=["aws-cdk.core=={}".format(CDK_VERSION),
                      "aws-cdk.aws_lambda=={}".format(CDK_VERSION),
                      "aws-cdk.aws_secretsmanager=={}".format(CDK_VERSION),
                      "aws-cdk.aws_iam=={}".format(CDK_VERSION),
                      "aws-cdk.aws_dynamodb=={}".format(CDK_VERSION),
                      "aws-cdk.aws_events=={}".format(CDK_VERSION),
                      "aws-cdk.aws_events_targets=={}".format(CDK_VERSION),
                      "aws-cdk.custom_resources=={}".format(CDK_VERSION),
                      "aws-cdk.aws_lambda_python=={}".format(CDK_VERSION),
                      "aws-cdk.aws_lambda_event_sources=={}".format(CDK_VERSION),
                      #add packages iot
                      "aws-cdk.aws_logs=={}".format(CDK_VERSION),
                      "aws-cdk.aws_iam=={}".format(CDK_VERSION),
                      "aws-cdk.aws_iot=={}".format(CDK_VERSION),
                      ],


    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
