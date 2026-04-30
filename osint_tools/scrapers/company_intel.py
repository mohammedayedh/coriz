"""
Company Intelligence Scraper
استخراج معلومات الشركات والسجلات القانونية
المصدر: OpenCorporates (أكبر قاعدة بيانات شركات مفتوحة)
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import urllib.parse

class CompanyIntelScraper:
    """
    أداة لاستخراج بيانات الشركات المسجلة قانونياً
    تستخرج العناوين، الملاك، والحالة القانونية
    """
    
    def __init__(self):
        self.base_url = "https://opencorporates.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

    def search_company(self, name: str) -> Dict[str, Any]:
        results = {
            'success': False,
            'query': name,
            'results': [],
            'total_results': 0,
            'error': None
        }

        try:
            session = requests.Session()
            search_url = f"{self.base_url}/companies?q={urllib.parse.quote(name)}"
            response = session.get(search_url, headers=self.headers, timeout=25)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # محاولة البحث عن النتائج بعدة طرق (Selectors)
            company_items = soup.select('ul.company_list li') or soup.select('table#companies tr')
            
            if not company_items and "challenge" in response.text.lower():
                raise Exception("الموقع يطلب التحقق (Bot Challenge) - يرجى المحاولة لاحقاً")

            for item in company_items:
                link_el = item.select_one('a.company_search_result') or item.select_one('td a')
                if not link_el or not link_el.get('href'): continue
                
                details = {
                    'title': link_el.text.strip(),
                    'url': self.base_url + link_el['href'] if not link_el['href'].startswith('http') else link_el['href'],
                    'id': 'Unknown',
                    'jurisdiction': 'Unknown',
                    'status': 'Unknown'
                }
                
                # استخراج المعرف والحالة
                id_el = item.select_one('.company_number') or item.select_one('.id')
                if id_el: details['id'] = id_el.text.strip()
                
                jur_el = item.select_one('.jurisdiction')
                if jur_el: details['jurisdiction'] = jur_el.text.strip()
                
                status_el = item.select_one('.status')
                if status_el: details['status'] = status_el.text.strip()

                details['description'] = f"المعرف: {details['id']} | الولاية/الدولة: {details['jurisdiction']} | الحالة: {details['status']}"
                results['results'].append(details)

            results['total_results'] = len(results['results'])
            results['success'] = True
            
        except Exception as e:
            results['error'] = str(e)
            
        return results

import sys
import json

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Company name not provided"}))
        sys.exit(1)
        
    query = sys.argv[1].strip()
    intel = CompanyIntelScraper()
    res = intel.search_company(query)
    print(json.dumps(res, ensure_ascii=False))

if __name__ == "__main__":
    main()
