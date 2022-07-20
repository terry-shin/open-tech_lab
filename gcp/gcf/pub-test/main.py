import os
from google.cloud import pubsub_v1

# 環境変数から値を取得
PROJECT_ID = os.environ.get('PROJECT_ID', "GCPプロジェクト")
TOPIC_ID = os.environ.get('TOPIC_ID', "test")

# publisher client
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

def main(request):
    print("pub/sub TEST START")

    # サンプルメッセージを10件
    for n in range(1, 10):
        data = "Message number {}".format(n)
        # Data must be a bytestring
        data = data.encode("utf-8")
        # Add two attributes, origin and username, to the message
        future = publisher.publish(
            topic_path, data, title="python-sample", username="testuser_{}".format(n), testparam="テスト"
        )
        print(future.result())

    print(f"Published messages with custom attributes to {topic_path}.")      
    return 'Success'
 