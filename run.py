import os
import subprocess
import json
import requests

def load_config():
    with open('config.json') as f:
        return json.load(f)

def get_recent_ips():
    command = ['/usr/bin/hypernode-parse-nginx-log', '--today', '--bots', '--fields', 'remote_addr']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception(f'Error executing pnl command: {stderr.decode()}')

    return stdout.decode().split('\n')[-100:]

def check_ip_abuse(config, ip):
    url = 'https://api.abuseipdb.com/api/v2/check'
    querystring = {
        'ipAddress': ip,
        'maxAgeInDays': config['DAYS']
    }
    headers = {
        'Accept': 'application/json',
        'Key': config['API_KEY']
    }

    response = requests.request(method='GET', url=url, headers=headers, params=querystring)
    response.raise_for_status()
    result = response.json()

    if not result or 'data' not in result or 'abuseConfidenceScore' not in result['data']:
        raise Exception(f'Error checking IP {ip}, response: {result}')

    return result['data']['abuseConfidenceScore']

def add_to_blacklist(ip):
    with open('/data/web/nginx/server.block_80procent_abuseIP', 'a') as f:
        f.write(f"deny {ip};\n")

def main():
    config = load_config()

    for ip in get_recent_ips():
        if ip:  # Skip empty IP addresses
            score = check_ip_abuse(config, ip)

            if score >= 80:
                add_to_blacklist(ip)


if __name__ == '__main__':
    main()
