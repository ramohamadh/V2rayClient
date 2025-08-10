import base64
import json
import re
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs


def parse_vmess_link(vmess_link: str) -> Dict[str, Any]:
    """
    Parse vmess:// link and return v2ray outbound configuration
    Supports both legacy and new vmess formats
    """
    if not vmess_link.startswith("vmess://"):
        raise ValueError("Not a vmess link")
    
    # Extract the base64 part
    b64 = vmess_link[len("vmess://"):]
    
    # Handle URL encoding if present
    if '%' in b64:
        import urllib.parse
        b64 = urllib.parse.unquote(b64)
    
    # Fix base64 padding
    missing = len(b64) % 4
    if missing:
        b64 += "=" * (4 - missing)
    
    try:
        raw = base64.b64decode(b64)
        data = json.loads(raw)
    except Exception as e:
        raise ValueError(f"Failed to decode vmess link: {e}")
    
    # Validate required fields
    required_fields = ['add', 'port', 'id']
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    # Build outbound configuration
    outbound = {
        "protocol": "vmess",
        "settings": {
            "vnext": [
                {
                    "address": data.get("add") or data.get("host"),
                    "port": int(data.get("port", 443)),
                    "users": [
                        {
                            "id": data.get("id"),
                            "alterId": int(data.get("aid", 0)) if data.get("aid") else 0,
                            "security": data.get("scy", "auto")
                        }
                    ]
                }
            ]
        }
    }
    
    # Handle stream settings
    if data.get("net"):
        outbound["streamSettings"] = {"network": data.get("net")}
        
        # WebSocket settings
        if data.get("net") == "ws":
            ws_settings = {}
            if data.get("path"):
                ws_settings["path"] = data.get("path")
            if data.get("host"):
                ws_settings["headers"] = {"Host": data.get("host")}
            if ws_settings:
                outbound["streamSettings"]["wsSettings"] = ws_settings
        
        # HTTP/2 settings
        elif data.get("net") == "h2":
            h2_settings = {}
            if data.get("path"):
                h2_settings["path"] = data.get("path")
            if data.get("host"):
                h2_settings["host"] = [data.get("host")]
            if h2_settings:
                outbound["streamSettings"]["httpSettings"] = h2_settings
        
        # TCP settings
        elif data.get("net") == "tcp":
            tcp_settings = {}
            if data.get("type") == "http":
                tcp_settings["type"] = "http"
                http_settings = {}
                if data.get("path"):
                    http_settings["path"] = [data.get("path")]
                if data.get("host"):
                    http_settings["host"] = [data.get("host")]
                if http_settings:
                    tcp_settings["httpSettings"] = http_settings
            if tcp_settings:
                outbound["streamSettings"]["tcpSettings"] = tcp_settings
        
        # TLS settings
        if data.get("tls") == "tls":
            tls_settings = {
                "serverName": data.get("sni") or data.get("host") or data.get("add"),
                "allowInsecure": True
            }
            outbound["streamSettings"]["security"] = "tls"
            outbound["streamSettings"]["tlsSettings"] = tls_settings
    
    return outbound


def parse_vmess_url(vmess_url: str) -> Dict[str, Any]:
    """
    Parse vmess:// URL format with query parameters
    """
    if not vmess_url.startswith("vmess://"):
        raise ValueError("Not a vmess URL")
    
    # Remove vmess:// prefix
    url_part = vmess_url[8:]
    
    # Split into base64 part and query part
    if '?' in url_part:
        b64_part, query_part = url_part.split('?', 1)
        query_params = parse_qs(query_part)
    else:
        b64_part = url_part
        query_params = {}
    
    # Parse base64 part
    outbound = parse_vmess_link(f"vmess://{b64_part}")
    
    # Apply query parameters
    if query_params.get('security'):
        outbound.setdefault("streamSettings", {})["security"] = query_params['security'][0]
    
    if query_params.get('sni'):
        outbound.setdefault("streamSettings", {}).setdefault("tlsSettings", {})["serverName"] = query_params['sni'][0]
    
    return outbound


def parse_vless_url(vless_url: str) -> Dict[str, Any]:
    """
    Parse vless:// URL format with query parameters
    """
    if not vless_url.startswith("vless://"):
        raise ValueError("Not a vless URL")
    
    # Parse the URL
    parsed = urlparse(vless_url)
    
    # Extract components
    uuid = parsed.username
    host = parsed.hostname
    port = parsed.port or 443
    query_params = parse_qs(parsed.query)
    fragment = parsed.fragment
    
    if not uuid or not host:
        raise ValueError("Invalid vless URL: missing UUID or host")
    
    # Build outbound configuration
    outbound = {
        "protocol": "vless",
        "settings": {
            "vnext": [
                {
                    "address": host,
                    "port": port,
                    "users": [
                        {
                            "id": uuid,
                            "encryption": query_params.get('encryption', ['none'])[0],
                            "flow": query_params.get('flow', [''])[0] if query_params.get('flow') else None
                        }
                    ]
                }
            ]
        }
    }
    
    # Remove None values
    for user in outbound["settings"]["vnext"][0]["users"]:
        if user["flow"] is None:
            del user["flow"]
    
    # Handle stream settings
    stream_settings = {}
    
    # Network type
    network = query_params.get('type', ['tcp'])[0]
    # Treat xhttp as http since V2Ray doesn't support xhttp
    if network == "xhttp":
        network = "http"
    stream_settings["network"] = network
    
    # WebSocket settings
    if network == "ws":
        ws_settings = {}
        if query_params.get('path'):
            path = query_params['path'][0]
            # Remove leading slash if present for WebSocket path
            if path.startswith('/'):
                path = path[1:]
            ws_settings["path"] = f"/{path}" if path else "/"
        if query_params.get('host'):
            ws_settings["headers"] = {"Host": query_params['host'][0]}
        if ws_settings:
            stream_settings["wsSettings"] = ws_settings
    
    # HTTP/2 settings
    elif network == "h2":
        h2_settings = {}
        if query_params.get('path'):
            h2_settings["path"] = query_params['path'][0]
        if query_params.get('host'):
            h2_settings["host"] = [query_params['host'][0]]
        if h2_settings:
            stream_settings["httpSettings"] = h2_settings
    
    # HTTP settings
    elif network == "http":
        http_settings = {}
        if query_params.get('path'):
            http_settings["path"] = query_params['path'][0]
        if query_params.get('host'):
            http_settings["host"] = [query_params['host'][0]]
        if http_settings:
            stream_settings["httpSettings"] = http_settings
    
    # TCP settings
    elif network == "tcp":
        tcp_settings = {}
        if query_params.get('type') and query_params['type'][0] == "http":
            tcp_settings["type"] = "http"
            http_settings = {}
            if query_params.get('path'):
                http_settings["path"] = [query_params['path'][0]]
            if query_params.get('host'):
                http_settings["host"] = [query_params['host'][0]]
            if http_settings:
                tcp_settings["httpSettings"] = http_settings
        if tcp_settings:
            stream_settings["tcpSettings"] = tcp_settings
    
    # XHTTP settings (custom HTTP-like protocol)
    elif network == "xhttp":
        xhttp_settings = {}
        if query_params.get('path'):
            xhttp_settings["path"] = query_params['path'][0]
        if xhttp_settings:
            stream_settings["xhttpSettings"] = xhttp_settings
    
    # Security settings
    security = query_params.get('security', ['none'])[0]
    if security == "tls":
        stream_settings["security"] = "tls"
        tls_settings = {}
        
        if query_params.get('sni'):
            tls_settings["serverName"] = query_params['sni'][0]
        
        if query_params.get('allowInsecure'):
            tls_settings["allowInsecure"] = query_params['allowInsecure'][0] == "1"
        else:
            # Default to false for security
            tls_settings["allowInsecure"] = False
        
        if query_params.get('alpn'):
            alpn_values = query_params['alpn'][0].split(',')
            tls_settings["alpn"] = alpn_values
        
        if query_params.get('fp'):
            fp_value = query_params['fp'][0]
            # Handle special fingerprint values
            if fp_value == "random":
                tls_settings["fingerprint"] = "random"
            elif fp_value in ["chrome", "firefox", "safari", "edge", "360", "qq", "android", "ios", "random", "randomized"]:
                tls_settings["fingerprint"] = fp_value
            else:
                # Default to chrome if unknown
                tls_settings["fingerprint"] = "chrome"
        
        if tls_settings:
            stream_settings["tlsSettings"] = tls_settings
    
    elif security == "reality":
        stream_settings["security"] = "reality"
        reality_settings = {}
        
        if query_params.get('sni'):
            reality_settings["serverName"] = query_params['sni'][0]
        
        if query_params.get('fp'):
            reality_settings["fingerprint"] = query_params['fp'][0]
        
        if query_params.get('pbk'):
            reality_settings["publicKey"] = query_params['pbk'][0]
        
        if query_params.get('sid'):
            reality_settings["shortId"] = query_params['sid'][0]
        
        if query_params.get('spx'):
            reality_settings["spiderX"] = query_params['spx'][0]
        
        if reality_settings:
            stream_settings["realitySettings"] = reality_settings
    
    # Add stream settings if not empty
    if stream_settings:
        outbound["streamSettings"] = stream_settings
    
    return outbound


def parse_proxy_url(proxy_url: str) -> Dict[str, Any]:
    """
    Parse proxy URL and return appropriate outbound configuration
    Supports vmess:// and vless:// protocols
    """
    if proxy_url.startswith("vmess://"):
        return parse_vmess_url(proxy_url)
    elif proxy_url.startswith("vless://"):
        return parse_vless_url(proxy_url)
    else:
        raise ValueError(f"Unsupported protocol: {proxy_url.split('://')[0] if '://' in proxy_url else 'unknown'}")