"""
OverpassMap Adapter - استخراج البيانات الجغرافية من OpenStreetMap
يبحث عن مواقع جغرافية محددة (مراقبة، مستشفيات، قواعد عسكرية...) داخل مدينة معينة
الاستخدام: python3 overpassmap_adapter.py "London" "amenity" "hospital"
"""
import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXTERNAL_TOOL_DIR = os.path.join(PROJECT_ROOT, 'external_tools', 'Coriza-Tool-Pro', 'overpassmap')
sys.path.insert(0, EXTERNAL_TOOL_DIR)

import requests

# خريطة الاختصارات: يمكن تمرير اسم الفئة بدلاً من tag_key/tag_value
CATEGORY_SHORTCUTS = {
    "hospital":     ("amenity", "hospital"),
    "police":       ("amenity", "police"),
    "military":     ("military", "base"),
    "surveillance": ("man_made", "surveillance"),
    "bank":         ("amenity", "bank"),
    "atm":          ("amenity", "atm"),
    "airport":      ("aeroway", "aerodrome"),
    "helipad":      ("aeroway", "helipad"),
    "fire_station": ("amenity", "fire_station"),
    "antenna":      ("telecom", "antenna"),
    "checkpoint":   ("military", "checkpoint"),
    "government":   ("office", "government"),
    "pharmacy":     ("amenity", "pharmacy"),
}

def run_overpass_query(city, tag_key, tag_value):
    """استعلام مباشر عبر Overpass API مع geocoding عبر Nominatim"""
    # الحصول على إحداثيات المدينة أولاً
    try:
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        geo_resp = requests.get(nominatim_url, params={"q": city, "format": "json", "limit": 1},
                                headers={"User-Agent": "Coriza-OSINT/1.0"}, timeout=10)
        geo_data = geo_resp.json()
        if not geo_data:
            return {"error": f"City '{city}' not found", "city": city}
        bbox = geo_data[0].get("boundingbox", [])
        if len(bbox) < 4:
            return {"error": "Could not get bounding box", "city": city}
        south, north, west, east = bbox
    except Exception as e:
        return {"error": f"Geocoding failed: {e}"}

    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
      node["{tag_key}"="{tag_value}"]({south},{west},{north},{east});
      way["{tag_key}"="{tag_value}"]({south},{west},{north},{east});
    );
    out body center;
    """
    try:
        response = requests.post(overpass_url, data={'data': query}, timeout=30)
        if response.status_code == 200:
            elements = response.json().get('elements', [])
            results = []
            for el in elements:
                lat = el.get('lat') or el.get('center', {}).get('lat')
                lon = el.get('lon') or el.get('center', {}).get('lon')
                tags = el.get('tags', {})
                results.append({
                    "id": el.get('id'),
                    "type": el.get('type'),
                    "name": tags.get('name', 'Unnamed'),
                    "lat": lat,
                    "lon": lon,
                    "tags": tags
                })
            return {
                "city": city,
                "query": f"{tag_key}={tag_value}",
                "total_found": len(results),
                "locations": results[:100]
            }
        else:
            return {"error": f"Overpass API error: HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: overpassmap_adapter.py <city> [category|tag_key] [tag_value]",
            "available_categories": list(CATEGORY_SHORTCUTS.keys())
        }))
        sys.exit(1)

    city = sys.argv[1].strip()

    if len(sys.argv) == 2:
        # لا يوجد تصنيف - نستخدم المستشفيات كافتراضي
        tag_key, tag_value = "amenity", "hospital"
    elif len(sys.argv) == 3:
        shortcut = sys.argv[2].lower()
        if shortcut in CATEGORY_SHORTCUTS:
            tag_key, tag_value = CATEGORY_SHORTCUTS[shortcut]
        else:
            print(json.dumps({"error": f"Unknown category '{shortcut}'. Use: {list(CATEGORY_SHORTCUTS.keys())}"}))
            sys.exit(1)
    else:
        tag_key = sys.argv[2].strip()
        tag_value = sys.argv[3].strip()

    result = run_overpass_query(city=city, tag_key=tag_key, tag_value=tag_value)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
