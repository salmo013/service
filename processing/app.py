#new processing service python file
import connexion, json, os
import requests
import yaml
import logging
import logging.config
import datetime 
from connexion import NoContent
from apscheduler.schedulers.background import BackgroundScheduler
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

EVENT_FILE = app_config['datastore']['filename']

now = datetime.datetime.now()
time_string = now.strftime('%Y-%m-%dT%H:%M:%SZ')
timestamp_datetime = datetime.datetime.strptime(time_string,"%Y-%m-%dT%H:%M:%SZ")



def populate_stats():

    """ Periodically update stats """
    logger.info(f'Start processing')
    #if os.path.isfile(EVENT_FILE):
    if os.path.exists(EVENT_FILE):
        print('file exists')
        with open(EVENT_FILE) as jsonFile:
            jsonObject = json.load(jsonFile)
        last_updated = jsonObject[0]['Last_update']
        logger.info(f'{last_updated} taken from the start of processing')
        total1 = jsonObject[0]['Total of event 1']
        total2 = jsonObject[0]['Total of event 2']
        logger.info(f'value to add{total2}')
    else:
        spec_yaml= 'inmotion.yaml'
        with open(spec_yaml, 'r') as f:
            data = yaml.load(f)
            stats_dict = data['components']['schemas']['ReadingStats']['properties']
            example_stats = {}
            for items in stats_dict:
                example_stats[items] = stats_dict[items]['example']
                #print(items,' ',stats_dict[items]['example'])
            last_updated = example_stats['Last_update']
            total1 = example_stats['Total of event 1']
            total2 = example_stats['Total of event 2']

    # current time parameter
    now = datetime.datetime.now()
    time_string = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {'timestamp': last_updated, 'endtimestamp_datetime': time_string}
    # get requests from door motion
    response = requests.get(app_config['eventstore']['url'],params = params )

    #get requests from movement motion
    response2 = requests.get(app_config['eventstore1']['url'],params = params )
    # calculate the events recieved
    logger.info(f'Log Conf File: {total1} + {len(response.json())}##############################################')
    total1 += len(response.json())
    total2 += len(response2.json())
    logger.info(f'events recieved {total1 + total2}')
    #print(response.json())
    if response.status_code != 200:
        # log status code error
        logger.error('error in application', response.status_code)
    else:
        dicts = response.json()
        dicts1 = response2.json()
        # how many times the couch was sit on
        value = list(filter(lambda dicts: dicts['location'] == 'Couch', dicts ))
        value1 = list(filter(lambda dicts1: dicts1['action'] == True , dicts1 ))
        # how many doors are left open
        
        
        jsonobj =[{'Total of event 1': total1, 'Total of event 2': total2 ,'Couch sits': len(value),'Door open': len(value1), 'Last_update': time_string }]

        # writing to the file
        json_object = json.dumps(jsonobj, indent = 4)

        # write if statement
        if total1 + total2 > 0:
            with open(EVENT_FILE, "w") as outfile:
                outfile.write(json_object)
                logger.debug(json_object)
               

        logger.info('end of processing')
        
        
        



def get_stats():
    #logger.info('################request processing####################')
    #if os.path.isfile(EVENT_FILE):
    if os.path.exists(EVENT_FILE):
        #print('file exists')
        with open(EVENT_FILE, 'r') as jsonFile:
            
            now = datetime.datetime.now()
            time_string = now.strftime('%Y-%m-%dT%H:%M:%SZ')
            timestamp_datetime = datetime.datetime.strptime(time_string,"%Y-%m-%dT%H:%M:%SZ")

            jsonObject = json.load(jsonFile)
            response_dict = {'Total of event 1':jsonObject[0]['Total of event 1'] , 'Total of event 2': jsonObject[0]['Total of event 2'] ,'Couch sits': jsonObject[0]['Couch sits'],'Doors open': jsonObject[0]['Door open'] , 'Last_update': jsonObject[0]['Last_update']}
            logger.info('request has completed') 
            logger.info(f'{jsonObject}')
            return response_dict, 200 
             
    else:
        error = "file does not exist"
        return error , 404 
    #return response_dict, 200



def init_scheduler():
   sched = BackgroundScheduler(daemon=True)
   sched.add_job(populate_stats, 
                     'interval',
                      seconds=app_config['scheduler']['period_sec'])
   sched.start()




app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS']= 'Content-Type'

app.add_api("inmotion.yaml", base_path="/processing",strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)

