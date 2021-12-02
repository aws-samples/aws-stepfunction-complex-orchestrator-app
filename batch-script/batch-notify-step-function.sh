#!/bin/sh
date
echo "Args: $@"
echo "-----------------------"
env
echo "-----------------------"

echo "This batch job attempts to sleep for given interval and then notify step function"
echo "jobId: $AWS_BATCH_JOB_ID"
echo "jobQueue: $AWS_BATCH_JQ_NAME"
echo "computeEnvironment: $AWS_BATCH_CE_NAME"
SLEEP_INT=$1
SQS_MSG_BODY=$2
STEP_FUNCTION_STATUS=$3
STEP_FUNCTION_ID=$4
STEP_FUNCTION_TASK_ID=$5
cat > send-message.json <<EOF_OF_MSG
{
    "Status": "$STEP_FUNCTION_STATUS",
    "ResponseMessage": "$SQS_MSG_BODY",
    "Function": "$STEP_FUNCTION_ID",
    "Task": "$STEP_FUNCTION_TASK_ID"
}
EOF_OF_MSG

sleep $SLEEP_INT
date

# If step function id does not start with valid aws arn, set it to empty
if [[ "$STEP_FUNCTION_ID" != "arn:aws:states"* ]]; then
  STEP_FUNCTION_ID=""
fi

# If no step function id or task id specified, just return
if [ "$STEP_FUNCTION_ID" == "" -o "$STEP_FUNCTION_TASK_ID" == "" ]; then
  echo "Completed batch job! Nothing to notify, exiting!!"
  exit 0
fi

echo "Done with activity, going to notify Step function : $STEP_FUNCTION_ID with task id: $STEP_FUNCTION_TASK_ID"
check_for_success=$(echo $STEP_FUNCTION_STATUS | grep -i ccess)
echo $check_for_success

if [ -z "$check_for_success" ]; then
	  aws stepfunctions send-task-failure --task-token $STEP_FUNCTION_TASK_ID --error failed
  else
	  aws stepfunctions send-task-success --task-token $STEP_FUNCTION_TASK_ID --task-output file://send-message.json
fi

echo "bye bye!!"
