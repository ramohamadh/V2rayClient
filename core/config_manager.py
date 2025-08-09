import json
import os
from typing import Dict, Any, List, Optional

DEFAULT_CONFIG = {
    "log": {
        "loglevel": "warning",
        "access": "access.log",
        "error": "error.log"
    },
    "inbounds": [
        {
            "port": 1080,
            "listen": "127.0.0.1",
            "protocol": "socks",
            "settings": {
                "auth": "noauth",
                "udp": True,
                "ip": "127.0.0.1"
            },
            "sniffing": {
                "enabled": True,
                "destOverride": ["http", "tls"]
            }
        },
        {
            "port": 1081,
            "listen": "127.0.0.1",
            "protocol": "http",
            "settings": {
                "timeout": 300
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "settings": {}
        },
        {
            "protocol": "blackhole",
            "tag": "block",
            "settings": {}
        }
    ],
    "routing": {
        "domainStrategy": "IPIfNonMatch",
        "rules": [
            {
                "type": "field",
                "ip": ["geoip:private"],
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "domain": ["geosite:category-ads-all"],
                "outboundTag": "block"
            }
        ]
    }
}

class ConfigManager:
    def __init__(self, path: str):
        self.path = path
        self.config = DEFAULT_CONFIG.copy()
        self._load_existing()

    def _load_existing(self):
        """Load existing config if it exists"""
        if os.path.exists(self.path):
            try:
                self.load()
            except Exception as e:
                print(f"Warning: Could not load existing config: {e}")
                print("Using default configuration")

    def set_outbound(self, outbound: Dict[str, Any]):
        """Set the main outbound configuration"""
        # Add tag for routing
        outbound["tag"] = "proxy"
        
        # Update outbounds - replace proxy outbound, keep freedom and block
        new_outbounds = []
        for ob in self.config["outbounds"]:
            if ob.get("tag") != "proxy":
                new_outbounds.append(ob)
        
        new_outbounds.insert(0, outbound)
        self.config["outbounds"] = new_outbounds

    def add_routing_rule(self, rule: Dict[str, Any]):
        """Add a custom routing rule"""
        if "routing" not in self.config:
            self.config["routing"] = {"rules": []}
        self.config["routing"]["rules"].append(rule)

    def set_log_level(self, level: str):
        """Set log level (debug, info, warning, error)"""
        if "log" not in self.config:
            self.config["log"] = {}
        self.config["log"]["loglevel"] = level

    def set_inbound_port(self, port: int, protocol: str = "socks"):
        """Set inbound port for specified protocol"""
        for inbound in self.config["inbounds"]:
            if inbound.get("protocol") == protocol:
                inbound["port"] = port
                break

    def enable_sniffing(self, enabled: bool = True):
        """Enable or disable traffic sniffing"""
        for inbound in self.config["inbounds"]:
            if inbound.get("protocol") == "socks":
                if "sniffing" not in inbound:
                    inbound["sniffing"] = {}
                inbound["sniffing"]["enabled"] = enabled
                break

    def save(self):
        """Save configuration to file"""
        # Ensure directory exists
        dir_path = os.path.dirname(self.path)
        if dir_path:  # Only create directory if path is not empty
            os.makedirs(dir_path, exist_ok=True)
        
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print(f"Configuration saved to {self.path}")

    def load(self):
        """Load configuration from file"""
        with open(self.path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()

    def validate(self) -> bool:
        """Validate configuration"""
        try:
            # Check required fields
            if "inbounds" not in self.config or "outbounds" not in self.config:
                return False
            
            # Check at least one proxy outbound exists
            has_proxy = any(ob.get("tag") == "proxy" for ob in self.config["outbounds"])
            if not has_proxy:
                return False
            
            return True
        except Exception:
            return False

    def print_summary(self):
        """Print configuration summary"""
        print("Configuration Summary:")
        print(f"  Inbounds: {len(self.config.get('inbounds', []))}")
        print(f"  Outbounds: {len(self.config.get('outbounds', []))}")
        
        # Show proxy outbound info
        for ob in self.config.get("outbounds", []):
            if ob.get("tag") == "proxy":
                protocol = ob.get("protocol", "unknown")
                address = ob.get("settings", {}).get("vnext", [{}])[0].get("address", "unknown")
                port = ob.get("settings", {}).get("vnext", [{}])[0].get("port", "unknown")
                print(f"  Proxy: {protocol} -> {address}:{port}")
                break