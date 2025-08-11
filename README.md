# V2Ray Client

A Python-based V2Ray client that supports VMess and VLESS protocols with automatic binary download and configuration management.

## Features

- 🚀 **Multi-Protocol Support**: VMess and VLESS protocols
- 🔧 **Auto-Download**: Automatically downloads V2Ray binary for your platform
- 📝 **Smart Parsing**: Parses proxy links and generates proper V2Ray configurations
- 🛡️ **Reality Support**: Full support for Reality security protocol
- 🔌 **Multiple Proxies**: SOCKS (1080) and HTTP (1081) proxy support
- 📱 **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites
- Python 3.7+
- Git

### Quick Start
```bash
# Clone the repository
git clone https://github.com/ramohamadh/V2rayClient.git
cd V2rayClient

# Install dependencies
pip install -r requirements.txt

# Run the client
python3 main.py --proxy "your_proxy_link_here" --auto-download
```

## Usage

### Basic Usage
```bash
# Connect using a proxy link
python3 main.py --proxy "vmess://..." --auto-download

# Connect using a VLESS link
python3 main.py --proxy "vless://..." --auto-download

# Use custom config file
python3 main.py --proxy "vmess://..." --config myconfig.json

# Check status
python3 main.py --status
```

### Command Line Options
- `--proxy`: Proxy link (vmess:// or vless://)
- `--config`: Path to config file (default: config.json)
- `--v2ray`: Path to V2Ray binary (default: ./bin/v2ray)
- `--auto-download`: Automatically download V2Ray binary if not found
- `--status`: Show current client status
- `--log-level`: Set log level (debug, info, warning, error)
- `--port`: Set custom port for SOCKS proxy
- `--disable-tls`: Disable TLS encryption in proxy configuration
- `--direct-domains`: Domains that should go direct instead of through proxy

### Example Proxy Links

#### VMess
```
vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6IjEyMzQ1Njc4LTlhYzEtNDM0NS1iNzE0LTQ5ODc2NTQzMjEwYiIsIm5ldCI6IndzIiwicG9ydCI6IjQ0MyIsInBzIjoiZXhhbXBsZSIsInRscyI6InRscyIsInR5cGUiOiJub25lIiwidiI6IjIifQ==
```

#### VLESS with Reality
```
vless://e396992f-0c58-4c9c-8d6b-f3c6ddd6cf3c@91.99.152.11:2222?encryption=none&security=reality&sni=cp7.cloudflare.com&fp=chrome&pbk=YOUR_PUBLIC_KEY&sid=YOUR_SHORT_ID&spx=%2Fcdn%2Fimage.jpg&type=xhttp&path=%2F&mode=auto
```

## Configuration

The client automatically generates a `config.json` file with:
- SOCKS proxy on port 1080
- HTTP proxy on port 1081
- Proper routing rules
- Support for Reality security protocol

### Manual Configuration
You can manually edit the generated `config.json` file or use the `--config` option to specify a custom configuration.

## Project Structure

```
v2ray_client/
├── main.py              # Main entry point
├── core/
│   ├── config_manager.py # Configuration management
│   ├── parser.py         # Proxy link parsing
│   ├── runner.py         # V2Ray process management
│   └── downloader.py     # V2Ray binary downloader
├── bin/                  # V2Ray binary and data files
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Supported Protocols

### VMess
- All standard VMess configurations
- WebSocket, HTTP/2, TCP with HTTP disguise
- TLS support

### VLESS
- VLESS protocol with Reality security
- HTTP, WebSocket, TCP transport
- Full Reality protocol support (SNI, fingerprint, public key, etc.)

## TLS Configuration

### Disabling TLS
If you encounter TLS-related issues or want to use the proxy without encryption, you can disable TLS:

```bash
# Disable TLS encryption
python3 main.py --proxy "vless://..." --disable-tls --auto-download

# Test connection without TLS
python3 main.py --proxy "vless://..." --disable-tls --test-connection

# Disable TLS with custom port and debug logging
python3 main.py --proxy "vless://..." --disable-tls --port 1088 --log-level debug
```

### What Gets Disabled
When you use `--disable-tls`, the following security settings are removed:

**TLS Settings Removed:**
- `security: "tls"` - TLS security protocol
- `tlsSettings` - All TLS configuration (SNI, fingerprint, alpn, etc.)

**Reality Settings Removed:**
- `security: "reality"` - Reality security protocol  
- `realitySettings` - All Reality configuration (public key, short ID, etc.)

**What Remains:**
- Transport protocol settings (WebSocket, HTTP, TCP)
- Network configuration and path settings
- All other non-security related settings

### Use Cases for Disabling TLS:

1. **Testing and Debugging**
   - Troubleshoot connection issues
   - Test proxy functionality without encryption overhead
   - Debug server compatibility problems

2. **Server Compatibility**
   - Work with servers that don't support TLS
   - Connect to servers with misconfigured TLS settings
   - Bypass TLS-related connection errors

3. **Performance Optimization**
   - Reduce encryption overhead for faster connections
   - Improve connection speed on low-end devices
   - Minimize CPU usage

4. **Development and Learning**
   - Understand proxy behavior without encryption
   - Test different transport protocols
   - Learn about V2Ray configuration

### Security Considerations

⚠️ **Important Security Notes:**

- **Traffic is Unencrypted**: All data transmitted without TLS is unencrypted
- **Server Authentication**: Without TLS, you can't verify server identity
- **Privacy Implications**: Your browsing activity may be visible to network administrators

**Recommended Usage:**
- ✅ Testing and development environments
- ✅ Trusted private networks  
- ✅ Debugging connection issues
- ✅ Performance testing

- ❌ Public Wi-Fi networks
- ❌ Sensitive data transmission
- ❌ Production environments without additional security

**Note**: Disabling TLS will remove all security settings (TLS, Reality) from the configuration. Use only on trusted networks and for testing purposes.

### Example Configuration Changes

**Before (with TLS):**
```json
{
  "streamSettings": {
    "network": "ws",
    "security": "tls",
    "tlsSettings": {
      "serverName": "example.com",
      "fingerprint": "chrome"
    },
    "wsSettings": {
      "path": "/path",
      "headers": {"Host": "example.com"}
    }
  }
}
```

**After (TLS disabled):**
```json
{
  "streamSettings": {
    "network": "ws",
    "wsSettings": {
      "path": "/path", 
      "headers": {"Host": "example.com"}
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **V2Ray binary not found**
   - Use `--auto-download` flag
   - Check if the binary is executable: `chmod +x bin/v2ray`

2. **Configuration errors**
   - Verify your proxy link format
   - Check the generated `config.json` file
   - Use `--log-level debug` for detailed error messages

3. **Port already in use**
   - Change the port using `--port` option
   - Kill existing processes using the port

4. **TLS/Encryption issues**
   - Try using `--disable-tls` option
   - Check if your server supports the security protocol
   - Verify SNI and fingerprint settings
   - Test connection without TLS first: `--disable-tls --test-connection`
   - Check if server requires TLS (some servers only accept encrypted connections)

### Logs
- Access logs: `access.log`
- Error logs: `error.log`
- Set log level: `--log-level debug`

## Development

### Setting up development environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
python3 test_client.py
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [V2Ray](https://github.com/v2fly/v2ray-core) - The core proxy framework
- [V2Fly](https://github.com/v2fly) - Community-driven V2Ray edition

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

---

**Note**: This client is for educational and personal use. Please ensure you comply with your local laws and regulations regarding proxy usage. 
