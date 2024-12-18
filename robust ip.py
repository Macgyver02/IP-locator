import requests
import socket
import ipaddress
import json
import random
import time
from typing import Dict, Any

class IPLocationTracker:
    def __init__(self):
        """
        Initialize the IP Location Tracker with multiple geolocation APIs
        """
        self.apis = [
            {
                "url": "https://ipapi.co/{}/json/",
                "name": "ipapi.co",
                "key_needed": False
            },
            {
                "url": "https://ipinfo.io/{}/json",
                "name": "ipinfo.io",
                "key_needed": False
            },
            {
                "url": "https://ip-api.com/json/{}",
                "name": "ip-api.com",
                "key_needed": False
            }
        ]

    def validate_ip_address(self, ip: str) -> bool:
        """
        Validate the input IP address
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def create_google_maps_link(self, latitude: float, longitude: float) -> str:
        """
        Generate a Google Maps link for given coordinates
        """
        if latitude == 0.0 and longitude == 0.0:
            return "No coordinates available"
        
        return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"

    def get_detailed_geolocation(self, ip: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive geolocation information using multiple APIs
        """
        if not self.validate_ip_address(ip):
            return {"error": "Invalid IP address format"}

        # Attempt to resolve hostname
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            hostname = "N/A"

        # Try multiple APIs
        for api in self.apis:
            try:
                response = requests.get(api['url'].format(ip), timeout=5)
                
                if response.status_code == 200:
                    geo_info = response.json()
                    
                    # Normalize data based on different API responses
                    if api['name'] == "ipapi.co":
                        return self._process_ipapi_response(ip, hostname, geo_info)
                    elif api['name'] == "ipinfo.io":
                        return self._process_ipinfo_response(ip, hostname, geo_info)
                    elif api['name'] == "ip-api.com":
                        return self._process_ipapi_direct_response(ip, hostname, geo_info)
                
                # Add small delay to prevent rate limiting
                time.sleep(1)
            
            except requests.RequestException:
                continue
        
        return {"error": "Failed to retrieve geolocation from all APIs"}

    def _process_ipapi_response(self, ip: str, hostname: str, geo_info: Dict) -> Dict:
        """Process response from ipapi.co"""
        latitude = geo_info.get('latitude', 0.0)
        longitude = geo_info.get('longitude', 0.0)

        return {
            "ip": ip,
            "hostname": hostname,
            "location": {
                "country": geo_info.get('country_name', 'Unknown'),
                "country_code": geo_info.get('country_code', 'N/A'),
                "city": geo_info.get('city', 'Unknown'),
                "region": geo_info.get('region', 'Unknown'),
                "postal_code": geo_info.get('postal', 'N/A'),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": geo_info.get('timezone', 'N/A'),
                "google_maps_link": self.create_google_maps_link(latitude, longitude)
            },
            "network": {
                "organization": geo_info.get('org', 'Unknown'),
                "isp": geo_info.get('isp', 'Unknown'),
                "asn": geo_info.get('asn', 'Unknown')
            }
        }

    def _process_ipinfo_response(self, ip: str, hostname: str, geo_info: Dict) -> Dict:
        """Process response from ipinfo.io"""
        loc = geo_info.get('loc', '0,0').split(',')
        latitude = float(loc[0])
        longitude = float(loc[1])

        return {
            "ip": ip,
            "hostname": hostname,
            "location": {
                "country": geo_info.get('country', 'Unknown'),
                "country_code": geo_info.get('country', 'N/A'),
                "city": geo_info.get('city', 'Unknown'),
                "region": geo_info.get('region', 'Unknown'),
                "postal_code": geo_info.get('postal', 'N/A'),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": geo_info.get('timezone', 'N/A'),
                "google_maps_link": self.create_google_maps_link(latitude, longitude)
            },
            "network": {
                "organization": geo_info.get('org', 'Unknown'),
                "isp": "N/A",
                "asn": "N/A"
            }
        }

    def _process_ipapi_direct_response(self, ip: str, hostname: str, geo_info: Dict) -> Dict:
        """Process response from ip-api.com"""
        latitude = geo_info.get('lat', 0.0)
        longitude = geo_info.get('lon', 0.0)

        return {
            "ip": ip,
            "hostname": hostname,
            "location": {
                "country": geo_info.get('country', 'Unknown'),
                "country_code": geo_info.get('countryCode', 'N/A'),
                "city": geo_info.get('city', 'Unknown'),
                "region": geo_info.get('regionName', 'Unknown'),
                "postal_code": geo_info.get('zip', 'N/A'),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": geo_info.get('timezone', 'N/A'),
                "google_maps_link": self.create_google_maps_link(latitude, longitude)
            },
            "network": {
                "organization": geo_info.get('org', 'Unknown'),
                "isp": geo_info.get('isp', 'Unknown'),
                "asn": "N/A"
            }
        }

    def display_location_details(self, location_info: Dict[str, Any]):
        """
        Display detailed location information in a formatted manner
        """
        if "error" in location_info:
            print(f"Error: {location_info['error']}")
            return

        print("\n===== IP Location Details =====")
        print(f"IP Address: {location_info['ip']}")
        print(f"Hostname: {location_info['hostname']}")
        
        print("\nLocation Information:")
        loc = location_info['location']
        for key, value in loc.items():
            if key != 'google_maps_link':
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print(f"\nGoogle Maps Link: {loc['google_maps_link']}")
        
        print("\nNetwork Details:")
        net = location_info['network']
        for key, value in net.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

def main():
    tracker = IPLocationTracker()
    
    print("IP Location Tracker")
    print("--------------------")
    
    while True:
        ip_address = input("\nEnter an IP address (or 'quit' to exit): ").strip()
        
        if ip_address.lower() == 'quit':
            break
        
        # Retrieve and display location details
        location_info = tracker.get_detailed_geolocation(ip_address)
        tracker.display_location_details(location_info)

if __name__ == "__main__":
    main()