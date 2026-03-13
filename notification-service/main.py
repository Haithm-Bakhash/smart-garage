import pika
import time
import json
import os

# Give RabbitMQ a few seconds to boot up before we try to connect
time.sleep(15) 

def callback(ch, method, properties, body):
    message = json.loads(body)
    print("\n" + "="*50)
    print(f" [x] NEW ALERT: Sending email to user about their {message['car']}...")
    print(f"     Issues found: {message['issues']}")
    print(f"     Estimated Cost: ${message['cost']}")
    print("     [EMAIL SENT SUCCESSFULLY]")
    print("="*50 + "\n")

# Connect to the RabbitMQ container
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

# Create a mailbox (queue) called 'maintenance_alerts'
channel.queue_declare(queue='maintenance_alerts')

channel.basic_consume(queue='maintenance_alerts', on_message_callback=callback, auto_ack=True)

print(' [*] Notification Service is online and waiting for alerts...')
channel.start_consuming()