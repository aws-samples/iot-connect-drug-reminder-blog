## Drug Reminder service using Amazon IOT, Amazon Lex and Amazon Connect

This repository compliments the blogpost *How to build Drug Reminder service using Amazon IOT, Amazon Lex and Amazon
Connect*
[Link](https://aws.amazon.com/blogs/contact-center/build-a-drug-reminder-service-with-aws-iot-amazon-lex-and-amazon-connect/)

## About the blog

Taking medications correctly is an important aspect of treatment for any illness, but when there are multiple pills to
take at different times of the day, it can become confusing, especially for people with mild
cognitive [impairment](https://www.verywellhealth.com/mild-cognitive-impairment-and-alzheimers-disease-98561)
, [Alzheimer's](https://www.verywellhealth.com/alzheimers-4581763)or another kind
of [dementia](https://www.verywellhealth.com/types-of-dementia-98770). Some medications are ordered for three times a
day, while others are taken on some days and not taken on other days. Since many people are on several medications, a
drug reminder system can often be helpful. Healthcare institutes can build a service to remind their patients to take
drug dosages in time. Especially for Alzheimer patients as they have the tendency to forget things. Additionally,
healthcare institutions would be interested in monitoring the real time benefits of taking the drugs on time. Building
an efficient drug adherence programme can not only improve the health of the patient suffering from chronic disease but
also save health costs and get clinical benefits.

The virtual health care assistant solution uses [Amazon IoT ](https://aws.amazon.com/iot/) to monitor the sensors
, [Amazon Connect](https://aws.amazon.com/connect/) to manage the call, [Amazon Lex](https://aws.amazon.com/lex/) as the
conversational interface, [AWS Lambda](https://aws.amazon.com/lambda/) to manage the data and connect to the CRM. In
this blog, you will learn how to use Amazon IOT , Amazon Connect and Amazon Lex to make an outbound reminder call to the
patient if they forget to take medicine at the prescribed time.

## Solution Architecture

![](./docs/architecture.png)

## Deploying the solution with AWS CDK

Deploying the solution with the AWS CDK The AWS CDK is an open-source framework for defining and provisioning cloud
application resources. It uses common programming languages such as JavaScript, C#, and Python.
The [AWS CDK command line interface](https://docs.aws.amazon.com/cdk/latest/guide/cli.html) (CLI) allows you to interact
with CDK applications. It provides features like synthesizing AWS CloudFormation templates, confirming the security
changes, and deploying applications.

This section shows how to prepare the environment for running CDK and the sample code. For this walkthrough, you must
have the following prerequisites:

*
An [AWS account](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fportal.aws.amazon.com%2Fbilling%2Fsignup%2Fresume&client_id=signup)
.
* An IAM user with administrator access
* [Configured AWS credentials](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_prerequisites)
* Installed Node.js, Python 3, and pip. To install the example application:

When working with Python, it’s good practice to use [venv](https://docs.python.org/3/library/venv.html#module-venv) to
create project-specific virtual environments. The use of `venv` also reflects AWS CDK standard behavior. You can find
out more in the
workshop [Activating the virtualenv](https://cdkworkshop.com/30-python/20-create-project/200-virtualenv.html).

1. Install the CDK and test the CDK CLI:
    ```bash
    $ npm install -g aws-cdk && cdk --version
    ```

2. Download the code from the GitHub repo and switch in the new directory:
    ```bash
    $ git clone https://github.com/aws-samples/iot-connect-drug-reminder-blog.git
    ```

3. Install the dependencies using the Python package manager:
   ```bash
   $ pip install -r requirements.txt
   ```
4. Fill in all the required parameters in the `env.sh` file as shown below and safe it:
   ```bash
   export CONNECT_INSTANCE_ID="<ConnectInstanceID>"
   export PROJECT_PREFIX="<ProjectPrefix>"
   export TIME_ZONE="US/Eastern"
   export CONSUMER_KEY="<SalesForceConsumerKey>"
   export CONSUMER_SECRET="<SalesForceConsumerSecret>"
   export USER_NAME="<SalesForceUserName>"
   export PASSWORD="<SalesForcePassword>"
   export SECURITY_TOKEN="<SalesForceUserSecurityToken>"
   export ENDPOINT="https://login.salesforce.com"
   ```

5. Test the configuration by executing a `cdk synthesize`. The configured `env.sh` file needs to be `sourced` first.
   ```bash
   $ source env.sh
   $ cdk synthesize
   ```

6. Below is a sample command to deploy the solution presented in the blog with the CDK CLI. The configured `env.sh` file
   needs to be `sourced` first.
    ```bash
    $ source env.sh
    $ cdk deploy 
    ```

## Cleaning up

Once you have completed the deployment and tested the application, clean up the environment to avoid incurring extra
cost. This command removes all resources in this stack provisioned by the CDK:

```bash
cdk destroy
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

