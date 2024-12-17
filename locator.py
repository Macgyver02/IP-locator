import requests
import socket
import ipaddress
import json
import re
import urllib.parse
from typing import Dict, Any

class IPLocationTracker:
    def __init__(self):
        """
        Initialize the IP Location Tracker with geolocation API
        """
        # Free IP geolocation API (limited requests)
        self.geo_api_url = "https://ipapi.co/{}/json/"

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
        
        # Construct Google Maps URL
        base_url = "https://www.google.com/maps/search/?api=1&query="
        query = f"{latitude},{longitude}"
        
        return base_url + urllib.parse.quote(query)

    def get_detailed_geolocation(self, ip: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive geolocation information for an IP address
        """
        if not self.validate_ip_address(ip):
            return {"error": "Invalid IP address format"}

        try:
            # Resolve hostname
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except (socket.herror, socket.gaierror):
                hostname = "N/A"

            # Get geolocation data
            response = requests.get(self.geo_api_url.format(ip), timeout=5)
            
            if response.status_code == 200:
                geo_info = response.json()
                
                # Prepare detailed location information
                latitude = geo_info.get('latitude', 0.0)
                longitude = geo_info.get('longitude', 0.0)

                detailed_info = {
                    "ip": ip,
                    "hostname": hostname,
                    "location": {
                        "country": geo_info.get('country_name', 'Unknown'),
                        "country_code": geo_info.get('country_code', 'N/A'),
                        "city": geo_info.get('city', 'Unknown'),
                        "region": geo_info.get('region', 'Unknown'),
                        "continent": geo_info.get('continent_code', 'Unknown'),
                        "postal_code": geo_info.get('postal', 'N/A'),
                        "latitude": latitude,
                        "longitude": longitude,
                        "timezone": geo_info.get('timezone', 'N/A'),
                        "google_maps_link": self.create_google_maps_link(latitude, longitude)
                    },
                    "network": {
                        "organization": geo_info.get('org', 'Unknown'),
                        "isp": geo_info.get('isp', 'Unknown'),
                        "asn": geo_info.get('asn', 'Unknown'),
                        "connection_type": geo_info.get('connection_type', 'N/A')
                    }
                }
                
                return detailed_info
            else:
                return {"error": f"Failed to retrieve geolocation. Status code: {response.status_code}"}
        
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

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