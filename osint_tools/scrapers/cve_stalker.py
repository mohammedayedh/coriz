import sys
import os
import logging

logger = logging.getLogger(__name__)

# إضافة مسار أداة CVE-Stalker
_CVE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'external_tools', 'Coriza-Tool-Pro', 'cve-stalker'
)
if _CVE_PATH not in sys.path:
    sys.path.insert(0, _CVE_PATH)


class CVEStalkerScraper:
    """Scraper مباشر لأداة CVE-Stalker"""

    def search(self, target: str) -> dict:
        """
        البحث عن ثغرات CVE لمنتج أو جهة معينة.
        يعيد dict بصيغة متوافقة مع _process_scraper_results.
        """
        try:
            from cvestalker import search_cve

            raw_results = search_cve(
                cve_input="",
                text_input=target,
                save_to_file=False,
                quiet_mode=True
            )

            if not raw_results:
                return {
                    'success': True,
                    'target': target,
                    'total_found': 0,
                    'results': [],
                }

            # تحويل كل نتيجة إلى صيغة مقبولة من _process_scraper_results
            processed = []
            for item in raw_results:
                if not isinstance(item, dict):
                    continue

                cve_id = item.get('cve_id', '')
                cvss_data = item.get('cvss', {}) or {}
                epss_data = item.get('epss', {}) or {}

                score = cvss_data.get('baseScore', 0)
                severity = cvss_data.get('baseSeverity', 'UNKNOWN')
                epss_score = epss_data.get('epss', '0')
                epss_pct = epss_data.get('percentile', '0')

                description = (
                    f"CVSS Score: {score} ({severity}) | "
                    f"EPSS: {epss_score} (Percentile: {epss_pct}) | "
                    f"Due Date: {item.get('due_date', 'N/A')}"
                )

                processed.append({
                    'title': cve_id or f"CVE نتيجة: {target}",
                    'description': description,
                    'type': 'other',         # نوع صالح في OSINTResult
                    'confidence': 'high',
                    'url': f"https://nvd.nist.gov/vuln/detail/{cve_id}" if cve_id else '',
                    'raw': item,             # البيانات الكاملة للعرض
                    # حقول إضافية للتقرير
                    'cve_id': cve_id,
                    'severity': severity,
                    'cvss_score': score,
                })

            return {
                'success': True,
                'target': target,
                'total_found': len(processed),
                'results': processed,
            }

        except ImportError as e:
            logger.error(f"CVE-Stalker import error: {e}")
            return {
                'success': False,
                'target': target,
                'total_found': 0,
                'results': [],
                'error': f"Import Error: {e}",
            }
        except Exception as e:
            logger.error(f"CVE-Stalker search error: {e}")
            return {
                'success': False,
                'target': target,
                'total_found': 0,
                'results': [],
                'error': str(e),
            }
