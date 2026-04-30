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
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]

    def search(self, dork: str, num_results: int = 20) -> Dict[str, Any]:
        results = {'success': False, 'results': [], 'total_found': 0, 'error': None}
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            params = {'q': dork, 'num': num_results, 'hl': 'en', 'safe': 'off'}
            response = self.session.get(self.base_url, params=params, headers=headers, timeout=25)
            
            if response.status_code == 200:
                if "captcha" in response.text.lower() or "google.com/sorry" in response.text:
                    results['error'] = "تم اكتشاف نشاط غير عادي من جوجل (Captcha). يرجى المحاولة لاحقاً."
                    return results

                soup = BeautifulSoup(response.text, 'html.parser')
                
                # البحث عن حاويات النتائج بعدة طرق
                search_results = soup.select('div.g') or soup.select('div.tF2Cxc') or soup.select('div.yuRUbf')
                
                if not search_results:
                    # محاولة البحث في النسخة المبسطة
                    search_results = soup.find_all('div', class_='ZINvNe')

                for result in search_results:
                    title_elem = result.select_one('h3')
                    link_elem = result.select_one('a')
                    
                    # محاولة العثور على الوصف بعدة طرق
                    desc_elem = result.select_one('div.VwiC3b') or result.select_one('div.kb0Bdb') or result.select_one('div.st')
                    
                    if title_elem and link_elem and link_elem.get('href'):
                        url = link_elem['href']
                        # تنظيف الرابط إذا كان من النسخة المبسطة (/url?q=...)
                        if url.startswith('/url?q='):
                            url = url.split('=')[1].split('&')[0]
                        
                        if not url.startswith('http'): continue

                        results['results'].append({
                            'title': title_elem.text.strip(),
                            'url': url,
                            'description': desc_elem.text.strip() if desc_elem else "لا يوجد وصف متاح",
                            'type': 'website'
                        })
                
                results['total_found'] = len(results['results'])
                results['success'] = True
            else:
                results['error'] = f"خطأ من جوجل (Status: {response.status_code})"
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
