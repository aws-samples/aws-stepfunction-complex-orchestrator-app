import json
import boto3
import os
import time



print('Loading function')

batch = boto3.client('batch')


def lambda_handler(event, context):
    """Sample Lambda function that submits a AWS Batch Job with some payloads that makes it mimic an activity.
    This would be invoked by a Step function using waitForCallback token pattern.

    The Lambda function passes along the Step function's TaskToken ID to the Batch job which would 
    then use it to notify (success or failure) completion back to Step function.

    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
        dict: Object containing details of the Batch job
    """
    # Log the received event
    print("Received event: {} ".format(event))
    # Get parameters for the SubmitJob call
    # http://docs.aws.amazon.com/batch/latest/APIReference/API_SubmitJob.html
    
    jobName =  (os.environ.get('JOB_NAME') + str(time.time())).split('.')[0]      #event['jobName']
    jobQueue = os.environ.get('JOB_QUEUE')                                        #event['jobQueue']
    jobDefinition = os.environ.get('JOB_DEFINITION')                              #event['jobDefinition']
    
    body = str(event['body'])
    taskToken = event['token']
    batch_status = event['status']
    sleep_interval = str(event['sleep_interval'])
    id = event['aws_stepfunction_execution_id']
        
    # containerOverrides and parameters are optional
    if event.get('containerOverrides'):
        containerOverrides = event['containerOverrides']
    else:
        containerOverrides = { 'command' : ["batch-notify-step-function.sh","Ref::sleep_interval",
                                            "Ref::batch_body","Ref::batch_status","Ref::function_id",
                                            "Ref::task_token"] }
    
    parameters = { 
                "batch_body": body, 
                "task_token": taskToken, 
                "function_id": id, 
                "batch_status": batch_status,  
                "sleep_interval": sleep_interval
    }

    print("Submitting job name: {} , defn: {}, queue: {},\n with containerOverrides: {},\n \
            parameters: {}".format(jobName, jobDefinition, jobQueue, containerOverrides, parameters))
    try:
        # Submit a Batch Job
        response = batch.submit_job(jobQueue=jobQueue, jobName=jobName, jobDefinition=jobDefinition,
                                    containerOverrides=containerOverrides, parameters=parameters)
        # Log response from AWS Batch
        print("Response: " + json.dumps(response, indent=2))
        # Return the jobId
        jobId = response['jobId']
        return {
            'jobId': jobId
        }
    except Exception as e:
        print(e)
        message = 'Error submitting Batch Job'
        print(message)
        raise Exception(message)

