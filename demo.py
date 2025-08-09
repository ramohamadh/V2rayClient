#!/usr/bin/env python3
"""
Demo script for V2Ray Client
Shows how to use the client programmatically
"""

import time
import logging
from core.config_manager import ConfigManager
from core.parser import parse_vmess_link
from core.runner import V2RayRunner
from core.downloader import V2RayDownloader

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def demo_config_manager():
    """Demonstrate configuration management"""
    print("=== Configuration Manager Demo ===")
    
    # Create config manager
    config = ConfigManager("demo_config.json")
    
    # Show default configuration
    print("Default configuration:")
    print(f"  Inbounds: {len(config.config.get('inbounds', []))}")
    print(f"  Outbounds: {len(config.config.get('outbounds', []))}")
    
    # Create a sample vmess outbound
    sample_outbound = {
        "protocol": "vmess",
        "settings": {
            "vnext": [{
                "address": "demo.example.com",
                "port": 443,
                "users": [{
                    "id": "demo-user-id",
                    "alterId": 0,
                    "security": "auto"
                }]
            }]
        },
        "streamSettings": {
            "network": "ws",
            "wsSettings": {
                "path": "/demo"
            }
        }
    }
    
    # Set the outbound
    config.set_outbound(sample_outbound)
    
    # Save configuration
    config.save()
    
    # Show summary
    config.print_summary()
    print()

def demo_parser():
    """Demonstrate proxy link parsing"""
    print("=== Proxy Link Parser Demo ===")
    
    from core.parser import parse_proxy_url
    
    # Demo vmess link
    vmess_link = "vmess://eyJhZGQiOiJ0ZXN0LmV4YW1wbGUuY29tIiwiYWlkIjoiMCIsImlkIjoiMTIzNDU2Nzg5MCIsInBvcnQiOiI0NDMiLCJ0bHMiOiJ0bHMiLCJ0eXBlIjoibm9uZSJ9"
    print(f"Parsing vmess link: {vmess_link[:50]}...")
    
    try:
        vmess_outbound = parse_proxy_url(vmess_link)
        print(f"✓ VMess parsed successfully: {vmess_outbound['protocol']}")
        print(f"  Address: {vmess_outbound['settings']['vnext'][0]['address']}")
        print(f"  Port: {vmess_outbound['settings']['vnext'][0]['port']}")
    except Exception as e:
        print(f"✗ VMess parsing failed: {e}")
    
    # Demo vless link
    vless_link = "vless://aa6fdaa6-5d69-48c6-96a7-45a3303da611@snapp.mumumumumu.ir:443?encryption=none&security=tls&sni=snapp.mumumumumu.ir&alpn=h3%2Ch2%2Chttp%2F1.1&fp=chrome&allowInsecure=1&type=ws&path=%2F"
    print(f"\nParsing vless link: {vless_link[:50]}...")
    
    try:
        vless_outbound = parse_proxy_url(vless_link)
        print(f"✓ VLESS parsed successfully: {vless_outbound['protocol']}")
        print(f"  Address: {vless_outbound['settings']['vnext'][0]['address']}")
        print(f"  Port: {vless_outbound['settings']['vnext'][0]['port']}")
        print(f"  Encryption: {vless_outbound['settings']['vnext'][0]['users'][0]['encryption']}")
        if 'streamSettings' in vless_outbound:
            print(f"  Network: {vless_outbound['streamSettings'].get('network', 'tcp')}")
            if vless_outbound['streamSettings'].get('security') == 'tls':
                print(f"  TLS: {vless_outbound['streamSettings']['tlsSettings'].get('serverName', 'N/A')}")
    except Exception as e:
        print(f"✗ VLESS parsing failed: {e}")
    
    print()

def demo_downloader():
    """Demonstrate V2Ray downloader"""
    print("=== V2Ray Downloader Demo ===")
    
    downloader = V2RayDownloader(extract_path="./demo_bin")
    
    print(f"Platform: {downloader.system} {downloader.arch}")
    
    # Get asset key for current platform
    try:
        asset_key = downloader._get_asset_key()
        print(f"Asset key: {asset_key}")
    except Exception as e:
        print(f"Failed to get asset key: {e}")
    
    # Check for updates (without downloading)
    try:
        has_update, latest_version = downloader.check_update()
        if has_update:
            print(f"Update available: {latest_version}")
        else:
            print("V2Ray is up to date")
    except Exception as e:
        print(f"Could not check for updates: {e}")
    
    print()

def demo_runner():
    """Demonstrate V2Ray runner (without actually starting)"""
    print("=== V2Ray Runner Demo ===")
    
    # Create a sample configuration for demo
    config = ConfigManager("demo_runner_config.json")
    
    sample_outbound = {
        "protocol": "vmess",
        "settings": {
            "vnext": [{
                "address": "demo.example.com",
                "port": 443,
                "users": [{"id": "demo-id"}]
            }]
        }
    }
    
    config.set_outbound(sample_outbound)
    config.save()
    
    # Create runner (but don't start it)
    runner = V2RayRunner("./demo_bin/v2ray", "demo_runner_config.json")
    
    print("Runner created successfully")
    print(f"Status: {runner.get_status()}")
    
    # Cleanup demo files
    import os
    if os.path.exists("demo_runner_config.json"):
        os.remove("demo_runner_config.json")
    
    print()

def main():
    """Run all demos"""
    print("V2Ray Client Demo\n")
    
    try:
        demo_config_manager()
        demo_parser()
        demo_downloader()
        demo_runner()
        
        print("=== Demo Completed Successfully! ===")
        print("\nTo use the client with a real vmess link:")
        print("python3 main.py --vmess 'vmess://...' --auto-download")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 