import requests
from time import sleep
import random
import yaml
from multiprocessing import Process
#import boto3
import json
import sqlalchemy
from sqlalchemy import text
from decouple import config


random.seed(100)


class AWSDBConnector:

    def __init__(self):
        creds_config_access = config('credentials_env')
        with open(creds_config_access, 'r') as db_creds:
            self.creds= yaml.safe_load(db_creds)

    def create_db_connector(self):
        engine = sqlalchemy.create_engine(f"mysql+pymysql://{self.creds['USER']}:{self.creds['PASSWORD']}@{self.creds['HOST']}:{self.creds['PORT']}/{self.creds['DATABASE']}?charset=utf8mb4")
        return engine

new_connector = AWSDBConnector()


def run_infinite_post_data_loop():
    while True:
        sleep(random.randrange(0, 2))
        random_row = random.randint(0, 11000)
        engine = new_connector.create_db_connector()

        with engine.connect() as connection:

            pin_string = text(f"SELECT * FROM pinterest_data LIMIT {random_row}, 1")
            pin_selected_row = connection.execute(pin_string)
            
            for row in pin_selected_row:
                pin_result = dict(row._mapping)

            geo_string = text(f"SELECT * FROM geolocation_data LIMIT {random_row}, 1")
            geo_selected_row = connection.execute(geo_string)
            
            for row in geo_selected_row:
                geo_result = dict(row._mapping)

            user_string = text(f"SELECT * FROM user_data LIMIT {random_row}, 1")
            user_selected_row = connection.execute(user_string)
            
            for row in user_selected_row:
                user_result = dict(row._mapping)
            
            print(pin_result)
            print(geo_result)
            print(user_result)


if __name__ == "__main__":
    run_infinite_post_data_loop()
    print('Working')
    
    


