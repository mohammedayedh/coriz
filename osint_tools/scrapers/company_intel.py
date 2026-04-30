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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
            search_url = f"{self.base_url}/companies?q={urllib.parse.quote(name)}"
            response = requests.get(search_url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            company_list = soup.select('ul.company_list li')
            
            for item in company_list:
                company_name = item.select_one('a.company_search_result')
                if not company_name: continue
                
                details = {
                    'title': company_name.text.strip(),
                    'url': self.base_url + company_name['href'],
                    'id': item.select_one('.company_number').text.strip() if item.select_one('.company_number') else 'Unknown',
                    'jurisdiction': item.select_one('.jurisdiction').text.strip() if item.select_one('.jurisdiction') else 'Unknown',
                    'status': item.select_one('.status').text.strip() if item.select_one('.status') else 'Unknown',
                    'description': f"رقم الشركة: {item.select_one('.company_number').text.strip() if item.select_one('.company_number') else 'غير معروف'} | الحالة: {item.select_one('.status').text.strip() if item.select_one('.status') else 'غير معروف'}"
                }
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
