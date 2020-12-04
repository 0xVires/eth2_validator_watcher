# ETH2 Validator Watcher

Uses the beaconcha.in API to query your validator's balance. Stores it in a sqlite db.
If the current total balance is lower than the previously recorded balance, an alert is sent.
At midnight, the script sends a summary of today's and this week's earnings and APR.

Setup:
1) Create a telegram bot: https://core.telegram.org/bots#6-botfather
2) send "/start" to your bot and visit https://api.telegram.org/botXXX:YYYYY/getUpdates (replace XXX:YYYYY with your API Token). This will give you your chat_id.
3) Adjust the config of the python script:
  - List your validator indexes as a string - comma separated but without space inbetween!
  - Change the MY_TEL_ID and TEL_TOKEN to your values
4) Run the script as a cronjob every 15min (respects the rate limits of the API and the epoch length of 6.4min)
