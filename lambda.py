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
# from re import (
#     search
# )

import requests
from boto3 import client


def handler(event, context):
    task_definition_arn = event["detail"]["taskDefinitionArn"]
    task_react = event["detail"]["stoppedReason"]
    cluster_arn = event["detail"]["clusterArn"]
    last_status = event["detail"]["lastStatus"]
    event_json = dumps(event)

    #process_record(cluster_arn, task_group, task_definition_arn, event_json)
    post_to_slack(task_react, task_definition_arn, cluster_arn, last_status)


#def get_message_key(cluster_arn, task_definition_arn, task_group):
#    m = search(r"/(.*)", cluster_arn)
#    cluster_name = m.group(1)
#
#    m = search(r"/(.*)", task_definition_arn)
#    task_definition_name = m.group(1)
#
#    return "{}/{}/{}-failure-message.json".format(cluster_name, task_group, task_definition_name)


#def check_for_message(s3, bucket_name, message_key):
#    """
#    Check if the message already exists in the bucket
#
#
#    :s3: S3 client
#    :bucket_name: Name of the bucket
#    :message_key: Key of the message to look for
#    :returns: False if the message doesn't exist and true if it does
#
#    """
#    try:
#        s3.get_object(
    #         Bucket=bucket_name,
    #         Key=message_key,
    #     )
    #     return True
    # except Exception as e:
    #     print(e)  # noqa
    #     return False


def post_to_slack(task_react, task_definition_arn, cluster_arn, last_status):
    """
    Post failure message to slack

    :task_group: Task Group name from the AWS event
    :task_definition_arn: Task Definition identifier from the AWS event
    :returns: False if the message was not posted to slack True if it was

    """
    webhook_url = environ["SLACK_WEBHOOK_URL"]

    # message = "The Cluster [{}] task [{}] is failing to deploy to [{}]".format(
    #     cluster_arn,
    #     task_react,
    #     task_definition_arn,
    # )

    if last_status = "STOPPED":
        cluster = cluster_arn.split('/')
        cluster = cluster[-1]

        task_definition = task_definition_arn.split('/')
        task_definition = task_definition[-1]
    
        slack_data = {"text": "ECS Task State Change", "attachments":[{"color":"#D00000","fields":[{"title": "Cluster","value": cluster}, {"title": "TaskDefinition","value": task_definition}, {"title": "ExitStatus","value": task_react}, {"title": "LastStatus","value": last_status}]}]}
        #slack_data = {"text": message, "attachments":[{"color":"#D00000","fields":[{"title":cluster,"value":"É muito mais fácil do que eu esperava."}]}]}

        response = requests.post(
            webhook_url, data=dumps(slack_data),
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code != 200:
            print("Error posting the message to slack, response wasn't 200")  # noqa
            return False

        return True

