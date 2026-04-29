"""
Google Dorks Scraper
البحث المتقدم في Google لاكتشاف معلومات حساسة
المصدر: Google Search (مجاني)
"""

import requests
import time
import random
import json
import argparse
from typing import List, Dict, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

class GoogleDorksScraper:
    def __init__(self):
        self.base_url = "https://www.google.com/search"
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

    def search(self, dork: str, num_results: int = 10) -> Dict[str, Any]:
        results = {'success': False, 'results': [], 'total_found': 0, 'error': None}
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            params = {'q': dork, 'num': num_results, 'hl': 'en'}
            response = self.session.get(self.base_url, params=params, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                search_results = soup.find_all('div', class_='g')
                
                for result in search_results:
                    title_elem = result.find('h3')
                    link_elem = result.find('a')
                    desc_elem = result.find('div', class_=['VwiC3b', 'yXK7lf'])
                    
                    if title_elem and link_elem:
                        results['results'].append({
                            'title': title_elem.text,
                            'url': link_elem['href'],
                            'description': desc_elem.text if desc_elem else "لا يوجد وصف",
                            'type': 'other'
                        })
                
                results['total_found'] = len(results['results'])
                results['success'] = True
            else:
                results['error'] = f"فشل البحث (Status: {response.status_code})"
        except Exception as e:
            results['error'] = str(e)
        return results

def main():
    parser = argparse.ArgumentParser(description='Google Dorks Tool for Coriza')
    parser.add_argument('--target', required=True, help='Target Dork or Domain')
    args = parser.parse_args()
    
    scraper = GoogleDorksScraper()
    # إذا كان المدخل نطاقاً بسيطاً، سنستخدم dork افتراضي للبحث عن الملفات
    dork = args.target
    if '.' in dork and ' ' not in dork and ':' not in dork:
        dork = f"site:{dork} filetype:pdf OR filetype:doc OR filetype:xls"
    
    output = scraper.search(dork)
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
