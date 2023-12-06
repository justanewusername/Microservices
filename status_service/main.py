import pika
import requests
import json
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
class BrokerManager:
    def __init__(self, queue_name: str, host: str):
        self.queue_name = queue_name

        connection = pika.BlockingConnection(pika.ConnectionParameters(host))
        self.channel = connection.channel()
        self.channel.queue_declare(queue=queue_name)

    def set_callback(self, callback):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)

def callback(ch, method, properties, body):
    msg = json.loads(body)

    response = None
    try:
        response = requests.get(msg['link'])
    except:
        print("wtf!")
    
    status_code = 0
    if response is not None:
        status_code = response.status_code
    
    send_status_code(msg['link_id'] ,status_code)

    # Подтверждение обработки сообщения (acknowledge)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def send_status_code(link_id: int, status_code: int):
    url = f'http://app:80/links?link_id={link_id}&status={status_code}'
    response = requests.put(url)

    if response.status_code == 200:
        print("Link updated successfully")
    else:
        print(f"Failed to update link. Status code: {response.status_code}, Response content: {response.text}")


queue_name = 'links'
broker = BrokerManager(queue_name, 'rabbitmq')
broker.set_callback(callback)


print(' [*] Waiting for messages. To exit, press CTRL+C')
broker.channel.start_consuming()