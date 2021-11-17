import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from base import Base
from motion import Motion
from door_motion import DoorMotion
import datetime
import pymysql
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
import json
from threading import Thread
import time

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')



with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']

logger.info(f'Connecting to DB. Hostname:{hostname}, Port:{port}')
#DB_ENGINE = create_engine("sqlite:///readings.sqlite")
DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_motion_readings(timestamp,endtimestamp_datetime):
    session = DB_SESSION()
    logger.info(f'trying to get readings {timestamp}   {endtimestamp_datetime}######################################')
    timestamp_datetime = datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%SZ")
    #new line add LAB9
    endtimestamp_datetime = datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%SZ")
    # additional line
    readingsL = session.query(DoorMotion).filter(and_(DoorMotion.date_created >= timestamp_datetime, DoorMotion.date_created < endtimestamp_datetime ))
    #readings = session.query(DoorMotion).filter(DoorMotion.date_created > timestamp_datetime)
    results_list = []
    for reading in readingsL:
        results_list.append(reading.to_dict())
    print(results_list,"#####################################")
    # send one request
    #logger.info(f'{reading}###################################################')
    session.close()

    #logger.info("Query for Blood motion readings after %s returns %d results" %
    #(timestamp, len(results_list)))
    return results_list, 200

def get_move_motion_readings(timestamp,endtimestamp_datetime):
    session = DB_SESSION()
    logger.info(f'trying to get readings {timestamp}{endtimestamp_datetime}######################################')
    timestamp_datetime = datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%SZ")
    endtimestamp_datetime = datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%SZ")
    readingsL = session.query(Motion).filter(and_(Motion.date_created >= timestamp_datetime, Motion.date_created < endtimestamp_datetime))
    readings = session.query(Motion).filter(Motion.date_created > timestamp_datetime)
    results_list = []
    for reading in readingsL:
        results_list.append(reading.to_dict())
    logger.info(f'{results_list}###################################################')    
    #print(readings,"#####################################")
    # send one request
    session.close()

    #logger.info("Query for Blood motion readings after %s returns %d results" %
    #(timestamp, len(results_list)))
    return results_list, 200


def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
    app_config["events"]["port"])
    
    #lab 9 code###############################
    attempts = 0
    max_attempts = app_config['connection']['tries']
    while attempts < max_attempts:
        try: 
            client = KafkaClient(hosts='3.21.10.177:9092')
            topic = client.topics[str.encode('events')]
            logger.info(f'##################connected to kafka#####################')
            attempts = 15
        except:
            logger.error('failed to connect to kafka')
        time.sleep(15)
        attempts += 1
        logger.info(f'trying to connect to kafka, number of attempts = {attempts}')        
    #############################################
    #client = KafkaClient(hosts=hostname)
    #topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Create a consume on a consumer group, that only reads new messages # (uncommitted messages) when the service re-starts (i.e., it doesn't # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',reset_offset_on_start=False,auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        #logger.info("Message: %s" % msg)
        payload = msg["payload"]
        #logger.info(payload)
        if msg["type"] == "motion": # Change this to your event type
            #logger.info(payload)
            session = DB_SESSION()
            logger.info("Message: %s" % msg)
            mo = Motion(payload['location'],
                    payload['item'],
                    payload['time'],                    
                    payload['action'])

            session.add(mo)

            session.commit()
            session.close()
            # Store the event1 (i.e., the payload) to the DB
           
            #movementDetection(payload)
        elif msg["type"] == "doormotion": # Change this to your event type
            session = DB_SESSION()

            dmo = DoorMotion(payload['location'],
                   payload['item'],
                   payload['time'],
                   payload['state'])

            session.add(dmo)

            session.commit()
            session.close()
            #doorDetection(payload)
            # Store the event2 (i.e., the payload) to the DB
            # Commit the new message as being read
        consumer.commit_offsets()




app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("inmotion.yaml",strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    t1 = Thread(target= process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8999)
