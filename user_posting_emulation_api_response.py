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
        engine= new_connector.create_db_connector()

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
            
            print("**************************************************\n")
            print("pin result: ", pin_result, "\n")
            print("geo result: ", geo_result, "\n")
            print("user result: ", user_result, "\n")

            pin_payload = json.dumps({
            "records": [
            {
            "value": {
                "index": pin_result["index"],
                "unique_id": pin_result["unique_id"],
                "title": pin_result["title"],
                "description": pin_result["description"],
                "poster_name": pin_result["poster_name"],
                "follower_count": pin_result["follower_count"],
                "tag_list": pin_result["tag_list"],
                "is_image_or_video": pin_result["is_image_or_video"],
                "image_src": pin_result["image_src"],
                "downloaded": pin_result["downloaded"],
                "save_location": pin_result["save_location"],
                "category": pin_result["category"]
                            }
                    }
                ]
            }, default=str)
            headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
            invoke_url_pin = "https://k2lim6ri8g.execute-api.us-east-1.amazonaws.com/staging/topics/123d7d4a88ef.pin"
            pin_response = requests.request("POST", invoke_url_pin, headers=headers, data=pin_payload)
            print("pin status code: ", pin_response.status_code, "\n")


            geo_payload = json.dumps({
            "records": [
            {
                "value": {
                "ind":geo_result["ind"],
                "timestamp":geo_result["timestamp"],
                "latitude":geo_result["latitude"],
                "longitude":geo_result["longitude"],
                "country":geo_result["country"]
                        }
                    }
                ]
            }, default=str)
            headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
            invoke_url_geo = "https://k2lim6ri8g.execute-api.us-east-1.amazonaws.com/staging/topics/123d7d4a88ef.geo"
            geo_response = requests.request("POST", invoke_url_geo, headers=headers, data=geo_payload)
            print("pin status code: ", pin_response.status_code, "\n")

            user_payload = json.dumps({
            "records": [
                {
                    "value": {
                        "ind":user_result["ind"],
                        "first_name":user_result["first_name"],
                        "last_name":user_result["last_name"],
                        "age":user_result["age"],
                        "date_joined":user_result["date_joined"]
                            }
                    }
                ]
            }, default=str)
            headers = {'Content-Type': 'application/vnd.kafka.json.v2+json'}
            invoke_url_user = "https://k2lim6ri8g.execute-api.us-east-1.amazonaws.com/staging/topics/123d7d4a88ef.user"
            user_response = requests.request("POST", invoke_url_user, headers=headers, data=user_payload)
            print("pin status code: ", pin_response.status_code, "\n")

if __name__ == "__main__":
    new_connector = AWSDBConnector()
    run_infinite_post_data_loop()
    print('working')


