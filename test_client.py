#!/usr/bin/env python3
"""
Test script for V2Ray Client
"""

import os
import sys
import json
from core.config_manager import ConfigManager
from core.parser import parse_vmess_link, parse_vmess_url
from core.downloader import V2RayDownloader

def test_config_manager():
    """Test configuration manager"""
    print("Testing ConfigManager...")
    
    config = ConfigManager("test_config.json")
    
    # Test default config
    assert "inbounds" in config.config
    assert "outbounds" in config.config
    print("✓ Default configuration loaded")
    
    # Test outbound setting
    test_outbound = {
        "protocol": "vmess",
        "settings": {
            "vnext": [{
                "address": "test.example.com",
                "port": 443,
                "users": [{"id": "test-id"}]
            }]
        }
    }
    
    config.set_outbound(test_outbound)
    assert len(config.config["outbounds"]) > 0
    print("✓ Outbound configuration set")
    
    # Test validation
    assert config.validate()
    print("✓ Configuration validation passed")
    
    # Test save/load
    config.save()
    assert os.path.exists("test_config.json")
    print("✓ Configuration saved")
    
    # Cleanup
    os.remove("test_config.json")
    print("✓ ConfigManager tests passed\n")
    return True

def test_parser():
    """Test proxy link parser"""
    print("Testing Proxy Parser...")

    # Test basic vmess link
    test_vmess = "vmess://eyJhZGQiOiJ0ZXN0LmV4YW1wbGUuY29tIiwiYWlkIjoiMCIsImlkIjoiMTIzNDU2Nzg5MCIsInBvcnQiOiI0NDMiLCJ0bHMiOiJ0bHMiLCJ0eXBlIjoibm9uZSJ9"

    try:
        from core.parser import parse_proxy_url
        outbound = parse_proxy_url(test_vmess)
        assert outbound["protocol"] == "vmess"
        assert "settings" in outbound
        print("✓ Basic vmess link parsing passed")
    except Exception as e:
        print(f"✗ Basic vmess link parsing failed: {e}")
        return False

    # Test vless link
    test_vless = "vless://aa6fdaa6-5d69-48c6-96a7-45a3303da611@snapp.mumumumumu.ir:443?encryption=none&security=tls&sni=snapp.mumumumumu.ir&alpn=h3%2Ch2%2Chttp%2F1.1&fp=chrome&allowInsecure=1&type=ws&path=%2F"
    
    try:
        outbound = parse_proxy_url(test_vless)
        assert outbound["protocol"] == "vless"
        assert "settings" in outbound
        print("✓ Basic vless link parsing passed")
    except Exception as e:
        print(f"✗ Basic vless link parsing failed: {e}")
        return False

    # Test invalid link
    try:
        parse_proxy_url("invalid://link")
        print("✗ Invalid link should have failed")
        return False
    except ValueError:
        print("✓ Invalid link correctly rejected")

    print("✓ Proxy Parser tests passed\n")
    return True

def test_downloader():
    """Test downloader functionality"""
    print("Testing V2Ray Downloader...")
    
    downloader = V2RayDownloader(extract_path="./test_bin")
    
    # Test platform detection
    assert hasattr(downloader, 'system')
    assert hasattr(downloader, 'arch')
    print("✓ Platform detection working")
    
    # Test asset key generation
    try:
        asset_key = downloader._get_asset_key()
        print(f"✓ Asset key generated: {asset_key}")
    except Exception as e:
        print(f"✗ Asset key generation failed: {e}")
        return False
    
    # Test release info fetching (skip if no internet)
    try:
        release_info = downloader.get_latest_release_info()
        assert "assets" in release_info
        print("✓ Release info fetching working")
    except Exception as e:
        print(f"⚠ Release info fetching failed (no internet?): {e}")
    
    print("✓ V2Ray Downloader tests passed\n")
    return True

def main():
    """Run all tests"""
    print("Running V2Ray Client Tests\n")
    print("=" * 40)
    
    tests = [
        test_config_manager,
        test_parser,
        test_downloader
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")
    
    print("=" * 40)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 