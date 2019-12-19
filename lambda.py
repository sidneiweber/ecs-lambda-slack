"""
Get notification from ECS when a deployment is failing. Post to slack

This lambda function receives a notification from a cloudwatch log filter when
an ECS deployment fails, it creates a hash based on the cluster arn and then
task definition and saves the file in S3.

To make sure we don't get duplicate, if we already have a file in S3, we don't
resend the notification.

"""
from json import dumps
from os import environ
import requests
from boto3 import client


def handler(event, context):
    task_definition_arn = event["detail"]["taskDefinitionArn"]
    task_group = event["detail"]["group"]
    cluster_arn = event["detail"]["clusterArn"]
    event_json = dumps(event)

    #process_record(cluster_arn, task_group, task_definition_arn, event_json)
    post_to_slack(task_group, task_definition_arn)


def post_to_slack(task_group, task_definition_arn):
    """
    Post failure message to slack

    :task_group: Task Group name from the AWS event
    :task_definition_arn: Task Definition identifier from the AWS event
    :returns: False if the message was not posted to slack True if it was

    """
    webhook_url = environ["SLACK_WEBHOOK_URL"]

    message = "The task [{}] is failing to deploy to [{}]".format(
        task_group,
        task_definition_arn,
    )
    slack_data = {"text": message}

    response = requests.post(
        webhook_url, data=dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        print("Error posting the message to slack, response wasn't 200")  # noqa
        return False

    return True
