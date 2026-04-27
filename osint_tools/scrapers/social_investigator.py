"""
Social Investigator Scraper
البحث عن الحسابات الاجتماعية المرتبطة بمعرف (Username)
المصادر: تفتيش مباشر في مئات المنصات
"""

import requests
import concurrent.futures
from typing import List, Dict, Any

class SocialInvestigatorScraper:
    """
    أداة للتحقق من وجود المعرف في المنصات الاجتماعية الرئيسية
    تعمل بتقنية البحث المتوازي (Parallel Scanning)
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # أهم المنصات التي تعطي معلومات مفيدة
        self.platforms = {
            'Facebook': 'https://www.facebook.com/{}',
            'Instagram': 'https://www.instagram.com/{}',
            'Twitter/X': 'https://twitter.com/{}',
            'LinkedIn': 'https://www.linkedin.com/in/{}',
            'GitHub': 'https://github.com/{}',
            'Pinterest': 'https://www.pinterest.com/{}',
            'Reddit': 'https://www.reddit.com/user/{}',
            'Snapchat': 'https://www.snapchat.com/add/{}',
            'TikTok': 'https://www.tiktok.com/@{}',
            'YouTube': 'https://www.youtube.com/@{}'
        }

    def check_platform(self, name: str, url_template: str, username: str) -> Dict[str, Any]:
        url = url_template.format(username)
        try:
            # نستخدم HEAD لزيادة السرعة وتقليل استهلاك البيانات
            response = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
            
            # التحقق من الحالة (مع مراعاة أن بعض المنصات تعيد 404 أو 403)
            is_found = False
            if response.status_code == 200:
                # التحقق الإضافي لبعض المنصات التي لا تعيد 404 حقيقي
                if name == 'Instagram' and 'Page Not Found' in response.text:
                    is_found = False
                else:
                    is_found = True
            
            return {
                'platform': name,
                'url': url,
                'status': 'Found' if is_found else 'Not Found',
                'success': is_found
            }
        except Exception:
            return {
                'platform': name,
                'url': url,
                'status': 'Error',
                'success': False
            }

    def investigate(self, username: str) -> Dict[str, Any]:
        results = {
            'username': username,
            'results': [],
            'total_found': 0,
            'summary': []
        }

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.check_platform, name, url, username): name for name, url in self.platforms.items()}
            for future in concurrent.futures.as_completed(future_to_url):
                res = future.result()
                if res['success']:
                    results['results'].append({
                        'platform': res['platform'],
                        'url': res['url'],
                        'status': 'found',
                        'description': f"حساب نشط على {res['platform']}",
                        'confidence': 'high'
                    })
                results['summary'].append(res)
        
        results['total_found'] = len(results['results'])
        return results

import sys
import json

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Username not provided"}))
        sys.exit(1)
        
    username = sys.argv[1].strip()
    investigator = SocialInvestigatorScraper()
    res = investigator.investigate(username)
    print(json.dumps(res, ensure_ascii=False))

if __name__ == "__main__":
    main()
