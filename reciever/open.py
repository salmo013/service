import connexion, json, os
import requests
import yaml
import logging
import logging.config
import datetime
from connexion import NoContent
from pykafka import KafkaClient

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
   log_config = yaml.safe_load(f.read())
   logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

#def get_motion_readings(timestamp)
#    response = requests.get(app_config['eventget1']['url'],json = body,headers=headers )


# def movementDetection(body):
#     logger.info(f'Recived event movement detection at {body["item"]}')
#     headers = {"content-type": "application/json"}
#     response = requests.post(app_config['eventstore1']['url'],json = body,headers=headers )
#     logger.info(f'Recived response for {body["item"]} with a status {response.status_code}')
#     # print(response.headers)
#     return NoContent, response.status_code # NoContent means there is no response message

def movementDetection(body):
    client = KafkaClient(hosts='3.21.10.177:9092')
    topic = client.topics[str.encode('events')]
    producer = topic.get_sync_producer()
    msg = { "type": "motion", "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return 201





def doorDetection(body):
    # logger.info(f'Recived event door detection at {body["item"]}')
    # headers = {"content-type": "application/json"}
    # #print(app_config['eventstore2']['url'])
    # response = requests.post(app_config['eventstore2']['url'], json=body, headers = headers)
    # logger.info(f'Recived response for {body["item"]} with a status {response.status_code}')

    # return NoContent, response.status_code  # NoContent means there is no response message
    client = KafkaClient(hosts='3.21.10.177:9092')
    topic = client.topics[str.encode('events')]
    producer = topic.get_sync_producer()
    msg = { "type": "doormotion", "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    return 201



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("inmotion.yaml",strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080)