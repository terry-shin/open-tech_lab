from google.cloud import pubsub_v1, bigquery
import datetime


# 実行日時 
run_date = datetime.datetime.now().strftime('%Y-%m-%d%H:00:00')
timeout = 5.0

# TODO(developer)
project_id = "GCPプロジェクト"
subscription_id = "test-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
flow_control = pubsub_v1.types.FlowControl(max_messages=1)

# bigquery
table_name = f"{GCPプロジェクト}.crawler_test.test_table"

def callback(message):
    print(f"Received {message.data}.")
    print(f"Message_ID {message.message_id}.")
    print(f"Publish {message.publish_time}.")
    input_data = []

    if message.attributes:
        print("Attributes:")
        for key in message.attributes:
            value = message.attributes.get(key)
            print(f"{key}:{value}")
            input_data.append(f"{key}:{value}")
        regist_data(input_data)

    message.ack()

# bigquery 登録テスト
def regist_data(input_data):
    bigquery_client = bigquery.Client()

    insert_row = [
        {u"check_date": f"{run_date}", u"value1": f"{input_data[0]}", u"value2": f"{input_data[1]}"}
    ]

    errors = bigquery_client.insert_rows_json(table_name, insert_row) 
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))

def main(request):
    print("pub/sub TEST START")

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback, flow_control=flow_control)

    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except Exception as e:
            streaming_pull_future.cancel()
            print(
                f"Listening for messages on {subscription_path} threw an exception: {e}."
            )

    return 'Success'