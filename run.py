import os
import subprocess
import json
import requests
import time

CACHE_FILENAME = 'checked_ips.json'
BLACKLIST_FILENAME = '/data/web/nginx/server.block_80procent_abuseIP'
CACHE_EXPIRATION_SECONDS = 48 * 60 * 60  # 48 hours in seconds

def load_config():
    with open('config.json') as f:
        return json.load(f)

def get_recent_ips():
    command1 = ['/usr/bin/hypernode-parse-nginx-log', '--today', '--bots', '--fields', 'remote_addr']
    command2 = ['sort']
    command3 = ['uniq', '-c']
    command4 = ['sort', '-n']
    command5 = ['/usr/bin/awk', '{$1=""; print $0}']

    process1 = subprocess.Popen(command1, stdout=subprocess.PIPE)
    process2 = subprocess.Popen(command2, stdin=process1.stdout, stdout=subprocess.PIPE)
    process3 = subprocess.Popen(command3, stdin=process2.stdout, stdout=subprocess.PIPE)
    process4 = subprocess.Popen(command4, stdin=process3.stdout, stdout=subprocess.PIPE)
    process5 = subprocess.Popen(command5, stdin=process4.stdout, stdout=subprocess.PIPE)

    process1.stdout.close()  
    process2.stdout.close()  
    process3.stdout.close()
    process4.stdout.close()  
    stdout, stderr = process5.communicate()

    if process5.returncode != 0:
        raise Exception(f'Error executing command: {stderr.decode()}')

    return stdout.decode().split('\n')[-100:]

def ensure_blacklist_file_exists():
    if not os.path.exists(BLACKLIST_FILENAME):
        open(BLACKLIST_FILENAME, 'w').close()

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

def load_blacklist():
    with open(BLACKLIST_FILENAME, 'r') as f:
        return set(line.split()[1] for line in f if line.startswith("deny"))

def add_to_blacklist(ip):
    blacklist = load_blacklist()
    
    if ip not in blacklist:
        with open(BLACKLIST_FILENAME, 'a') as f:
            f.write(f"deny {ip};\n")

def load_checked_ips():
    if os.path.exists(CACHE_FILENAME):
        with open(CACHE_FILENAME, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_checked_ips(checked_ips):
    with open(CACHE_FILENAME, 'w') as f:
        json.dump(checked_ips, f)

def cleanup_checked_ips(checked_ips):
    current_time = time.time()

    for ip, added_time in list(checked_ips.items()):
        if current_time - added_time > CACHE_EXPIRATION_SECONDS:
            del checked_ips[ip]

    save_checked_ips(checked_ips)

def main():
    config = load_config()
    ensure_blacklist_file_exists()
    checked_ips = load_checked_ips()  

    for ip in get_recent_ips():
        if ip and ip not in checked_ips:  
            score = check_ip_abuse(config, ip)

            if score >= 80:
                add_to_blacklist(ip)
            
            checked_ips[ip] = time.time() 

    save_checked_ips(checked_ips) 
    cleanup_checked_ips(checked_ips)  

if __name__ == '__main__':
    main()
