#!/usr/bin/env python3
"""
AbuseIPDB Nginx Blocker - Hypernode Edition
Downloads and processes AbuseIPDB blocklist for efficient nginx blocking using geo module.
"""

import os
import requests
import tempfile
import shutil
import logging
import ipaddress
from datetime import datetime
from typing import List, Set
import re

# Configuration
BLOCKLIST_URL = "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-30d.ipv4"
NGINX_GEO_FILE = "/data/web/nginx/http.abuseip"
NGINX_BLOCK_FILE = "/data/web/nginx/server.abuseip-block"

# Limits for safety
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB max download
MAX_IPS = 500000  # Maximum number of IPs to process
TIMEOUT_SECONDS = 120  # Request timeout

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_blocklist() -> str:
    """Download the latest AbuseIPDB blocklist with safety limits."""
    logger.info(f"Downloading blocklist from {BLOCKLIST_URL}")
    
    try:
        response = requests.get(
            BLOCKLIST_URL, 
            timeout=TIMEOUT_SECONDS,
            stream=True
        )
        response.raise_for_status()
        
        # Check content length
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {content_length} bytes (max: {MAX_FILE_SIZE})")
        
        # Download with size limit
        content = b""
        for chunk in response.iter_content(chunk_size=8192):
            content += chunk
            if len(content) > MAX_FILE_SIZE:
                raise ValueError(f"Downloaded content exceeds size limit: {MAX_FILE_SIZE}")
        
        text_content = content.decode('utf-8', errors='ignore')
        logger.info(f"Downloaded {len(content)} bytes, {len(text_content.splitlines())} lines")
        return text_content
        
    except requests.RequestException as e:
        logger.error(f"Failed to download blocklist: {e}")
        raise
    except (ValueError, UnicodeDecodeError) as e:
        logger.error(f"Invalid content received: {e}")
        raise


def validate_ip_address(ip: str) -> bool:
    """Validate IP address format and ensure it's IPv4."""
    try:
        addr = ipaddress.IPv4Address(ip)
        # Exclude private/reserved ranges
        return not (addr.is_private or addr.is_reserved or addr.is_loopback)
    except ipaddress.AddressValueError:
        return False


def parse_blocklist(content: str) -> List[str]:
    """Parse the blocklist content and extract valid IP addresses."""
    ips: Set[str] = set()  # Use set to automatically handle duplicates
    lines = content.strip().split('\n')
    
    if len(lines) > MAX_IPS * 2:  # Conservative estimate with comments
        logger.warning(f"Large file detected: {len(lines)} lines")
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Extract IP address (everything before the first space or #)
        ip_match = re.match(r'^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', line)
        if ip_match:
            ip = ip_match.group(1)
            if validate_ip_address(ip):
                ips.add(ip)
            else:
                logger.debug(f"Skipped invalid/private IP on line {line_num}: {ip}")
        
        # Safety check for excessive processing
        if len(ips) > MAX_IPS:
            logger.warning(f"Reached maximum IP limit: {MAX_IPS}")
            break
    
    # Convert back to sorted list for consistent output
    ip_list = sorted(ips, key=lambda x: ipaddress.IPv4Address(x))
    logger.info(f"Parsed {len(ip_list)} unique valid IP addresses")
    return ip_list


def create_geo_config(ips: List[str]) -> str:
    """Create nginx geo module configuration efficiently."""
    if not ips:
        raise ValueError("No IP addresses to configure")
    
    header = f"""# AbuseIPDB Geo Configuration
# GitHub: https://github.com/hpowernl/AbuseIPDB-nginx-blocker
# Generated on: {datetime.now().isoformat()}
# Total blocked IPs: {len(ips)}

geo $blocked_ip {{
    default 0;
"""
    
    footer = "}\n"
    
    # Use list comprehension for better performance
    ip_entries = [f"    {ip} 1;" for ip in ips]
    
    return header + '\n'.join(ip_entries) + '\n' + footer


def create_block_config() -> str:
    """Create nginx blocking configuration that uses the geo variable."""
    return """# AbuseIPDB Block Configuration
# GitHub: https://github.com/hpowernl/AbuseIPDB-nginx-blocker
# This file uses the $blocked_ip variable from http.abuseip

# Block requests from IPs in the AbuseIPDB blocklist
if ($blocked_ip) {
    return 403 "Access denied - IP blocked by AbuseIPDB";
}
"""


def write_config_files(geo_content: str, block_content: str) -> None:
    """Write the configuration files atomically with proper cleanup."""
    # Check if target directories exist
    geo_dir = os.path.dirname(NGINX_GEO_FILE)
    block_dir = os.path.dirname(NGINX_BLOCK_FILE)
    
    for directory in [geo_dir, block_dir]:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Target directory {directory} does not exist")
        if not os.access(directory, os.W_OK):
            raise PermissionError(f"No write permission for directory {directory}")
    
    temp_geo_path = None
    temp_block_path = None
    
    try:
        # Write geo configuration
        with tempfile.NamedTemporaryFile(
            mode='w', 
            delete=False, 
            dir=geo_dir,
            prefix='.tmp.http.abuseip.',
            suffix='.conf'
        ) as temp_geo:
            temp_geo.write(geo_content)
            temp_geo_path = temp_geo.name
        
        # Write block configuration  
        with tempfile.NamedTemporaryFile(
            mode='w', 
            delete=False,
            dir=block_dir,
            prefix='.tmp.server.abuseip-block',
            suffix='.conf'
        ) as temp_block:
            temp_block.write(block_content)
            temp_block_path = temp_block.name
        
        # Atomic moves
        shutil.move(temp_geo_path, NGINX_GEO_FILE)
        shutil.move(temp_block_path, NGINX_BLOCK_FILE)
        
        logger.info("Configuration files written successfully")
        
    except Exception as e:
        # Cleanup temporary files on failure
        for temp_path in [temp_geo_path, temp_block_path]:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass  # Best effort cleanup
        raise


def main() -> int:
    """Main function with comprehensive error handling."""
    try:
        # Download and parse blocklist
        content = download_blocklist()
        ips = parse_blocklist(content)
        
        if not ips:
            logger.error("No valid IP addresses found in blocklist")
            return 1
        
        # Generate configurations
        geo_config = create_geo_config(ips)
        block_config = create_block_config()
        
        # Write new configuration
        write_config_files(geo_config, block_config)
        
        logger.info(f"Successfully updated blocklist with {len(ips)} IP addresses")
        
        return 0
        
    except (requests.RequestException, ValueError, UnicodeDecodeError) as e:
        logger.error(f"Download/parsing error: {e}")
        return 1
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f"File system error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    exit(main()) 