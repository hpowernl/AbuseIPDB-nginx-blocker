# AbuseIPDB Blacklist Updater on a Hypernode server

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

## Features
- Scans your server logs for unique IP addresses.
- Checks each IP against the AbuseIPDB to get its abuse confidence score.
- If the abuse score is 80 or above, the IP is added to a blacklist file.
- Caches checked IPs for 30 days to reduce the number of requests to the AbuseIPDB API.
- If the blacklist file doesn't exist, it is automatically created.


## License
[MIT](https://choosealicense.com/licenses/mit/)
