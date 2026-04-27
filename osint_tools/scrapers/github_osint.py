"""
GitHub OSINT Scraper
جمع معلومات من GitHub بدون API
المصدر: GitHub Public Pages (مجاني 100%)
"""

import requests
import re
import json
import argparse
from typing import Dict, Any, List
from bs4 import BeautifulSoup

class GitHubOSINT:
    def __init__(self):
        self.base_url = "https://github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        results = {'success': False, 'username': username, 'results': [], 'total_found': 0, 'error': None}
        try:
            url = f"{self.base_url}/{username}"
            response = self.session.get(url, timeout=20)
            if response.status_code != 200:
                results['error'] = 'المستخدم غير موجود'
                return results
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Profile Card
            name = soup.find('span', {'itemprop': 'name'})
            bio = soup.find('div', {'data-bio-text': True})
            results['results'].append({
                'title': f"الملف الشخصي: {name.text.strip() if name else username}",
                'description': bio.text.strip() if bio else "لا يوجد وصف",
                'type': 'profile',
                'confidence': 'high'
            })
            
            # Stats
            followers = soup.find('a', href=re.compile(r'\?tab=followers'))
            if followers:
                count = followers.find('span', class_='text-bold')
                results['results'].append({
                    'title': "إحصائيات المتابعة",
                    'description': f"المتابعون: {count.text.strip() if count else '0'}",
                    'type': 'stats',
                    'confidence': 'high'
                })
            
            # Repositories
            repo_list = soup.find_all('div', {'itemprop': 'owns'})
            for repo in repo_list[:5]:
                repo_name = repo.find('a', {'itemprop': 'name codeRepository'})
                if repo_name:
                    results['results'].append({
                        'title': f"مستودع: {repo_name.text.strip()}",
                        'url': f"{self.base_url}{repo_name.get('href')}",
                        'type': 'repository',
                        'confidence': 'high'
                    })
            
            results['total_found'] = len(results['results'])
            results['success'] = True
        except Exception as e:
            results['error'] = str(e)
        return results

def main():
    parser = argparse.ArgumentParser(description='GitHub OSINT Tool')
    parser.add_argument('--username', required=True, help='Target Username')
    args = parser.parse_args()
    scraper = GitHubOSINT()
    output = scraper.get_user_info(args.username)
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
