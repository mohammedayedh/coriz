import requests
import csv
import sys

class TextColor:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_banner():
    banner = rf"""
{TextColor.CYAN}
   ____                                   
  / __ \_   _____  _________  ____  _____ 
 / / / / | / / _ \/ ___/ __ \/ __ `/ ___/ 
/ /_/ /| |/ /  __/ /  / /_/ / /_/ (__  )  
\____/ |___/\___/_/  / .___/\__,_/____/   
                    /_/                   
           Geo-OSINT Tool (Detailed Mode)
{TextColor.END}
"""
    print(banner)

# Dictionary of categories and tags
OSM_CATEGORIES = {
    "1": {
        "title": "Security & Intelligence",
        "options": [
            {"key": "man_made", "val": "surveillance", "desc": "CCTV and Surveillance Cameras"},
            {"key": "amenity", "val": "police", "desc": "Police Stations and Outposts"},
            {"key": "military", "val": "base", "desc": "Military Bases and Facilities"},
            {"key": "military", "val": "checkpoint", "desc": "Military or Security Checkpoints"},
            {"key": "barrier", "val": "gate", "desc": "Security Gates and Closed Entrances"}
        ]
    },
    "2": {
        "title": "Infrastructure & Telecom",
        "options": [
            {"key": "telecom", "val": "antenna", "desc": "Cellular Towers and Antennas"},
            {"key": "power", "val": "substation", "desc": "Power Substations"},
            {"key": "aeroway", "val": "helipad", "desc": "Helipads"},
            {"key": "aeroway", "val": "aerodrome", "desc": "Airports and Aerodromes"},
            {"key": "highway", "val": "traffic_signals", "desc": "Traffic Signals and Lights"}
        ]
    },
    "3": {
        "title": "Financial & Corporate",
        "options": [
            {"key": "amenity", "val": "bank", "desc": "Bank Branches"},
            {"key": "amenity", "val": "atm", "desc": "Automated Teller Machines (ATMs)"},
            {"key": "office", "val": "company", "desc": "Corporate Headquarters and Offices"},
            {"key": "office", "val": "government", "desc": "Government Buildings and Offices"}
        ]
    },
    "4": {
        "title": "Emergency & Medical",
        "options": [
            {"key": "amenity", "val": "hospital", "desc": "Hospitals and Medical Centers"},
            {"key": "amenity", "val": "pharmacy", "desc": "Pharmacies"},
            {"key": "amenity", "val": "fire_station", "desc": "Fire Stations"}
        ]
    },
    "5": {
        "title": "Public Life & Facilities",
        "options": [
            {"key": "amenity", "val": "fuel", "desc": "Gas and Fuel Stations"},
            {"key": "amenity", "val": "cafe", "desc": "Cafes and Coffee Shops"},
            {"key": "amenity", "val": "place_of_worship", "desc": "Places of Worship (Mosques, Churches, etc.)"},
            {"key": "shop", "val": "supermarket", "desc": "Supermarkets and Groceries"}
        ]
    },
    "6": {
        "title": "Manual Entry (Custom Tags)",
        "options": [] 
    }
}

def run_overpass(city, tag_key, tag_value, output_file=None):
    """
    Main function for Geo-OSINT querying with highly detailed metadata extraction.
    """
    print(f"\n[*] Querying OpenStreetMap for [{tag_key}={tag_value}] in [{city}]...\n")
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # The query is designed to fetch full detailed data (out body center)
    overpass_query = f"""
    [out:json][timeout:25];
    area[name="{city}"]->.searchArea;
    (
      node["{tag_key}"="{tag_value}"](area.searchArea);
      way["{tag_key}"="{tag_value}"](area.searchArea);
      relation["{tag_key}"="{tag_value}"](area.searchArea);
    );
    out body center;
    """
    
    try:
        response = requests.post(overpass_url, data={'data': overpass_query}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get('elements', [])
            
            if not elements:
                print(f"{TextColor.YELLOW}[-] No results found for your query in the specified city.{TextColor.END}")
                return []
                
            print(f"{TextColor.GREEN}[+] Successfully extracted {len(elements)} locations with FULL details!{TextColor.END}")
            
            all_results = []
            # Use a set to dynamically collect all possible columns found
            all_fieldnames = {"ID", "Type", "Name", "Latitude", "Longitude"}
            
            for el in elements:
                lat = el.get('lat') or el.get('center', {}).get('lat', 'Unknown')
                lon = el.get('lon') or el.get('center', {}).get('lon', 'Unknown')
                el_id = el.get('id', 'Unknown')
                el_type = el.get('type', 'Unknown')
                
                tags = el.get('tags', {})
                name = tags.get('name', 'Unnamed Location')
                
                # Basic data dictionary
                row_data = {
                    "ID": el_id,
                    "Type": el_type,
                    "Name": name,
                    "Latitude": lat,
                    "Longitude": lon,
                }
                
                # Dynamically add all other detailed tags
                for k, v in tags.items():
                    if k != 'name': # Avoid duplicating the name
                        row_data[k] = v
                        all_fieldnames.add(k)
                        
                all_results.append(row_data)
                
                # Print a quick sample to the screen
                extra_info = ""
                if 'phone' in tags: extra_info += f" | Phone: {tags['phone']}"
                if 'website' in tags: extra_info += f" | Web: {tags['website']}"
                print(f"  -> {name} {TextColor.YELLOW}{extra_info}{TextColor.END}")
                
            if output_file:
                try:
                    # Sort CSV columns to have basic ones first, then the rest
                    base_cols = ["ID", "Type", "Name", "Latitude", "Longitude"]
                    other_cols = sorted([f for f in all_fieldnames if f not in base_cols])
                    final_fieldnames = base_cols + other_cols
                    
                    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=final_fieldnames)
                        writer.writeheader()
                        writer.writerows(all_results)
                    print(f"\n{TextColor.CYAN}[*] Process completed! Detailed results saved to -> {output_file}{TextColor.END}\n")
                except Exception as e:
                    print(f"\n{TextColor.RED}[!] Failed to save CSV file: {e}{TextColor.END}\n")
                    
            return all_results
        else:
            print(f"{TextColor.RED}[!] API Error. Status Code: {response.status_code}{TextColor.END}")
            
    except requests.exceptions.RequestException as e:
        print(f"{TextColor.RED}[!] Network error: {e}{TextColor.END}")
        
    return []


if __name__ == "__main__":
    print_banner()
    
    target_city = input(f"{TextColor.YELLOW}Enter target City (e.g., London, Sanaa, Cairo): {TextColor.END}").strip()
    if not target_city:
        print(f"{TextColor.RED}[!] City is required. Exiting...{TextColor.END}")
        sys.exit()

    print(f"\n{TextColor.CYAN}=== Select a Category ==={TextColor.END}")
    for key, cat in OSM_CATEGORIES.items():
        print(f"{key}. {cat['title']}")
        
    cat_choice = input(f"\n{TextColor.YELLOW}Enter Category Number (1-6): {TextColor.END}").strip()
    
    if cat_choice not in OSM_CATEGORIES:
        print(f"{TextColor.RED}[!] Invalid choice. Exiting...{TextColor.END}")
        sys.exit()
        
    selected_cat = OSM_CATEGORIES[cat_choice]
    
    tag_key = ""
    tag_val = ""
    
    if cat_choice == "6":
        tag_key = input(f"{TextColor.CYAN}Enter Custom Key (e.g., amenity): {TextColor.END}").strip()
        tag_val = input(f"{TextColor.CYAN}Enter Custom Value (e.g., cafe): {TextColor.END}").strip()
    else:
        print(f"\n{TextColor.CYAN}=== {selected_cat['title']} ==={TextColor.END}")
        for idx, option in enumerate(selected_cat['options'], 1):
            print(f"{idx}. [{option['key']}={option['val']}] -> {option['desc']}")
            
        opt_choice = input(f"\n{TextColor.YELLOW}Select an option (1-{len(selected_cat['options'])}): {TextColor.END}").strip()
        
        try:
            opt_idx = int(opt_choice) - 1
            if 0 <= opt_idx < len(selected_cat['options']):
                chosen_option = selected_cat['options'][opt_idx]
                tag_key = chosen_option['key']
                tag_val = chosen_option['val']
            else:
                print(f"{TextColor.RED}[!] Invalid option number. Exiting...{TextColor.END}")
                sys.exit()
        except ValueError:
            print(f"{TextColor.RED}[!] Please enter a valid number. Exiting...{TextColor.END}")
            sys.exit()

    if tag_key and tag_val:
        out_file = f"osm_{tag_val}_in_{target_city.replace(' ', '_')}.csv"
        run_overpass(city=target_city, tag_key=tag_key, tag_value=tag_val, output_file=out_file)
    else:
        print(f"{TextColor.RED}[!] Incomplete tag information. Exiting...{TextColor.END}")