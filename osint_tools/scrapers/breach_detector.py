"""
Breach Detector Scraper
البحث عن تسريبات البيانات المرتبطة بالبريد الإلكتروني
المصادر: LeakCheck / BreachDirectory (Public Lookups)
"""

import requests
import json
import argparse
import re
from typing import List, Dict, Any

class BreachDetectorScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })

    def search_email(self, email: str) -> Dict[str, Any]:
        results = {'success': False, 'email': email, 'results': [], 'total_found': 0, 'error': None}
        try:
            lc_url = f"https://leakcheck.io/api/public?check={email}"
            response = self.session.get(lc_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    for source in data.get('sources', []):
                        results['results'].append({
                            'title': f"تسريب بيانات: {source.get('name')}",
                            'description': f"المصدر: {source.get('name')} | التاريخ: {source.get('date', 'Unknown')}",
                            'type': 'data_leak',
                            'confidence': 'high'
                        })
                    results['success'] = True
                    results['total_found'] = len(results['results'])
            else:
                results['error'] = "فشل الاتصال بمصدر البيانات"
        except Exception as e:
            results['error'] = str(e)
        return results

def main():
    parser = argparse.ArgumentParser(description='Breach Detector Tool for Coriza')
    parser.add_argument('--email', required=True, help='Target Email to Check')
    args = parser.parse_args()
    
    detector = BreachDetectorScraper()
    output = detector.search_email(args.email)
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
