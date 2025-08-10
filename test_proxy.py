#!/usr/bin/env python3
"""
Test script to verify V2Ray proxy connection
"""

import requests
import socket
import socks
import time
import sys

def test_socks_proxy():
    """Test SOCKS proxy connection"""
    print("Testing SOCKS proxy connection...")
    
    # Test basic connectivity
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect(("127.0.0.1", 1080))
        sock.close()
        print("✓ SOCKS proxy is accessible")
        return True
    except Exception as e:
        print(f"✗ SOCKS proxy connection failed: {e}")
        return False

def test_http_proxy():
    """Test HTTP proxy connection"""
    print("Testing HTTP proxy connection...")
    
    proxies = {
        'http': 'http://127.0.0.1:1081',
        'https': 'http://127.0.0.1:1081'
    }
    
    try:
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        if response.status_code == 200:
            print("✓ HTTP proxy is working")
            print(f"  Your IP: {response.json().get('origin', 'unknown')}")
            return True
        else:
            print(f"✗ HTTP proxy returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ HTTP proxy test failed: {e}")
        return False

def test_websites():
    """Test access to various websites through proxy"""
    print("Testing website access through proxy...")
    
    # Configure requests to use SOCKS proxy
    session = requests.Session()
    session.proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
    
    test_sites = [
        "https://www.google.com",
        "https://www.youtube.com",
        "https://www.github.com",
        "https://httpbin.org/ip"
    ]
    
    for site in test_sites:
        try:
            print(f"  Testing {site}...")
            response = session.get(site, timeout=10)
            if response.status_code == 200:
                print(f"    ✓ {site} - OK")
            else:
                print(f"    ✗ {site} - Status: {response.status_code}")
        except Exception as e:
            print(f"    ✗ {site} - Error: {e}")

def main():
    print("V2Ray Proxy Test")
    print("=" * 50)
    
    # Wait a bit for V2Ray to start
    print("Waiting for V2Ray to start...")
    time.sleep(3)
    
    # Test basic connectivity
    if not test_socks_proxy():
        print("SOCKS proxy test failed. Make sure V2Ray is running.")
        sys.exit(1)
    
    print()
    
    # Test HTTP proxy
    test_http_proxy()
    
    print()
    
    # Test website access
    test_websites()
    
    print()
    print("Test completed!")

if __name__ == "__main__":
    main() 