"""
Wayback Machine Scraper
البحث في أرشيف المواقع القديمة
المصدر: Archive.org (مجاني 100%)
"""

import requests
import json
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import quote


class WaybackMachineScraper:
    """
    أداة للبحث في أرشيف Wayback Machine
    تستخرج النسخ القديمة من المواقع والتغييرات التاريخية
    """
    
    def __init__(self):
        self.base_url = "https://web.archive.org"
        self.api_url = f"{self.base_url}/cdx/search/cdx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_snapshots(self, url: str, limit: int = 100) -> Dict[str, Any]:
        """
        البحث عن نسخ محفوظة من الموقع باستخدام CDX API
        """
        results = {
            'success': False,
            'url': url,
            'results': [], # الحقل المطلوب للمنصة
            'total_found': 0,
            'error': None
        }
        
        try:
            # تنظيف الرابط
            clean_url = url.replace('http://', '').replace('https://', '').strip('/')
            
            # محاولة جلب البيانات من CDX
            params = {
                'url': clean_url,
                'output': 'json',
                'limit': limit,
                'fl': 'timestamp,original,statuscode,mimetype',
                'collapse': 'timestamp:8' # نتيجة واحدة لكل يوم لتقليل التكرار
            }
            
            response = self.session.get(self.api_url, params=params, timeout=20)
            
            if response.status_code != 200:
                # محاولة بديلة بدون تصفية
                params.pop('collapse')
                response = self.session.get(self.api_url, params=params, timeout=20)

            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    for row in data[1:]:
                        ts, orig, status, mime = row
                        dt = datetime.strptime(ts, '%Y%m%d%H%M%S')
                        
                        item = {
                            'title': f"نسخة مؤرشفة - {dt.strftime('%Y-%m-%d')}",
                            'description': f"نوع الملف: {mime} | الحالة: {status}",
                            'url': f"https://web.archive.org/web/{ts}/{orig}",
                            'type': 'archive',
                            'timestamp': ts
                        }
                        results['results'].append(item)
                    
                    results['total_found'] = len(results['results'])
                    results['success'] = True
                else:
                    results['error'] = "لم يتم العثور على أرشيف لهذا النطاق"
            else:
                results['error'] = f"فشل الاتصال بالأرشيف (Status: {response.status_code})"
                
        except Exception as e:
            results['error'] = f"حدث خطأ أثناء الفحص: {str(e)}"
        
        return results

import argparse

def main():
    parser = argparse.ArgumentParser(description='Wayback Machine Scraper for Coriza')
    parser.add_argument('--url', required=True, help='Target URL')
    args = parser.parse_args()
    
    scraper = WaybackMachineScraper()
    output = scraper.search_snapshots(args.url)
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
