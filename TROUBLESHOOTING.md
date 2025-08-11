# V2Ray Client Troubleshooting Guide

## Issues Fixed

### 1. Connection Refused Errors
**Problem**: Some traffic was going direct instead of through the proxy, causing "connection refused" errors.

**Root Cause**: The routing configuration was not properly set up to route all external traffic through the proxy.

**Solution**: Updated the routing rules to ensure all traffic goes through the proxy by default, with only specific exceptions for private IPs and Chinese domains.

### 2. Improper Traffic Routing
**Problem**: The logs showed some domains being routed to direct instead of proxy.

**Root Cause**: Missing default routing rule to catch all traffic.

**Solution**: Added a catch-all rule: `{"type": "field", "network": "tcp,udp", "outboundTag": "proxy"}`

### 3. VLESS Configuration Issues
**Problem**: The VLESS parser wasn't handling the path parameter correctly.

**Solution**: Improved the VLESS parser to properly handle WebSocket paths and TLS fingerprint settings.

## How to Use

### Basic Usage
```bash
# Start with your VLESS link
python3 main.py --proxy "vless://..." --auto-download

# Test connection first
python3 main.py --proxy "vless://..." --auto-download --test-connection

# Use custom log level for debugging
python3 main.py --proxy "vless://..." --auto-download --log-level debug

# Disable TLS encryption if needed
python3 main.py --proxy "vless://..." --disable-tls --auto-download
```

### Custom Direct Domains
If you want certain domains to go direct instead of through the proxy:

```bash
python3 main.py --proxy "vless://..." --direct-domains example.com localhost
```

### Custom Port
To change the SOCKS proxy port:

```bash
python3 main.py --proxy "vless://..." --port 1088
```

## Testing Your Proxy

### 1. Connection Test
```bash
python3 main.py --proxy "vless://..." --test-connection
```

### 2. Full Proxy Test
```bash
# Start V2Ray in background
python3 main.py --proxy "vless://..." --auto-download &

# Test proxy functionality and speed
python3 test_proxy.py

# Stop V2Ray
pkill -f v2ray
```

### 3. Speed Test Details
The `test_proxy.py` script includes comprehensive speed testing:

- **Test Files**: Downloads 5MB, 10MB, and 25MB files from Cloudflare
- **Speed Calculation**: Measures download speed in Mbps
- **Results Display**: Shows average, maximum, and minimum speeds
- **Speed Rating**: 
  - 🚀 Excellent: 50+ Mbps
  - ⚡ Good: 25-50 Mbps
  - 📶 Fair: 10-25 Mbps
  - 🐌 Slow: 5-10 Mbps
  - ❌ Very Slow: <5 Mbps

## Common Issues and Solutions

### Issue: "connection refused" errors
**Solution**: 
1. Use `--test-connection` to verify the proxy is working
2. Check that your proxy link is correct
3. Ensure the proxy server is online
4. Use `--log-level debug` for detailed logging

### Issue: Some websites not loading
**Solution**:
1. Check if the domain should go direct (use `--direct-domains`)
2. Verify the routing rules in the generated config.json
3. Check V2Ray logs for specific errors

### Issue: Proxy not accessible locally
**Solution**:
1. Make sure V2Ray started successfully
2. Check that ports 1080 (SOCKS) and 1081 (HTTP) are not blocked
3. Verify the configuration was generated correctly

### Issue: TLS/Encryption errors
**Solution**:
1. Try using `--disable-tls` option to remove encryption
2. Check if your server supports the security protocol being used
3. Verify SNI and fingerprint settings in your proxy link
4. Use `--log-level debug` to see detailed TLS error messages

## Configuration Details

The improved client now generates configurations with:

- **Proper routing**: All external traffic goes through proxy by default
- **Smart exceptions**: Private IPs and Chinese domains go direct
- **Ad blocking**: Built-in ad blocking via geosite rules
- **Flexible customization**: Easy to add custom direct/blocked domains

## Log Files

- `access.log`: V2Ray access logs
- `error.log`: V2Ray error logs
- Console output: Real-time V2Ray status

## Support

If you continue to have issues:

1. Run with `--log-level debug`
2. Check the generated `config.json` file
3. Verify your proxy link format
4. Test with `--test-connection` first
5. Check V2Ray logs for specific error messages 