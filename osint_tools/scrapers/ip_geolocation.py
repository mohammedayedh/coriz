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
            # طلب جميع الحقول الممكنة والمهمة من الـ API
            params = {
                'fields': 'status,message,continent,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,mobile,proxy,hosting'
            }
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    # 1. الموقع الجغرافي (Geolocation)
                    location_desc = []
                    if data.get('city'): location_desc.append(f"المدينة: {data.get('city')}")
                    if data.get('regionName'): location_desc.append(f"المنطقة: {data.get('regionName')}")
                    if data.get('zip'): location_desc.append(f"الرمز البريدي: {data.get('zip')}")
                    
                    results['results'].append({
                        'title': f"الموقع الجغرافي: {data.get('country')}",
                        'description': " | ".join(location_desc),
                        'type': 'geolocation',
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'confidence': 'high'
                    })
                    
                    # 2. معلومات الشبكة (Network Intelligence)
                    network_desc = []
                    if data.get('isp'): network_desc.append(f"مزود الخدمة: {data.get('isp')}")
                    if data.get('org'): network_desc.append(f"المنظمة: {data.get('org')}")
                    if data.get('as'): network_desc.append(f"الشبكة (ASN): {data.get('as')}")
                    
                    if network_desc:
                        results['results'].append({
                            'title': "معلومات الشبكة والمزود",
                            'description': " | ".join(network_desc),
                            'type': 'network',
                            'confidence': 'high'
                        })
                    
                    # 3. تحليل الأمان والخصوصية (Security Flags)
                    flags = []
                    if data.get('proxy'): flags.append("⚠️ يستخدم Proxy أو VPN")
                    if data.get('hosting'): flags.append("🖥️ عنوان يتبع لمركز بيانات (Hosting/Data Center)")
                    if data.get('mobile'): flags.append("📱 اتصال شبكة هاتف محمول (Cellular)")
                    
                    if flags:
                        results['results'].append({
                            'title': "تحليل الأمان والخصوصية",
                            'description': " • ".join(flags),
                            'type': 'security_alert',
                            'confidence': 'high'
                        })
                    elif data.get('proxy') is False and data.get('hosting') is False:
                        results['results'].append({
                            'title': "تحليل الأمان",
                            'description': "✅ اتصال منزلي طبيعي (لا يوجد Proxy أو VPN نشط)",
                            'type': 'info',
                            'confidence': 'high'
                        })
                        
                    results['total_found'] = len(results['results'])
                    results['success'] = True
                else:
                    results['error'] = data.get('message', 'فشل البحث: عنوان IP غير صالح أو مخصص (Private IP)')
        except Exception as e:
            results['error'] = f"خطأ في الاتصال بمزود الخدمة: {str(e)}"
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
