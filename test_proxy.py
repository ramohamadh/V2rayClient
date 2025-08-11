#!/usr/bin/env python3
"""
Test script to verify V2Ray proxy connection and speed
"""

import requests
import socket
import socks
import time
import sys
import statistics

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

def test_speed():
    """Test download speed using Cloudflare speed test endpoints"""
    print("Testing download speed through proxy...")
    
    # Configure requests to use SOCKS proxy
    session = requests.Session()
    session.proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
    
    # Cloudflare speed test endpoints with different file sizes
    speed_test_urls = [
        ("https://speed.cloudflare.com/__down?bytes=25000000", "25MB"),  # 25MB
        ("https://speed.cloudflare.com/__down?bytes=10000000", "10MB"),  # 10MB
        ("https://speed.cloudflare.com/__down?bytes=5000000", "5MB"),    # 5MB
    ]
    
    results = []
    
    for url, size in speed_test_urls:
        try:
            print(f"  Testing {size} download...")
            start_time = time.time()
            
            response = session.get(url, timeout=30, stream=True)
            if response.status_code == 200:
                # Download the content
                content_length = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        content_length += len(chunk)
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Calculate speed in Mbps
                size_mb = content_length / (1024 * 1024)
                speed_mbps = (size_mb * 8) / duration
                
                results.append(speed_mbps)
                print(f"    ✓ {size}: {speed_mbps:.2f} Mbps ({duration:.2f}s)")
            else:
                print(f"    ✗ {size}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ✗ {size}: Error - {e}")
    
    # Calculate and display average speed
    if results:
        avg_speed = statistics.mean(results)
        max_speed = max(results)
        min_speed = min(results)
        
        print(f"\n  📊 Speed Test Results:")
        print(f"    Average: {avg_speed:.2f} Mbps")
        print(f"    Maximum: {max_speed:.2f} Mbps")
        print(f"    Minimum: {min_speed:.2f} Mbps")
        
        # Speed rating
        if avg_speed >= 50:
            rating = "🚀 Excellent"
        elif avg_speed >= 25:
            rating = "⚡ Good"
        elif avg_speed >= 10:
            rating = "📶 Fair"
        elif avg_speed >= 5:
            rating = "🐌 Slow"
        else:
            rating = "❌ Very Slow"
        
        print(f"    Rating: {rating}")
    else:
        print("  ❌ Speed test failed - no successful downloads")

def main():
    print("V2Ray Proxy Test & Speed Test")
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
    
    # Test speed
    test_speed()
    
    print()
    print("Test completed!")

if __name__ == "__main__":
    main() 