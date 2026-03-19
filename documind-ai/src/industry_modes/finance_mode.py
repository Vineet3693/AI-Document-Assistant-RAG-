"""
Finance Mode - Special handling for financial documents
Extracts financial metrics, KPIs, risk factors, and trends
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class FinanceMode:
    """Specialized processing for financial documents"""
    
    def __init__(self):
        self.financial_patterns = {
            'revenue': [r'revenue[:\s]*\$?([\d,\.]+)', r'total revenue[:\s]*\$?([\d,\.]+)'],
            'profit': [r'net profit[:\s]*\$?([\d,\.]+)', r'net income[:\s]*\$?([\d,\.]+)'],
            'margin': [r'profit margin[:\s]*([\d\.]+)%', r'gross margin[:\s]*([\d\.]+)%'],
            'assets': [r'total assets[:\s]*\$?([\d,\.]+)', r'assets[:\s]*\$?([\d,\.]+)'],
            'liabilities': [r'total liabilities[:\s]*\$?([\d,\.]+)', r'liabilities[:\s]*\$?([\d,\.]+)'],
            'cash': [r'cash[:\s]*\$?([\d,\.]+)', r'cash equivalents[:\s]*\$?([\d,\.]+)'],
            'eps': [r'EPS[:\s]*\$?([\d\.]+)', r'earnings per share[:\s]*\$?([\d\.]+)'],
        }
        
    def extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """Extract key financial metrics from document"""
        metrics = {}
        
        for metric, patterns in self.financial_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(',', '')
                    try:
                        metrics[metric] = float(value)
                    except ValueError:
                        metrics[metric] = value
                    break
        
        return metrics
    
    def detect_risk_factors(self, text: str) -> List[Dict[str, str]]:
        """Detect risk factors mentioned in financial documents"""
        risk_keywords = [
            'risk factor', 'uncertainty', 'volatility', 'decline', 'loss',
            'adverse', 'negative impact', 'regulatory concern', 'litigation',
            'market risk', 'credit risk', 'liquidity risk', 'operational risk'
        ]
        
        risks = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            for keyword in risk_keywords:
                if keyword in sentence_lower and len(sentence) > 20:
                    risks.append({
                        'text': sentence.strip() + '.',
                        'keyword': keyword,
                        'severity': self._assess_severity(sentence, keyword)
                    })
                    break
        
        return risks[:10]  # Return top 10 risks
    
    def _assess_severity(self, text: str, keyword: str) -> str:
        """Assess severity of risk based on context"""
        text_lower = text.lower()
        high_severity_words = ['critical', 'severe', 'material', 'significant', 'substantial']
        medium_severity_words = ['moderate', 'potential', 'possible', 'may']
        
        for word in high_severity_words:
            if word in text_lower:
                return 'HIGH'
        
        for word in medium_severity_words:
            if word in text_lower:
                return 'MEDIUM'
        
        return 'LOW'
    
    def identify_kpis(self, text: str) -> List[Dict[str, Any]]:
        """Identify Key Performance Indicators"""
        kpi_patterns = [
            (r'year-over-year growth[:\s]*([\d\.]+)%', 'YoY Growth'),
            (r'quarterly growth[:\s]*([\d\.]+)%', 'Quarterly Growth'),
            (r'return on equity[:\s]*([\d\.]+)%', 'ROE'),
            (r'return on assets[:\s]*([\d\.]+)%', 'ROA'),
            (r'debt-to-equity[:\s]*([\d\.]+)', 'Debt-to-Equity'),
            (r'current ratio[:\s]*([\d\.]+)', 'Current Ratio'),
            (r'operating margin[:\s]*([\d\.]+)%', 'Operating Margin'),
        ]
        
        kpis = []
        for pattern, name in kpi_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                kpis.append({
                    'name': name,
                    'value': match.group(1),
                    'unit': '%' if '%' in match.group(0) else 'ratio'
                })
        
        return kpis
    
    def analyze_trends(self, text: str) -> List[Dict[str, str]]:
        """Analyze financial trends mentioned in document"""
        trend_indicators = {
            'increasing': ['increased', 'grew', 'rose', 'improved', 'gained', 'upward'],
            'decreasing': ['decreased', 'declined', 'fell', 'dropped', 'reduced', 'downward'],
            'stable': ['stable', 'consistent', 'steady', 'unchanged', 'flat'],
            'volatile': ['volatile', 'fluctuating', 'erratic', 'unpredictable']
        }
        
        trends = []
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for trend_type, indicators in trend_indicators.items():
                for indicator in indicators:
                    if indicator in sentence_lower and len(sentence) > 30:
                        trends.append({
                            'trend': trend_type,
                            'indicator': indicator,
                            'context': sentence.strip() + '.'
                        })
                        break
        
        return trends[:5]
    
    def generate_financial_summary(self, text: str, company_name: str = "") -> Dict[str, Any]:
        """Generate comprehensive financial summary"""
        metrics = self.extract_financial_metrics(text)
        risks = self.detect_risk_factors(text)
        kpis = self.identify_kpis(text)
        trends = self.analyze_trends(text)
        
        # Calculate overall health score
        health_score = self._calculate_health_score(metrics, risks, kpis)
        
        return {
            'company_name': company_name,
            'metrics': metrics,
            'kpis': kpis,
            'risks': risks,
            'trends': trends,
            'health_score': health_score,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_health_score(self, metrics: Dict, risks: List, kpis: List) -> int:
        """Calculate overall financial health score (0-100)"""
        score = 70  # Base score
        
        # Adjust based on metrics
        if metrics.get('profit', 0) > 0:
            score += 10
        if metrics.get('margin', 0) > 15:
            score += 10
        
        # Deduct for risks
        high_risks = sum(1 for r in risks if r.get('severity') == 'HIGH')
        score -= high_risks * 5
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def get_prompt_template(self) -> str:
        """Return the financial analysis prompt template"""
        return """You are a CFA-level financial analyst who extracts critical insights from financial documents.

COMPANY: {company_name}
REPORT TYPE: {report_type}
PERIOD: {report_period}

DOCUMENT CONTENT:
{document_text}

Generate a comprehensive financial analysis including:
1. Key Financial Metrics (Revenue, Profit, Margins, Assets, Liabilities, Cash, EPS)
2. Performance Highlights (Strengths and Concerns)
3. Risk Factors Mentioned
4. Management Guidance (if any)
5. Key Insights for Decision Makers

Be precise, numbers-focused, and grounded in the document only."""
