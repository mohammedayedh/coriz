"""
Reverse Image Search Scraper
البحث العكسي عن الصور في محركات متعددة
المصدر: Google Images, Yandex, TinEye (مجاني)
"""

import requests
import json
import argparse
from typing import Dict, Any, List
from urllib.parse import urlencode

class ReverseImageSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.engines = {
            'google': 'https://www.google.com/searchbyimage',
            'yandex': 'https://yandex.com/images/search',
            'tineye': 'https://tineye.com/search',
            'bing': 'https://www.bing.com/images/search'
        }

    def search_by_url(self, image_url: str) -> Dict[str, Any]:
        results = {'success': False, 'image_url': image_url, 'results': [], 'total_found': 0, 'error': None}
        try:
            # محركات البحث تولد روابط بحث مباشرة
            for engine, base_url in self.engines.items():
                params = {}
                if engine == 'google': params = {'image_url': image_url}
                elif engine == 'yandex': params = {'rpt': 'imageview', 'url': image_url}
                elif engine == 'tineye': params = {'url': image_url}
                elif engine == 'bing': params = {'view': 'detailv2', 'iss': 'sbi', 'q': f'imgurl:{image_url}'}
                
                search_url = f"{base_url}?{urlencode(params)}"
                results['results'].append({
                    'title': f"نتائج {engine.capitalize()}",
                    'description': f"البحث العكسي عن الصورة في محرك {engine}",
                    'url': search_url,
                    'type': 'reverse_search',
                    'confidence': 'high'
                })
            
            results['total_found'] = len(results['results'])
            results['success'] = True
        except Exception as e:
            results['error'] = str(e)
        return results

def main():
    parser = argparse.ArgumentParser(description='Reverse Image Search Tool for Coriza')
    parser.add_argument('--url', required=True, help='Image URL to Search')
    args = parser.parse_args()
    
    searcher = ReverseImageSearcher()
    output = searcher.search_by_url(args.url)
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
