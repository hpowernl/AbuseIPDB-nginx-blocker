
# AbuseIPDB Blacklist on a Hypernode server

This Python application checks your server logs for any suspicious IP addresses. 
It makes use of the AbuseIPDB API to check the abuse score of each IP. Any IP with an abuse score of 80 or above is added to a blacklist file.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/hpowernl/AbuseIPDB-nginx-blocker.git
```

2. Change into the directory:
```bash
cd AbuseIPDB-nginx-blocker
```

## Usage
1. You must first configure the application by modifying the `config.json` file. 
Provide your AbuseIPDB API key and set the maximum age of the reports you want to consider (in days).

2. Run the script:
```bash
python3 run.py
```
You can also specify the `--bots` argument to only check bot traffic:
```bash
python3 run.py --bots
```

## Cron
If you want to run this process in a cron, you can use the following:

1. Run `crontab -e` to open a crontab editor.
2. Now add the following to the last line: `*/30 * * * * cd /data/web/AbuseIPDB-nginx-blocker && /usr/bin/python3 run.py`
   
If you want to only check bot traffic in the cron, add the `--bots` argument:
```bash
*/30 * * * * cd /data/web/AbuseIPDB-nginx-blocker && /usr/bin/python3 run.py --bots
```
You can run it more frequently than every 30 minutes, but keep in mind that executing the hypernode-parse-nginx-log command can use a lot of resources.

## Features
- Scans your server logs for unique IP addresses.
- Can specifically check for bot traffic by using the `--bots` argument.
- Checks each IP against the AbuseIPDB to get its abuse confidence score.
- If the abuse score is 80 or above, the IP is added to a blacklist file.
- Caches checked IPs for 30 days to reduce the number of requests to the AbuseIPDB API.
- If the blacklist file doesn't exist, it is automatically created.

## License
[MIT](https://github.com/hpowernl/AbuseIPDB-nginx-blocker/blob/main/LICENSE)
