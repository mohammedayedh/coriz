"""
GitHub OSINT Scraper
جمع معلومات من GitHub عبر API العام (بدون API key)
المصدر: api.github.com (مجاني - 60 طلب/ساعة)
"""

import requests
import json
import argparse
from typing import Dict, Any, List


class GitHubOSINT:
    def __init__(self):
        self.api_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; OSINT-Tool/1.0)',
            'Accept': 'application/vnd.github.v3+json',
        })

    def get_user_info(self, username: str) -> Dict[str, Any]:
        results = {
            'success': False,
            'username': username,
            'results': [],
            'total_found': 0,
            'error': None
        }

        try:
            # جلب معلومات المستخدم
            user_url = f"{self.api_url}/users/{username}"
            response = self.session.get(user_url, timeout=15)

            if response.status_code == 404:
                results['error'] = 'المستخدم غير موجود على GitHub'
                # نعيد نتيجة واحدة بدلاً من الفشل الكامل
                results['results'].append({
                    'title': f"GitHub: {username}",
                    'description': 'لم يتم العثور على هذا المستخدم على GitHub',
                    'type': 'profile',
                    'confidence': 'low',
                    'url': f"https://github.com/{username}"
                })
                results['total_found'] = 1
                results['success'] = True
                return results

            if response.status_code == 403:
                # Rate limit - نعيد نتيجة بسيطة
                results['results'].append({
                    'title': f"GitHub Profile: {username}",
                    'description': 'تم تجاوز حد الطلبات، جرب لاحقاً',
                    'type': 'profile',
                    'confidence': 'low',
                    'url': f"https://github.com/{username}"
                })
                results['total_found'] = 1
                results['success'] = True
                return results

            if response.status_code != 200:
                results['error'] = f"خطأ HTTP: {response.status_code}"
                return results

            user_data = response.json()

            # معلومات الملف الشخصي
            name = user_data.get('name') or username
            bio = user_data.get('bio') or 'لا يوجد وصف'
            location = user_data.get('location') or 'غير محدد'
            company = user_data.get('company') or 'غير محدد'
            blog = user_data.get('blog') or ''
            followers = user_data.get('followers', 0)
            following = user_data.get('following', 0)
            public_repos = user_data.get('public_repos', 0)
            created_at = user_data.get('created_at', '')[:10] if user_data.get('created_at') else ''

            results['results'].append({
                'title': f"GitHub Profile: {name}",
                'description': f"Bio: {bio} | الموقع: {location} | الشركة: {company}",
                'type': 'profile',
                'confidence': 'high',
                'url': f"https://github.com/{username}"
            })

            results['results'].append({
                'title': "إحصائيات GitHub",
                'description': f"المتابعون: {followers} | يتابع: {following} | المستودعات: {public_repos} | تاريخ الإنشاء: {created_at}",
                'type': 'stats',
                'confidence': 'high',
                'url': f"https://github.com/{username}?tab=repositories"
            })

            if blog:
                results['results'].append({
                    'title': "الموقع الشخصي",
                    'description': f"رابط الموقع: {blog}",
                    'type': 'website',
                    'confidence': 'high',
                    'url': blog if blog.startswith('http') else f"https://{blog}"
                })

            # جلب المستودعات العامة
            repos_url = f"{self.api_url}/users/{username}/repos?sort=updated&per_page=5"
            repos_response = self.session.get(repos_url, timeout=10)
            if repos_response.status_code == 200:
                repos = repos_response.json()
                for repo in repos[:5]:
                    stars = repo.get('stargazers_count', 0)
                    lang = repo.get('language') or 'غير محدد'
                    results['results'].append({
                        'title': f"مستودع: {repo.get('name')}",
                        'description': f"{repo.get('description') or 'لا يوجد وصف'} | اللغة: {lang} | النجوم: {stars}",
                        'type': 'repository',
                        'confidence': 'high',
                        'url': repo.get('html_url', '')
                    })

            results['total_found'] = len(results['results'])
            results['success'] = True

        except requests.exceptions.Timeout:
            results['error'] = 'انتهت مهلة الاتصال بـ GitHub'
            results['results'].append({
                'title': f"GitHub: {username}",
                'description': 'تعذر الاتصال بـ GitHub API في الوقت المحدد',
                'type': 'profile',
                'confidence': 'low',
                'url': f"https://github.com/{username}"
            })
            results['total_found'] = 1
            results['success'] = True
        except Exception as e:
            results['error'] = str(e)
            results['results'].append({
                'title': f"GitHub: {username}",
                'description': f"خطأ في الاتصال: {str(e)[:100]}",
                'type': 'profile',
                'confidence': 'low',
                'url': f"https://github.com/{username}"
            })
            results['total_found'] = 1
            results['success'] = True

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
