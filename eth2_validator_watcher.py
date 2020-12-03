import requests
import json
import time
import datetime
import sqlite3

###
# CONFIG - CHANGE ACCORDINGLY
### 
db = "validator_data.db"
my_validators = "1111,1115,2121" # List your validator by index. Comma separated but NO SPACE.

# Telegram
MY_TEL_ID = 1111111 # Your telegram ID, google if you don't know how to get it
TEL_TOKEN = "11111111111:AABBBBCCCC" # Change to your API Token
TEL_URL = "https://api.telegram.org/bot{}/".format(TEL_TOKEN)
###

conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

# Create table if it does not exist already
c.execute("""CREATE TABLE IF NOT EXISTS validators (
            timestamp timestamp,
            validator integer,
            balance integer    
            )""")
conn.commit()

def get_data():
    BEACON_API = "https://beaconcha.in/api/v1/validator/"
    return requests.get(BEACON_API+my_validators).json()["data"]
    
def get_previous_balance(validator):
    c.execute("""SELECT 
                    balance
                FROM 
                    validators
                WHERE
                    validator = ?
                ORDER BY 
                    timestamp
                DESC""", (validator,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        return None

def is_between_0000_and_0010(timestamp):
    start = datetime.time(0, 0)
    end = datetime.time(0, 10)
    now = datetime.time(timestamp.hour, timestamp.minute)
    if start <= now <= end: 
        return True
    else:
        return False

def n_days_ago(n_days):
    """Get the date in the format Year-Month-Day (e.g. 2020-12-02) n days ago"""
    n_days_ago = datetime.datetime.now()-datetime.timedelta(days=n_days)
    return n_days_ago.strftime("%Y-%m-%d")
            
def get_initial_balance_of_date(date):
    """Get the inital total balance of all validators of a date.
    The date has to be in the format %Y-%m-%d (e.g. 2020-12-02)"""
    num_validators = len(my_validators.split(","))
    total = 0
    c.execute("""SELECT 
                    balance
                FROM 
                    validators
                WHERE
                    DATE(timestamp) = ?
                LIMIT
                    ?""", (date, num_validators))
    for i in c.fetchall():
        total += i[0]
    return total

def get_increase_and_APR(n_days):
    """Gets the APR based on data from the previous n days.
    n_days has to be at least 1.
    """
    inital_balance = get_initial_balance_of_date(n_days_ago(n_days))
    if inital_balance > 0:
        increase = total_balance - inital_balance
        # Since we query shortly after midnight, we take the initial balance of the previous day
        if n_days == 1:
            multiplier = 365
        else:
            multiplier = 365/(n_days-1)
        APR = str(round(increase/inital_balance*multiplier*100,2))+"%"
        increase = str(round(increase/10**9,4))+" ETH"
        return increase, APR
    else:
        increase, APR = "not enough data", "not enough data"
        return increase, APR
    
# Telegram - send message
def send_telegram(text, chat_id):
    sendURL = TEL_URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown&disable_web_page_preview=True".format(text, chat_id)
    try:
        requests.get(sendURL)
    except Exception as ex:
        print(ex)
    
def check_balance_and_record(data):
    """Gets the balance of every validator and compares it with t"""
    timestamp = datetime.datetime.now()
    total_balance = 0
    for val in data:
        validator = val["validatorindex"]
        balance = val["balance"]
        # If a previous entry exists, check if balance increased, notify if not
        if get_previous_balance(validator):
            diff = balance - get_previous_balance(validator)
            if not diff > 0:
                message = f"WARNING! The balance of validator {validator} decreased by" \
                          f"{str(round(diff/10**9,2))} ETH during the last 15min!"
                send_telegram(message, MY_TEL_ID)
                time.sleep(1)
        # Insert balances into db
        with conn:
            c.execute("INSERT INTO validators VALUES (?, ?, ?)", (timestamp, validator, balance))
        # Record total balance for end of day reporting
        total_balance += balance        
    if is_between_0000_and_0010(timestamp):
        # since function runs after midnight, substract +1 day
        d_increase, d_APR = get_increase_and_APR(1)
        w_increase, w_APR = get_increase_and_APR(8)
        message = f"Today's balance increase: {d_increase}\n" \
                  f"Weekly balance increase:  {w_increase}\n\n" \
                  f"APR (last 24h): {d_APR}\n" \
                  f"APR (last 7d):  {w_APR}"
        send_telegram(message, MY_TEL_ID)

def main():
    try:
        data = get_data()
        check_balance_and_record(data)
        conn.close()
    except Exception as ex:
        print(ex)
        send_telegram(ex, MY_TEL_ID)
        conn.close()

if __name__ == '__main__':
    main()