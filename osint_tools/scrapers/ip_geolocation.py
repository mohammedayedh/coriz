"""
IP Geolocation Scraper
تحديد الموقع الجغرافي لعناوين IP
المصدر: ip-api.com (مجاني 100% - بدون API key)
"""

import requests
import json
import argparse
from typing import Dict, Any, List

class IPGeolocationScraper:
    def __init__(self):
        self.services = {
            'ip-api': 'http://ip-api.com/json/',
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def lookup(self, ip_address: str) -> Dict[str, Any]:
        results = {'success': False, 'ip': ip_address, 'results': [], 'total_found': 0, 'error': None}
        try:
            url = f"{self.services['ip-api']}{ip_address}"
            params = {
                'fields': 'status,message,country,countryCode,regionName,city,lat,lon,timezone,isp,org,as,proxy,hosting'
            }
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    # إضافة النتائج بصيغة مهيكلة للمنصة
                    results['results'].append({
                        'title': f"الموقع الجغرافي: {data.get('city')}, {data.get('country')}",
                        'description': f"المزود: {data.get('isp')} | التوقيت: {data.get('timezone')}",
                        'type': 'geolocation',
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'confidence': 'high'
                    })
                    
                    if data.get('proxy') or data.get('hosting'):
                        results['results'].append({
                            'title': "تحليل الشبكة",
                            'description': f"بروكسي: {'نعم' if data.get('proxy') else 'لا'} | استضافة: {'نعم' if data.get('hosting') else 'لا'}",
                            'type': 'network_security',
                            'confidence': 'medium'
                        })
                        
                    results['total_found'] = len(results['results'])
                    results['success'] = True
                else:
                    results['error'] = data.get('message', 'فشل البحث')
        except Exception as e:
            results['error'] = str(e)
        return results

def main():
    parser = argparse.ArgumentParser(description='IP Geolocation Tool for Coriza')
    parser.add_argument('--ip', required=True, help='Target IP Address')
    args = parser.parse_args()
    
    scraper = IPGeolocationScraper()
    output = scraper.lookup(args.ip)
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
