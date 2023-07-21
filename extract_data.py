import boto3
import os
from datetime import datetime
import json
import pandas as pd
import pytz

def convert_epoch_to_central_time(epoch):
    # Define the time zone
    central_timezone = pytz.timezone('America/Chicago')

    # Convert epoch to datetime object
    datetime_obj = datetime.fromtimestamp(epoch/1000)  # Assuming the epoch is in milliseconds

    # Localize the datetime object to UTC
    datetime_utc = pytz.utc.localize(datetime_obj)

    # Convert the datetime object to the Central timezone
    datetime_central = datetime_utc.astimezone(central_timezone)

    # Extract the date and time separately
    date_central = datetime_central.date()
    time_central = datetime_central.time()

    return date_central, time_central


def extract_data_from_json(response, start_date, end_date, bot_id_filter, bucket_name):
    data = []
    for obj in response['Contents']:
        # Retrieve the JSON file from S3
        file_key = obj['Key']
        #last_modified = obj['LastModified']
        last_modified = obj['LastModified'].replace(tzinfo=None) 

        # Retrieve AWS access keys from environment variables
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

        # Create an S3 client
        s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

        # Compare the last modified date with the threshold
        if start_date <= last_modified <= end_date:
            response = s3_client.get_object(Bucket=bucket_name ,Key=file_key)
            json_data = response['Body'].read().decode('utf-8')

            # Parse the JSON data
            try:
                json_object = json.loads(json_data)
                session_id = json_object.get('session_id')
                account_id = json_object.get('account_id')
                referrer = json_object.get('referrer')
                bot_name = json_object.get('bot_name')
                is_billable = json_object.get('is_billable')
                is_test = json_object.get('is_test')
                bot_id = json_object.get('bot_id')
                created_at = json_object.get('created_at')
                history = json_object.get('history')
                turns = len(history["turns"])
                confidence_threshold = json_object['config']['semantic_search']['confidence_threshold']
                auto_add_threshold_lower = json_object['config']['online_learning']['utterance_auto_add_threshold_lower']
                auto_add_threshold_upper = json_object['config']['online_learning']['utterance_auto_add_threshold_upper']
                fail_counter = json_object['state']['fail_counter']
                fail_turn_indices = json_object['state']['fail_turn_indices']
                report_indices = json_object['state']['report_indices']
                email_triggers = json_object['state']['email_triggers']
                max_consecutive_fails = json_object['config']['fail_mechanism']['max_consecutive_fails']
                user_conversation = extract_user_conversation(json_object) or []
                component_info = extract_component_info(json_object) or []

                # Filter by bot_id
                if bot_id == bot_id_filter:
                    # Convert epoch time to date format
                    created_at_date = datetime.fromtimestamp(created_at // 1000).strftime('%Y-%m-%d')  # Assuming milliseconds precision
                    created_at_time = datetime.fromtimestamp(created_at // 1000).strftime('%H:%M:%S')  # Assuming milliseconds precision

                    # Convert epoch time to Central Time
                    created_at_date_central, created_at_time_central = convert_epoch_to_central_time(created_at)


                    data.append([session_id, account_id, referrer, bot_name, bot_id, turns, created_at, is_billable,
                                 is_test, confidence_threshold, auto_add_threshold_lower, auto_add_threshold_upper,
                                 created_at_date, created_at_time,fail_counter, 
                                 fail_turn_indices, report_indices, email_triggers, max_consecutive_fails, 
                                 user_conversation, component_info, created_at_date_central, created_at_time_central])
                    
            except json.JSONDecodeError:
                print(f"Error decoding JSON data in file: {file_key}")


    return pd.DataFrame(data)



def extract_user_conversation(json_data):
    conversation = []
    history = json_data['history']['turns']

    for turn in history:
        if 'speaker' in turn and 'utterance' in turn:
            speaker = turn['speaker']
            utterances = turn['utterance']
            
            for utterance in utterances:
                conversation.append({
                    'speaker': speaker,
                    'utterance': utterance
                })
    
    return conversation if conversation else [{}]



def extract_component_info(json_data):
    component_info = []
    state = json_data.get('state')

    if state and 'component_state' in state:
        component_state = state['component_state']

        query_results = component_state.get('query_results')
        if query_results:
            for query_result in query_results:
                component_id = query_result.get('_source', {}).get('component_id')
                component_name = query_result.get('_source', {}).get('component_name')
                component_type = query_result.get('_source', {}).get('component_type')

                component_info.append({
                    'component_id': component_id if component_id else None,
                    'component_name': component_name if component_name else ''
                })

    return component_info if component_info else [{}]
