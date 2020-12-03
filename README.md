# eth2_validator_watcher

Change the config accordingly! 
List the validator indexes as a string - comma separated but without space inbetween!

Uses the beaconcha.in API to query the validator's balance. Stores it in a sqlite db.
If the current balance is lower than the previously recorded balance, an alert is sent.
At midnight, the script sends a summary of today's and this week's earnings and APR.

Use crontrab to run the script every 15min (respects the rate limits of the API and the epoch length of 6.4min).
