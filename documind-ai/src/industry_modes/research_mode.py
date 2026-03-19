"""
Research Mode - Academic paper analysis and research document processing
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class ResearchMode:
    """Specialized processing for academic and research papers"""
    
    def __init__(self):
        self.research_sections = [
            'abstract', 'introduction', 'methodology', 'methods', 'results',
            'discussion', 'conclusion', 'references', 'bibliography',
            'literature review', 'experimental', 'analysis', 'findings'
        ]
        
        self.statistical_terms = [
            'p-value', 'confidence interval', 'standard deviation', 'mean',
            'median', 'correlation', 'regression', 'anova', 't-test',
            'chi-square', 'sample size', 'n=', 'significance'
        ]
        
        self.research_types = [
            'experimental', 'observational', 'qualitative', 'quantitative',
            'meta-analysis', 'systematic review', 'case study', 'survey',
            'longitudinal', 'cross-sectional', 'randomized controlled trial'
        ]
    
    def analyze_paper(self, text: str) -> Dict[str, Any]:
        """Comprehensive analysis of research paper"""
        return {
            'metadata': self._extract_metadata(text),
            'research_question': self._identify_research_question(text),
            'methodology': self._extract_methodology(text),
            'key_findings': self._extract_findings(text),
            'statistics': self._extract_statistics(text),
            'limitations': self._extract_limitations(text),
            'future_work': self._extract_future_work(text),
            'plain_summary': self._generate_plain_summary(text),
            'impact_assessment': self._assess_impact(text)
        }
    
    def _extract_metadata(self, text: str) -> Dict[str, str]:
        """Extract paper metadata"""
        metadata = {}
        
        # Title (first line or after "Title:")
        title_match = re.search(r'(?:title[:\s]+)?([A-Z][^.\n]{20,100})', text, re.IGNORECASE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Authors
        author_match = re.search(r'(?:authors?|by)[:\s]+([^.\n]+)', text, re.IGNORECASE)
        if author_match:
            metadata['authors'] = author_match.group(1).strip()
        
        # Journal/Publication
        journal_match = re.search(r'(?:published in|journal|conference)[:\s]+([^.\n]+)', text, re.IGNORECASE)
        if journal_match:
            metadata['publication'] = journal_match.group(1).strip()
        
        # Date/Year
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            metadata['year'] = year_match.group(0)
        
        # DOI
        doi_match = re.search(r'10\.\d{4,}/[\S]+', text)
        if doi_match:
            metadata['doi'] = doi_match.group(0)
        
        return metadata
    
    def _identify_research_question(self, text: str) -> str:
        """Identify the main research question"""
        # Look for question patterns
        patterns = [
            r'(?:we investigate|this study examines|our research asks)[:\s]+(.+?)(?:\.|\n)',
            r'(?:the goal|the aim|the purpose)[:\s]+(?:is to|was to)\s+(.+?)(?:\.|\n)',
            r'(?:research question|hypothesis)[:\s]+(.+?)(?:\.|\n)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: first sentence of abstract/introduction
        abstract_match = re.search(r'abstract[:\s]+(.+?)(?:\n\s*\n|introduction)', text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            sentences = abstract_match.group(1).split('.')
            if sentences:
                return sentences[0].strip() + '.'
        
        return "Not explicitly stated"
    
    def _extract_methodology(self, text: str) -> Dict[str, Any]:
        """Extract methodology details"""
        methodology = {
            'type': self._identify_research_type(text),
            'sample_size': self._extract_sample_size(text),
            'tools': self._extract_tools(text),
            'procedure': self._extract_procedure(text)
        }
        
        return methodology
    
    def _identify_research_type(self, text: str) -> str:
        """Identify the type of research conducted"""
        text_lower = text.lower()
        
        for rtype in self.research_types:
            if rtype in text_lower:
                return rtype.title()
        
        return "Not specified"
    
    def _extract_sample_size(self, text: str) -> Optional[int]:
        """Extract sample size from text"""
        patterns = [
            r'(?:n|sample size|participants|subjects)[:\s]*(\d+)',
            r'\bn\s*=\s*(\d+)\b',
            r'(\d+)\s*(?:participants|subjects|patients|respondents)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_tools(self, text: str) -> List[str]:
        """Extract tools, software, or instruments used"""
        tools = []
        
        # Software patterns
        software_patterns = [
            r'\b(SPSS|R|Python|MATLAB|Stata|SAS|Excel)\b',
            r'\b(TensorFlow|PyTorch|Keras|Scikit-learn)\b',
        ]
        
        for pattern in software_patterns:
            matches = re.findall(pattern, text)
            tools.extend(matches)
        
        return list(set(tools))[:10]
    
    def _extract_procedure(self, text: str) -> str:
        """Extract brief procedure description"""
        # Look for methodology section
        method_match = re.search(r'(?:methodology|methods)[:\s]+(.+?)(?:\n\s*\n|results|discussion)', text, re.IGNORECASE | re.DOTALL)
        if method_match:
            content = method_match.group(1)
            # Return first 300 chars as summary
            return content[:300].strip() + "..." if len(content) > 300 else content.strip()
        
        return "Procedure not detailed"
    
    def _extract_findings(self, text: str) -> List[str]:
        """Extract key findings"""
        findings = []
        
        # Look for results/findings section
        results_match = re.search(r'(?:results|findings)[:\s]+(.+?)(?:\n\s*\n|discussion|conclusion)', text, re.IGNORECASE | re.DOTALL)
        
        if results_match:
            content = results_match.group(1)
            sentences = content.split('.')
            
            # Take significant sentences
            for sentence in sentences[:10]:
                sentence = sentence.strip()
                if len(sentence) > 30 and any(word in sentence.lower() for word in ['significant', 'found', 'showed', 'demonstrated', 'revealed']):
                    findings.append(sentence + '.')
        
        return findings[:5]
    
    def _extract_statistics(self, text: str) -> List[Dict[str, str]]:
        """Extract statistical information"""
        stats = []
        
        for term in self.statistical_terms:
            # Find mentions with values
            pattern = rf'{term}[:\s]*=?\s*([\d\.\-]+%?)'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                stats.append({
                    'metric': term,
                    'value': match.group(1),
                    'context': match.group(0)[:100]
                })
        
        return stats[:10]
    
    def _extract_limitations(self, text: str) -> List[str]:
        """Extract study limitations"""
        limitations = []
        
        # Look for limitations section or mentions
        patterns = [
            r'(?:limitations?|constraints?|weaknesses?)[:\s]+(.+?)(?:\n\s*\n|conclusion|references)',
            r'(?:limited by|constraint|weakness)[:\s]+(.+?)(?:\.|\n)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1)
                sentences = content.split('.')
                limitations.extend([s.strip() + '.' for s in sentences if len(s.strip()) > 20][:3])
                break
        
        # Also look for "however" statements that indicate limitations
        however_matches = re.findall(r'[Hh]owever, .+?(?:\.|\n)', text)
        limitations.extend([m.strip() for m in however_matches[:2]])
        
        return limitations[:5]
    
    def _extract_future_work(self, text: str) -> List[str]:
        """Extract suggestions for future research"""
        future_work = []
        
        patterns = [
            r'(?:future work|future research|further studies?)[:\s]+(.+?)(?:\n\s*\n|references|$)',
            r'(?:should|could|would) be (?:studied|investigated|examined)[^\n.]+',
            r'[Ff]uture (?:work|research|studies?) (?:should|could|will)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(0)
                sentences = content.split('.')
                future_work.extend([s.strip() + '.' for s in sentences if len(s.strip()) > 20][:3])
                break
        
        return future_work[:3]
    
    def _generate_plain_summary(self, text: str) -> str:
        """Generate plain English summary for non-experts"""
        # Extract abstract if available
        abstract_match = re.search(r'abstract[:\s]+(.+?)(?:\n\s*\n|introduction)', text, re.IGNORECASE | re.DOTALL)
        
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Simplify language
            simplified = abstract
            complex_terms = {
                'utilize': 'use',
                'demonstrate': 'show',
                'indicate': 'suggest',
                'subsequently': 'then',
                'approximately': 'about',
                'methodology': 'method',
                'facilitate': 'help',
            }
            
            for complex, simple in complex_terms.items():
                simplified = simplified.replace(complex, simple)
            
            return simplified[:300] + "..." if len(simplified) > 300 else simplified
        
        return "Summary not available"
    
    def _assess_impact(self, text: str) -> Dict[str, str]:
        """Assess potential real-world impact"""
        impact_keywords = {
            'high': ['breakthrough', 'novel', 'first', 'unprecedented', 'revolutionary'],
            'medium': ['improves', 'enhances', 'advances', 'contributes', 'extends'],
            'low': ['confirms', 'validates', 'replicates', 'supports']
        }
        
        text_lower = text.lower()
        
        for level, keywords in impact_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return {
                        'level': level.upper(),
                        'indicator': keyword,
                        'description': self._get_impact_description(level)
                    }
        
        return {
            'level': 'UNKNOWN',
            'indicator': 'none found',
            'description': 'Impact assessment inconclusive'
        }
    
    def _get_impact_description(self, level: str) -> str:
        """Get description for impact level"""
        descriptions = {
            'high': 'Potentially groundbreaking research with significant implications',
            'medium': 'Meaningful contribution that advances the field',
            'low': 'Incremental improvement or validation of existing work'
        }
        return descriptions.get(level, 'Unknown impact')
    
    def compare_papers(self, paper1_text: str, paper2_text: str) -> Dict[str, Any]:
        """Compare two research papers"""
        analysis1 = self.analyze_paper(paper1_text)
        analysis2 = self.analyze_paper(paper2_text)
        
        return {
            'paper1_title': analysis1['metadata'].get('title', 'Unknown'),
            'paper2_title': analysis2['metadata'].get('title', 'Unknown'),
            'methodology_comparison': {
                'paper1': analysis1['methodology']['type'],
                'paper2': analysis2['methodology']['type'],
                'similar': analysis1['methodology']['type'] == analysis2['methodology']['type']
            },
            'findings_alignment': self._compare_findings(
                analysis1['key_findings'], 
                analysis2['key_findings']
            ),
            'complementary_aspects': self._find_complementary_aspects(analysis1, analysis2)
        }
    
    def _compare_findings(self, findings1: List[str], findings2: List[str]) -> str:
        """Compare findings from two papers"""
        if not findings1 or not findings2:
            return "Insufficient data for comparison"
        
        # Simple keyword overlap check
        words1 = set(' '.join(findings1).lower().split())
        words2 = set(' '.join(findings2).lower().split())
        
        overlap = len(words1 & words2) / max(len(words1), len(words2)) * 100
        
        if overlap > 50:
            return "High alignment - papers reach similar conclusions"
        elif overlap > 25:
            return "Moderate alignment - some overlapping findings"
        else:
            return "Low alignment - papers address different aspects"
    
    def _find_complementary_aspects(self, analysis1: Dict, analysis2: Dict) -> List[str]:
        """Find complementary aspects between papers"""
        complementary = []
        
        # Different methodologies
        if analysis1['methodology']['type'] != analysis2['methodology']['type']:
            complementary.append(f"Different approaches: {analysis1['methodology']['type']} vs {analysis2['methodology']['type']}")
        
        # Different sample sizes
        if analysis1['methodology']['sample_size'] and analysis2['methodology']['sample_size']:
            diff = abs(analysis1['methodology']['sample_size'] - analysis2['methodology']['sample_size'])
            if diff > 50:
                complementary.append("Significantly different sample sizes provide broader evidence")
        
        return complementary
    
    def get_prompt_template(self) -> str:
        """Return the research paper analysis prompt template"""
        return """You are a PhD-level research analyst who makes complex academic papers understandable.

PAPER TITLE: {title}
RESEARCH FIELD: {field}

DOCUMENT CONTENT:
{document_text}

Generate a comprehensive analysis including:
1. Paper Overview (title, authors, publication, year)
2. Research Question (what problem does this solve?)
3. Methodology (research type, sample size, tools used)
4. Key Findings (top 5 most important findings)
5. Key Statistics (all important numbers, percentages, p-values)
6. Limitations (what the research cannot prove)
7. Future Research Suggestions
8. Plain English Summary (explain to a non-expert in 5 sentences)
9. Real-World Impact Assessment

Make complex concepts accessible while maintaining accuracy."""
