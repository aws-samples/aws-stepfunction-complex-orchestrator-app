import boto3
import json
import time
import random

STEP_FUNCTIONS_CLIENT = boto3.client("stepfunctions")


def lambda_handler(event: dict, _context: dict):
    """Sample Lambda function that notifies back the Step function that invoked it,
    using the Task Token id passed along with its payload

    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function
        Requires a valid task token to be passed as 'token'.

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
        dict: status of notification
    """
    if event:
        print("New event consumed :  {}.".format(event))
    
        time.sleep(6)

        #print("Sending task heartbeat for task ID {}".format(body['token']))
        #STEP_FUNCTIONS_CLIENT.send_task_heartbeat(taskToken=body["token"])
        is_task_success = random.choice([True, False])

        body = event['body']
        taskToken = event['token']
        id = event['aws_stepfunction_execution_id']
        

        print("Sending task success for task ID  {}".format(taskToken))
        STEP_FUNCTIONS_CLIENT.send_task_success(
            taskToken=taskToken,
            output=json.dumps({"id": id})
        )
        
        return { "status": "notified" }

        # if is_task_success:
        #     print("Sending task success for task ID  {}".format(taskToken))
        #     STEP_FUNCTIONS_CLIENT.send_task_success(
        #         taskToken=taskToken,
        #         output=json.dumps({"id": id})
        #     )
        # else:
        #     print("Sending task failure for task ID  {}".format(taskToken))
        #     STEP_FUNCTIONS_CLIENT.send_task_failure(
        #         taskToken=taskToken,
        #         cause="Random choice returned False."
        #     )
                
