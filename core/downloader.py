import os
import platform
import requests
import zipfile
import shutil
from io import BytesIO
from typing import Optional, Tuple
import logging

GITHUB_API_RELEASES = "https://api.github.com/repos/v2fly/v2ray-core/releases/latest"

class V2RayDownloader:
    def __init__(self, extract_path: str = "./bin"):
        self.extract_path = extract_path
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.logger = logging.getLogger(__name__)
        
        # Normalize architecture names
        if self.arch in ["x86_64", "amd64"]:
            self.arch = "64"
        elif self.arch in ["i386", "i686", "x86"]:
            self.arch = "32"
        elif self.arch == "arm64":
            self.arch = "arm64"
        elif self.arch.startswith("arm"):
            self.arch = "arm32"

    def get_latest_release_info(self) -> dict:
        """Get latest release information from GitHub"""
        try:
            resp = requests.get(GITHUB_API_RELEASES, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch release info: {e}")

    def get_asset_url(self, release_info: dict) -> str:
        """Get download URL for current platform"""
        # Determine asset key based on platform
        asset_key = self._get_asset_key()
        
        for asset in release_info["assets"]:
            if asset_key in asset["name"]:
                return asset["browser_download_url"]
        
        raise RuntimeError(f"Suitable asset not found for {asset_key}")

    def _get_asset_key(self) -> str:
        """Get asset key for current platform"""
        if self.system == "linux":
            if self.arch == "64":
                return "v2ray-linux-64.zip"
            elif self.arch == "32":
                return "v2ray-linux-32.zip"
            elif self.arch == "arm64":
                return "v2ray-linux-arm64-v8a.zip"
            elif self.arch == "arm32":
                return "v2ray-linux-arm32-v7a.zip"
        elif self.system == "darwin":
            if self.arch == "64":
                return "v2ray-macos-64.zip"
            elif self.arch == "arm64":
                return "v2ray-macos-arm64-v8a.zip"
        elif self.system == "windows":
            if self.arch == "64":
                return "v2ray-windows-64.zip"
            elif self.arch == "32":
                return "v2ray-windows-32.zip"
            elif self.arch == "arm64":
                return "v2ray-windows-arm64-v8a.zip"
        
        raise RuntimeError(f"Unsupported platform: {self.system} {self.arch}")

    def download_and_extract(self, force: bool = False) -> str:
        """Download and extract v2ray binary"""
        # Check if already exists
        v2ray_binary = self._get_v2ray_binary_path()
        if os.path.exists(v2ray_binary) and not force:
            self.logger.info(f"V2Ray binary already exists at {v2ray_binary}")
            return v2ray_binary
        
        # Create extract directory
        os.makedirs(self.extract_path, exist_ok=True)
        
        # Get release info and download URL
        release_info = self.get_latest_release_info()
        url = self.get_asset_url(release_info)
        
        self.logger.info(f"Downloading V2Ray from {url}...")
        
        # Download with progress
        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # Download to memory first
            content = BytesIO()
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rDownload progress: {progress:.1f}%", end="", flush=True)
            
            print()  # New line after progress
            
            # Extract
            self.logger.info("Extracting V2Ray...")
            with zipfile.ZipFile(content) as z:
                z.extractall(self.extract_path)
            
            # Find and rename v2ray binary
            v2ray_binary = self._setup_v2ray_binary()
            
            # Make executable on Unix systems
            if self.system != "windows":
                os.chmod(v2ray_binary, 0o755)
            
            self.logger.info(f"V2Ray extracted to {v2ray_binary}")
            return v2ray_binary
            
        except Exception as e:
            # Cleanup on failure
            if os.path.exists(self.extract_path):
                shutil.rmtree(self.extract_path)
            raise RuntimeError(f"Failed to download/extract V2Ray: {e}")

    def _setup_v2ray_binary(self) -> str:
        """Setup v2ray binary and return path"""
        # Find v2ray binary in extracted files
        v2ray_name = "v2ray.exe" if self.system == "windows" else "v2ray"
        
        # Look for binary in extract path
        for root, dirs, files in os.walk(self.extract_path):
            if v2ray_name in files:
                v2ray_path = os.path.join(root, v2ray_name)
                break
        else:
            raise RuntimeError(f"V2Ray binary not found in extracted files")
        
        # Move to extract_path root for easier access
        final_path = os.path.join(self.extract_path, v2ray_name)
        if v2ray_path != final_path:
            shutil.move(v2ray_path, final_path)
        
        return final_path

    def _get_v2ray_binary_path(self) -> str:
        """Get expected path of v2ray binary"""
        v2ray_name = "v2ray.exe" if self.system == "windows" else "v2ray"
        return os.path.join(self.extract_path, v2ray_name)

    def get_version(self) -> Optional[str]:
        """Get installed v2ray version"""
        v2ray_binary = self._get_v2ray_binary_path()
        if not os.path.exists(v2ray_binary):
            return None
        
        try:
            import subprocess
            result = subprocess.run([v2ray_binary, "version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Extract version from output
                for line in result.stdout.split('\n'):
                    if 'V2Ray' in line:
                        return line.strip()
        except Exception:
            pass
        
        return None

    def cleanup(self):
        """Clean up downloaded files"""
        if os.path.exists(self.extract_path):
            shutil.rmtree(self.extract_path)
            self.logger.info(f"Cleaned up {self.extract_path}")

    def check_update(self) -> Tuple[bool, Optional[str]]:
        """Check if update is available"""
        try:
            release_info = self.get_latest_release_info()
            latest_version = release_info.get("tag_name", "")
            current_version = self.get_version()
            
            if current_version and latest_version:
                return latest_version != current_version, latest_version
            
            return False, latest_version
        except Exception as e:
            self.logger.error(f"Failed to check for updates: {e}")
            return False, None


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    downloader = V2RayDownloader()
    try:
        binary_path = downloader.download_and_extract()
        print(f"V2Ray installed at: {binary_path}")
        
        version = downloader.get_version()
        if version:
            print(f"Version: {version}")
        
        has_update, latest = downloader.check_update()
        if has_update:
            print(f"Update available: {latest}")
        else:
            print("V2Ray is up to date")
            
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
