import requests
from prometheus_client import start_http_server, Gauge
from time import sleep

validators = [1111,1122,2345] # CHANGE THIS!

def get_balance(val_index):
    URL = "http://127.0.0.1:5052/eth/v1/beacon/states/head/validators/" + str(val_index)
    balance = request.get(URL).json()["data"]["balance"]
    return balance

guage = Gauge('eth2_validator_balance', 'ETH2 Validator Balance')
start_http_server(5074) # The port of the server, add this to the prometheus.yml file

while (True):
    total_balance = 0
    for val in validators:
        total_balance += int(get_balance(val))
    guage.set(total_balance/10**9)
    # One epoch
    sleep(384)