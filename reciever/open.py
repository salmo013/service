import connexion, json, os
import requests
import yaml
import logging
import logging.config
import datetime
from connexion import NoContent
from pykafka import KafkaClient
import time


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Enviroment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Enviroment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
   log_config = yaml.safe_load(f.read())
   logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info(f'App Conf File: {app_conf_file}')
logger.info(f'Log Conf File: {log_conf_file}')

#def get_motion_readings(timestamp)
#    response = requests.get(app_config['eventget1']['url'],json = body,headers=headers )

####Lab 9#####################################
attempts = 0
max_attempts = app_config['connection']['tries']
while attempts < max_attempts:
    try: 
        client = KafkaClient(hosts='3.21.10.177:9092')
        topic = client.topics[str.encode('events')]
        attempts = 15
        #topic = client.topics[str.encode(app_config["events"]["topic"])]
    except:
        logger.error('failed to connect to kafka')
    time.sleep(app_config['time']['sleep'])
    attempts += 1
    logger.info(f'trying to connect to kafka, number of attempts = {attempts}')

####################################################

# def movementDetection(body):
#     logger.info(f'Recived event movement detection at {body["item"]}')
#     headers = {"content-type": "application/json"}
#     response = requests.post(app_config['eventstore1']['url'],json = body,headers=headers )
#     logger.info(f'Recived response for {body["item"]} with a status {response.status_code}')
#     # print(response.headers)
#     return NoContent, response.status_code # NoContent means there is no response message

def movementDetection(body):
    #client = KafkaClient(hosts='3.21.10.177:9092')
    #topic = client.topics[str.encode('events')]
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
    
        #client = KafkaClient(hosts='3.21.10.177:9092')
        #topic = client.topics[str.encode('events')]
    producer = topic.get_sync_producer()
    msg = { "type": "doormotion", "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
            
    return 201



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("inmotion.yaml",base_path="/reciever",strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080)