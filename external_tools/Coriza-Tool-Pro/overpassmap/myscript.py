# 1. Import the tool
import overpassmap

# 2. Define target parameters
target_city = "Sanaa"
key = "amenity"
value = "hospital"

csv_filename = f"detailed_{value}_{target_city}.csv"

print(f"--- Starting Geo-OSINT scan for {value} in {target_city} ---")

# 3. Call the function
results = overpassmap.run_overpass(
    city=target_city, 
    tag_key=key, 
    tag_value=value, 
    output_file=csv_filename
)

# 4. Optional: Handle output
if results:
    print(f"\n[!] Success! Found {len(results)} locations.")
    print("Top 3 results:")
    for i, place in enumerate(results[:3], 1):
        print(f" {i}. {place.get('Name', 'Unnamed Location')}")
else:
    print("\n[-] No results found.")