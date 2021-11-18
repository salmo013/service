import connexion, json, os
import requests
import yaml
import logging
import logging.config
import datetime 
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin

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


def get_door_motion(index):
    """ Get motion Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
    app_config["events"]["port"])
    #client = KafkaClient(hosts=hostname)
    #topic = client.topics[str.encode(app_config["events"]["topics"])]
    client = KafkaClient(hosts='3.21.10.177:9092')
    topic = client.topics[str.encode('events')]
 # Here we reset the offset on start so that we retrieve
 # messages at the beginning of the message queue. 
 # To prevent the for loop from blocking, we set the timeout to
 # 100ms. There is a risk that this loop never stops if the
 # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, 
    consumer_timeout_ms=1000)
    logger.info("Retrieving door motion at index %d" % index)
    #logger.info(consumer)
    counter = 0
    try:
        logger.info('this is the get for door motion')
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if counter == index and msg['type'] == "doormotion":
                return msg , 200
            counter += 1
    # Find the event at the index you want and 
       # return code 200
    # i.e., return event, 200
    except:
        logger.error("No more messages found")
 
        logger.error("Could not find motion at index %d" % index)
    return { "message": "Not Found"}, 404





def get_motion(index):
    """ Get motion Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
    app_config["events"]["port"])
    #client = KafkaClient(hosts=hostname)
    #topic = client.topics[str.encode(app_config["events"]["topics"])]
    client = KafkaClient(hosts='3.21.10.177:9092')
    topic = client.topics[str.encode('events')]
 # Here we reset the offset on start so that we retrieve
 # messages at the beginning of the message queue. 
 # To prevent the for loop from blocking, we set the timeout to
 # 100ms. There is a risk that this loop never stops if the
 # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, 
    consumer_timeout_ms=1000)
    logger.info("Retrieving motion at index %d" % index)
    counter = 0
    try:
        logger.info('this is the get for motion')
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if counter == index and msg['type'] == "motion":
                return msg , 200
            counter += 1 
    # Find the event at the index you want and 
       # return code 200
    # i.e., return event, 200
    except:
        logger.error("No more messages found")
 
        logger.error("Could not find motion at index %d" % index)
    return { "message": "Not Found"}, 404




app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS']= 'Content-Type'
app.add_api("audit.yaml",strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    app.run(port=8200)