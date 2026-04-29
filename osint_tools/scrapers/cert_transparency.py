"""
Certificate Transparency Scraper
البحث عن النطاقات الفرعية من خلال شهادات SSL/TLS
المصدر: crt.sh (مجاني 100%)
"""

import requests
import json
import re
from typing import List, Dict, Any
from urllib.parse import quote


class CertTransparencyScraper:
    """
    أداة للبحث في سجلات Certificate Transparency
    تستخرج جميع النطاقات الفرعية المسجلة في شهادات SSL/TLS
    """
    
    def __init__(self):
        self.base_url = "https://crt.sh"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search(self, domain: str, wildcard: bool = True) -> Dict[str, Any]:
        """
        البحث عن شهادات النطاق مع نظام بديل
        """
        results = {
            'success': False,
            'domain': domain,
            'results': [], # الحقل المطلوب للمنصة
            'total_found': 0,
            'error': None
        }
        
        # المصدر الأول: crt.sh
        try:
            search_domain = f"%.{domain}" if wildcard else domain
            params = {'q': search_domain, 'output': 'json'}
            response = self.session.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                certs = response.json()
                subdomains = set()
                for cert in certs:
                    names = cert.get('name_value', '').split('\n')
                    for n in names:
                        n = n.strip().lower().replace('*.', '')
                        if n.endswith(domain):
                            subdomains.add(n)
                
                for sub in sorted(list(subdomains)):
                    results['results'].append({
                        'title': sub,
                        'description': f"نطاق فرعي مكتشف (عبر شهادات SSL)",
                        'type': 'domain',
                        'url': f"http://{sub}"
                    })
                
                if results['results']:
                    results['success'] = True
                    results['total_found'] = len(results['results'])
                    return results
        except Exception:
            pass # فشل المصدر الأول، سننتقل للبديل

        # المصدر البديل: HackerTarget (مستقر جداً)
        try:
            fallback_url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
            response = self.session.get(fallback_url, timeout=10)
            if response.status_code == 200 and "," in response.text:
                lines = response.text.strip().split('\n')
                for line in lines:
                    parts = line.split(',')
                    if len(parts) >= 1:
                        sub = parts[0].strip().lower()
                        results['results'].append({
                            'title': sub,
                            'description': f"نطاق فرعي مكتشف (عبر DNS Lookup)",
                            'type': 'domain',
                            'url': f"http://{sub}"
                        })
                
                results['success'] = True
                results['total_found'] = len(results['results'])
        except Exception as e:
            results['error'] = f"فشل الفحص في كافة المصادر: {str(e)}"
            
        return results

import argparse

def main():
    parser = argparse.ArgumentParser(description='Cert Transparency Scraper for Coriza')
    parser.add_argument('--domain', required=True, help='Target domain')
    args = parser.parse_args()
    
    scraper = CertTransparencyScraper()
    output = scraper.search(args.domain)
    print(json.dumps(output, ensure_ascii=False))

if __name__ == "__main__":
    main()
