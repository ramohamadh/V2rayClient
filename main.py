#!/usr/bin/env python3
"""
V2Ray Client - A Python client for V2Ray proxy
"""

import argparse
import os
import sys
import logging
import signal
from pathlib import Path
from core.config_manager import ConfigManager
from core.parser import parse_proxy_url
from core.runner import V2RayRunner
from core.downloader import V2RayDownloader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class V2RayClient:
    def __init__(self, config_path: str = "config.json", v2ray_path: str = "./bin/v2ray"):
        self.config_path = config_path
        self.v2ray_path = v2ray_path
        self.config_manager = None
        self.runner = None
        
    def setup(self, proxy_link: str, auto_download: bool = True):
        """Setup V2Ray client with proxy link (vmess:// or vless://)"""
        try:
            # Parse proxy link
            logger.info("Parsing proxy link...")
            outbound = parse_proxy_url(proxy_link)
            
            logger.info(f"Parsed {outbound['protocol']} link successfully")
            
            # Setup configuration
            self.config_manager = ConfigManager(self.config_path)
            self.config_manager.set_outbound(outbound)
            
            # Validate configuration
            if not self.config_manager.validate():
                raise RuntimeError("Invalid configuration generated")
            
            # Save configuration
            self.config_manager.save()
            self.config_manager.print_summary()
            
            # Check if v2ray binary exists
            if not os.path.exists(self.v2ray_path) and auto_download:
                logger.info("V2Ray binary not found, downloading...")
                self._download_v2ray()
            elif not os.path.exists(self.v2ray_path):
                raise FileNotFoundError(f"V2Ray binary not found at {self.v2ray_path}")
            
            # Setup runner
            self.runner = V2RayRunner(self.v2ray_path, self.config_path)
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise
    
    def _download_v2ray(self):
        """Download V2Ray binary"""
        try:
            downloader = V2RayDownloader(extract_path="./bin")
            binary_path = downloader.download_and_extract()
            self.v2ray_path = binary_path
            logger.info(f"V2Ray downloaded to {binary_path}")
        except Exception as e:
            logger.error(f"Failed to download V2Ray: {e}")
            raise
    
    def start(self):
        """Start V2Ray client"""
        if not self.runner:
            raise RuntimeError("Client not setup. Call setup() first.")
        
        try:
            logger.info("Starting V2Ray...")
            self.runner.start()
            
            # Print connection info
            print("\n" + "="*50)
            print("V2Ray Client Started Successfully!")
            print("="*50)
            print(f"SOCKS Proxy: 127.0.0.1:1080")
            print(f"HTTP Proxy: 127.0.0.1:1081")
            print("="*50)
            print("Press Ctrl+C to stop")
            print("="*50 + "\n")
            
            # Wait for user interrupt
            try:
                while self.runner.is_running():
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received stop signal")
                
        except Exception as e:
            logger.error(f"Failed to start V2Ray: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop V2Ray client"""
        if self.runner:
            self.runner.stop()
            logger.info("V2Ray stopped")
    
    def status(self):
        """Get client status"""
        if not self.runner:
            return {"status": "not_setup"}
        
        status = self.runner.get_status()
        if status["status"] == "running":
            # Add proxy info
            status["proxy"] = {
                "socks": "127.0.0.1:1080",
                "http": "127.0.0.1:1081"
            }
        return status

def signal_handler(signum, frame):
    """Handle system signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="V2Ray Client - A Python client for V2Ray proxy (supports vmess:// and vless://)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --proxy "vmess://..." --auto-download
  %(prog)s --proxy "vless://..." --auto-download
  %(prog)s --proxy "vmess://..." --config myconfig.json
  %(prog)s --status
        """
    )
    
    parser.add_argument("--proxy", help="proxy link to connect to (vmess:// or vless://)")
    parser.add_argument("--config", help="path to config.json", default="config.json")
    parser.add_argument("--v2ray", help="path to v2ray binary", default="./bin/v2ray")
    parser.add_argument("--auto-download", action="store_true", 
                       help="automatically download V2Ray binary if not found")
    parser.add_argument("--status", action="store_true", help="show client status")
    parser.add_argument("--log-level", choices=["debug", "info", "warning", "error"], 
                       default="info", help="set log level")
    parser.add_argument("--port", type=int, help="set SOCKS proxy port (default: 1080)")
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        client = V2RayClient(args.config, args.v2ray)
        
        if args.status:
            # Show status
            status = client.status()
            print("V2Ray Client Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            return
        
        if not args.proxy:
            parser.error("--proxy is required unless using --status")
        
        # Setup client
        client.setup(args.proxy, args.auto_download)
        
        # Set custom port if specified
        if args.port:
            client.config_manager.set_inbound_port(args.port)
            client.config_manager.save()
            logger.info(f"Set SOCKS proxy port to {args.port}")
        
        # Start client
        client.start()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()