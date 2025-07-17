# AbuseIPDB Nginx Blocker - Hypernode Edition

An efficient nginx blocker specifically designed for Hypernode servers that uses nginx's geo module to block IP addresses from the AbuseIPDB blocklist. This version can efficiently handle 240,000+ IP addresses without performance issues.

## Advantages of this approach

- **Performance**: Nginx geo module is optimized for large IP lists
- **Memory efficient**: Much faster than 300,000 individual deny rules
- **Security**: IP validation and filtering of private/reserved addresses
- **Reliability**: Automatic duplicate removal and file size limits (20MB max)
- **Automatic updates**: Can be configured for automatic updates every 4 hours
- **Atomic updates**: Safe configuration updates without downtime
- **Error handling**: Comprehensive error handling with automatic cleanup

## Requirements

- Hypernode server
- Python 3.6+ (available on Hypernode)
- Access to `/data/web/nginx/` directory (standard on Hypernode)

## ⚡ Quick Installation

One command installation (recommended):
```bash
curl -s https://raw.githubusercontent.com/hpowernl/AbuseIPDB-nginx-blocker/main/install.sh | sh
```

## Manual Installation

1. Download the script:
```bash
curl -o blocklist_updater.py https://raw.githubusercontent.com/hpowernl/AbuseIPDB-nginx-blocker/main/blocklist_updater.py
chmod +x blocklist_updater.py
```

2. Ensure the directory exists:
```bash
# Make sure /data/web/nginx/ exists and is writable
```

## Usage

### Initial configuration

Update the blocklist:
```bash
python3.11 blocklist_updater.py
```

The script uses fixed locations optimized for Hypernode servers and requires no additional options.

### Features

- **Automatic validation**: Filters out private, reserved, and invalid IP addresses
- **Duplicate removal**: Automatically removes duplicate entries
- **Safety limits**: 20MB download limit and 500,000 IP maximum
- **Robust error handling**: Detailed error messages and automatic cleanup
- **Atomic file operations**: Safe configuration updates without corruption risk

## Automation with Cron

Manual cron setup for automatic updates:
```bash
# Update every 4 hours
0 */4 * * * cd /path/to/script && python3.11 blocklist_updater.py >/dev/null 2>&1
```

For logging:
```bash
0 */4 * * * cd /path/to/script && python3.11 blocklist_updater.py >> /data/web/abuseipdb-blocker.log 2>&1
```

## Generated files

- `/data/web/nginx/http.abuseip` - Geo module configuration (284,712+ unique valid IPs)
- `/data/web/nginx/server.abuseip-block` - Blocking logic

The script automatically filters and validates all IP addresses, removing:
- Private IP ranges (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
- Reserved and loopback addresses
- Invalid IP addresses
- Duplicate entries

## Example geo configuration

```nginx
# AbuseIPDB Geo Configuration
# GitHub: https://github.com/hpowernl/AbuseIPDB-nginx-blocker
# Generated on: 2025-01-17T10:30:00
# Total blocked IPs: 284712

geo $blocked_ip {
    default 0;
    1.0.138.92 1;
    1.0.148.146 1;
    1.0.165.243 1;
    # ... more IPs
}
```

## Example block configuration

```nginx
# AbuseIPDB Block Configuration
# GitHub: https://github.com/hpowernl/AbuseIPDB-nginx-blocker
# This file uses the $blocked_ip variable from http.abuseip

# Block requests from IPs in the AbuseIPDB blocklist
if ($blocked_ip) {
    return 403 "Access denied - IP blocked by AbuseIPDB";
}
```

## Performance

The geo module offers excellent performance:
- O(log n) lookup time for IP matching
- Minimal memory usage
- Scales linearly with number of IPs
- Automatic IP deduplication reduces config size
- Sorted IP addresses for optimal nginx performance

### Performance Impact

nginx configuration test times:
- **Before**: `nginx -t` in 0.098s
- **After**: `nginx -t` in 0.302s (+0.204s)

The slight increase in configuration test time is acceptable for the protection of 280.000+ validated malicious IPs.

### Safety Features

- **Download limits**: 20MB maximum file size protection
- **Processing limits**: 500,000 IP maximum for safety
- **Memory efficient**: Streaming download with chunk processing
- **Validation**: Only valid public IPv4 addresses are included

## Troubleshooting

### Check logs
```bash
# Monitor nginx logs for any issues
tail -f /var/log/nginx/error.log

# Monitor script logs if using logging
tail -f /data/web/abuseipdb-blocker.log
```

### Configuration verification
Check if the generated files are correct:
```bash
ls -la /data/web/nginx/http.abuseip /data/web/nginx/server.abuseip-block
head /data/web/nginx/http.abuseip
wc -l /data/web/nginx/http.abuseip  # Check number of IPs
```

### Common Issues

**Permission denied**: Ensure `/data/web/nginx/` directory exists and is writable
**File too large**: The script limits downloads to 20MB for safety
**No IPs found**: Check internet connection and blocklist URL availability
**Invalid IPs skipped**: The script automatically filters invalid/private IPs

## Migration from old version

If you're using the old run.py version:

1. Backup current configuration
2. Install new version with one command: `curl -s https://raw.githubusercontent.com/hpowernl/AbuseIPDB-nginx-blocker/main/install.sh | sh`
3. Update blocklist: `python3.11 blocklist_updater.py`
4. Configure nginx includes
5. Reload nginx

The new version includes:
- **Better security**: IP validation and filtering
- **Improved reliability**: Error handling and atomic operations  
- **Enhanced performance**: Duplicate removal and optimized processing
- **Safety features**: File size limits and comprehensive validation

## Sources

- **AbuseIPDB list**: https://github.com/borestad/blocklist-abuseipdb
- **Nginx geo module**: http://nginx.org/en/docs/http/ngx_http_geo_module.html
- **Project repository**: https://github.com/hpowernl/AbuseIPDB-nginx-blocker

## License

[MIT](LICENSE) 