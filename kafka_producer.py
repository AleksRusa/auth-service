from datetime import datetime

from confluent_kafka import Producer
import json

from config.logger import logger


conf = {
    'bootstrap.servers': 'kafka:9092'
}

producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Error in message delivery to kafka: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def send_user_registered_event(email):
    topic = 'user-registration'
    message = {
        'event_type': 'user-registered',
        'email': email,
        'timestamp': datetime.now().isoformat()
    }

    producer.produce(
        topic,
        value=json.dumps(message).encode('utf-8'),
        callback=delivery_report
    )
    producer.flush()