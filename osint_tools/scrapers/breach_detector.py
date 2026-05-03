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
            # استخدام واجهة XposedOrNot الموثوقة والمجانية
            xon_url = f"https://api.xposedornot.com/v1/check-email/{email}"
            response = self.session.get(xon_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                breaches = data.get('breaches', [])
                
                if breaches:
                    results['results'].append({
                        'title': f"⚠️ حالة التسريب: تم الاختراق (Pwned)",
                        'description': f"تم العثور على هذا البريد في {len(breaches)} قاعدة بيانات مسربة.",
                        'type': 'security_alert',
                        'confidence': 'high'
                    })
                    
                    # عرض تفاصيل التسريبات (بحد أقصى 15 مصدر للحفاظ على التنسيق)
                    for source in breaches[:15]:
                        results['results'].append({
                            'title': f"تسريب بيانات: {source}",
                            'description': f"المصدر المسرب: {source} | يُنصح بتغيير كلمة المرور المرتبطة بهذا الموقع فوراً.",
                            'type': 'leak',
                            'confidence': 'high'
                        })
                    
                    if len(breaches) > 15:
                        results['results'].append({
                            'title': "مزيد من التسريبات...",
                            'description': f"يوجد {len(breaches) - 15} تسريباً إضافياً لم يتم عرضها لتجنب الإطالة.",
                            'type': 'info',
                            'confidence': 'high'
                        })
                else:
                    results['results'].append({
                        'title': "حالة التسريب: آمن",
                        'description': "لم يتم العثور على هذا البريد في أي تسريبات بيانات عامة.",
                        'type': 'info',
                        'confidence': 'high'
                    })
                    
                results['success'] = True
                results['total_found'] = len(results['results'])
            elif response.status_code == 404:
                # 404 في XposedOrNot تعني أن الإيميل غير موجود في قاعدة التسريبات (آمن)
                results['results'].append({
                    'title': "حالة التسريب: آمن (Clear)",
                    'description': "لم يتم العثور على هذا البريد في أي تسريبات بيانات عامة.",
                    'type': 'info',
                    'confidence': 'high'
                })
                results['success'] = True
                results['total_found'] = 1
            else:
                results['error'] = f"فشل الاتصال بمصدر البيانات (Status: {response.status_code})"
        except Exception as e:
            results['error'] = f"خطأ غير متوقع: {str(e)}"
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
