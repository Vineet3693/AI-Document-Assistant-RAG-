"""
Prompt Builder Module
Constructs complete prompts for AI models with context, history, and instructions.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import yaml
from pathlib import Path


@dataclass
class Message:
    """Represents a chat message."""
    role: str  # 'system', 'user', or 'assistant'
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API."""
        return {'role': self.role, 'content': self.content}


@dataclass
class PromptTemplate:
    """Represents a prompt template from config."""
    name: str
    system_prompt: str
    user_template: str
    variables: List[str] = field(default_factory=list)
    
    def render(
        self,
        context: str = "",
        question: str = "",
        history: str = "",
        **kwargs
    ) -> tuple[str, str]:
        """
        Render the prompt with variables.
        
        Returns:
            Tuple of (system_message, user_message)
        """
        # Replace context and question in user template
        user_content = self.user_template.replace('{context}', context)
        user_content = user_content.replace('{question}', question)
        user_content = user_content.replace('{history}', history)
        
        # Replace any additional variables
        for key, value in kwargs.items():
            placeholder = f'{{{key}}}'
            if placeholder in user_content:
                user_content = user_content.replace(placeholder, str(value))
        
        return self.system_prompt, user_content


class PromptBuilder:
    """
    Builds complete prompts for AI models with proper formatting.
    """
    
    def __init__(self, prompts_config_path: Optional[str] = None):
        """
        Initialize prompt builder.
        
        Args:
            prompts_config_path: Path to prompts.yaml config file
        """
        self.templates: Dict[str, PromptTemplate] = {}
        self.default_template = "rag_qa"
        self.logger = None
        
        # Load prompts from config
        if prompts_config_path:
            self.load_prompts(prompts_config_path)
        else:
            # Try default location
            default_path = Path(__file__).parent.parent.parent / 'config' / 'prompts.yaml'
            if default_path.exists():
                self.load_prompts(str(default_path))
            else:
                self._load_default_prompts()
    
    def load_prompts(self, config_path: str):
        """Load prompts from YAML configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            prompts = config.get('prompts', {})
            
            for name, prompt_data in prompts.items():
                template = PromptTemplate(
                    name=name,
                    system_prompt=prompt_data.get('system_prompt', ''),
                    user_template=prompt_data.get('user_template', ''),
                    variables=prompt_data.get('variables', [])
                )
                self.templates[name] = template
            
            if self.logger:
                self.logger.info(f"Loaded {len(self.templates)} prompt templates")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load prompts from {config_path}: {e}")
            self._load_default_prompts()
    
    def _load_default_prompts(self):
        """Load default built-in prompts."""
        # Main RAG Q&A Prompt
        self.templates['rag_qa'] = PromptTemplate(
            name="rag_qa",
            system_prompt="""You are DocuMind AI, an elite document analysis assistant trusted by Fortune 500 companies.

Your ONE job: Answer questions ACCURATELY using ONLY the document context provided.

YOUR ABSOLUTE RULES:
1. ONLY use information from the CONTEXT below
2. If answer not found → Say exactly: "I could not find this in the documents. The documents available are: {doc_names}"
3. NEVER guess, assume, or make up information
4. ALWAYS cite your source: 📄 Found in: [Document Name], Page [X]
5. If partially found → Share what you found and clearly state what is missing
6. If question is unclear → Ask for clarification before answering
7. Answer in the same language as the question

YOUR ANSWER FORMAT:
✅ Direct Answer:
[Your main answer here - 2 to 4 sentences]

📌 Key Details:
• [Detail 1]
• [Detail 2]
• [Detail 3]

📄 Source:
Document: [name]
Location: Page [X] / Section [Y]
Quote: "[exact text from document]"

🔍 Confidence: [High / Medium / Low]
Reason: [why you are confident or not]""",
            user_template="""CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION:
{question}

Answer the question based ONLY on the context above.""",
            variables=['context', 'question', 'doc_names']
        )
        
        # Executive Summary Prompt
        self.templates['executive_summary'] = PromptTemplate(
            name="executive_summary",
            system_prompt="""You are a senior business analyst who creates world-class executive summaries for C-suite leaders.

Your summaries are:
- Clear and jargon-free
- Action-oriented
- Focused on what matters most
- Never longer than needed""",
            user_template="""DOCUMENT NAME: {document_name}
DOCUMENT TYPE: {document_type}
INDUSTRY: {industry}

DOCUMENT CONTENT:
{document_text}

Generate a comprehensive executive summary with:
1. ONE LINE SUMMARY
2. EXECUTIVE SUMMARY (100 words max)
3. 5 KEY POINTS
4. IMPORTANT DATA FOUND (numbers, dates, people, companies)
5. ACTION ITEMS
6. RISKS OR CONCERNS
7. BOTTOM LINE""",
            variables=['document_name', 'document_type', 'industry', 'document_text']
        )
        
        # Document Comparison Prompt
        self.templates['document_comparison'] = PromptTemplate(
            name="document_comparison",
            system_prompt="""You are an expert document analyst specializing in comparing legal contracts, financial reports, and business documents.

Your comparisons are:
- Precise and factual
- Unbiased
- Easy to understand
- Actionable""",
            user_template="""DOCUMENT 1: {doc1_name}
{doc1_text}

DOCUMENT 2: {doc2_name}
{doc2_text}

Compare these documents and provide:
1. AT A GLANCE comparison table
2. WHAT THEY AGREE ON
3. KEY DIFFERENCES (table format)
4. CRITICAL DIFFERENCES
5. MINOR DIFFERENCES
6. ANALYST RECOMMENDATION
7. IMPORTANT NOTES""",
            variables=['doc1_name', 'doc1_text', 'doc2_name', 'doc2_text']
        )
        
        # Legal Contract Review Prompt
        self.templates['legal_review'] = PromptTemplate(
            name="legal_review",
            system_prompt="""You are a senior legal analyst with 20 years of experience reviewing contracts across all industries.

IMPORTANT: Always include disclaimer: "⚠️ This is an AI analysis for informational purposes only. Always consult a qualified attorney before making legal decisions."

Your analysis is thorough, precise, and identifies both risks and favorable terms.""",
            user_template="""CONTRACT TYPE: {contract_type}
PARTY 1: {party1_name}
PARTY 2: {party2_name}

CONTRACT TEXT:
{contract_text}

Provide comprehensive contract analysis including:
1. CONTRACT OVERVIEW (type, parties, dates, value, jurisdiction)
2. KEY CLAUSES FOUND
3. HIGH RISK CLAUSES (with recommendations)
4. MEDIUM RISK CLAUSES
5. FAVORABLE CLAUSES
6. MISSING CLAUSES
7. RISK SCORE (LOW/MEDIUM/HIGH/CRITICAL)
8. RECOMMENDED NEXT STEPS

Include the legal disclaimer at the end.""",
            variables=['contract_type', 'party1_name', 'party2_name', 'contract_text']
        )
        
        # Financial Analysis Prompt
        self.templates['financial_analysis'] = PromptTemplate(
            name="financial_analysis",
            system_prompt="""You are a CFA-level financial analyst who extracts critical insights from financial documents.

Your analysis is:
- Numbers-focused and precise
- Free of speculation
- Grounded in the document only
- Written for executive decision-making""",
            user_template="""COMPANY: {company_name}
REPORT TYPE: {report_type}
PERIOD: {report_period}

REPORT CONTENT:
{report_text}

Extract and analyze:
1. KEY FINANCIAL METRICS (revenue, profit, margins, assets, liabilities, cash, EPS)
2. PERFORMANCE HIGHLIGHTS (strengths and concerns)
3. RISK FACTORS MENTIONED
4. MANAGEMENT GUIDANCE
5. KEY INSIGHTS for decision makers""",
            variables=['company_name', 'report_type', 'report_period', 'report_text']
        )
        
        # Multi-Document Q&A Prompt
        self.templates['multi_doc_qa'] = PromptTemplate(
            name="multi_doc_qa",
            system_prompt="""You are an expert research analyst who can synthesize information from multiple documents to give comprehensive, well-cited answers.

CRITICAL RULES:
1. Search ALL documents for the answer
2. If found in multiple documents → Mention all
3. If documents CONTRADICT each other → Flag it
4. Always cite WHICH document each point came from
5. If not found in ANY document → Say so clearly""",
            user_template="""DOCUMENTS AVAILABLE:
{document_list}

CONTEXT FROM ALL DOCUMENTS:
{context}

USER QUESTION:
{question}

Provide a comprehensive answer synthesizing information from all documents. Include:
1. COMPREHENSIVE ANSWER
2. SOURCES USED (which document contributed what)
3. CONTRADICTIONS FOUND (if any)
4. NOT FOUND IN ANY DOCUMENT
5. RELATED INFORMATION""",
            variables=['document_list', 'context', 'question']
        )
    
    def build_prompt(
        self,
        template_name: Optional[str] = None,
        context: str = "",
        question: str = "",
        chat_history: Optional[List[Dict[str, str]]] = None,
        industry_mode: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> List[Message]:
        """
        Build complete prompt with all components.
        
        Args:
            template_name: Name of template to use
            context: Document context
            question: User question
            chat_history: Previous conversation messages
            industry_mode: Industry-specific mode (legal, finance, etc.)
            language: Preferred response language
            **kwargs: Additional template variables
            
        Returns:
            List of Message objects ready for API
        """
        # Get template
        template_name = template_name or self.default_template
        template = self.templates.get(template_name)
        
        if not template:
            if self.logger:
                self.logger.warning(f"Template '{template_name}' not found, using default")
            template = self.templates.get('rag_qa')
        
        # Format history
        history_str = ""
        if chat_history:
            history_parts = []
            for msg in chat_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_parts.append(f"{role.capitalize()}: {content}")
            history_str = "\n".join(history_parts)
        
        # Add language instruction if specified
        if language:
            lang_instruction = f"\n\nIMPORTANT: Respond in {language}."
            if '{question}' in template.user_template:
                template_copy = PromptTemplate(
                    name=template.name,
                    system_prompt=template.system_prompt,
                    user_template=template.user_template + lang_instruction,
                    variables=template.variables
                )
                system_prompt, user_prompt = template_copy.render(
                    context=context,
                    question=question,
                    history=history_str,
                    **kwargs
                )
            else:
                system_prompt, user_prompt = template.render(
                    context=context,
                    question=question,
                    history=history_str,
                    **kwargs
                )
        else:
            system_prompt, user_prompt = template.render(
                context=context,
                question=question,
                history=history_str,
                **kwargs
            )
        
        # Add industry mode instruction
        if industry_mode:
            mode_instructions = {
                'legal': "\n\nMODE: Legal Analysis. Focus on clauses, risks, compliance, and legal implications.",
                'finance': "\n\nMODE: Financial Analysis. Focus on numbers, metrics, trends, and financial implications.",
                'healthcare': "\n\nMODE: Healthcare Analysis. Focus on medical accuracy, patient safety, and include medical disclaimers.",
                'hr': "\n\nMODE: HR Analysis. Focus on skills matching, candidate evaluation, and fair assessment.",
                'research': "\n\nMODE: Research Analysis. Focus on methodology, findings, statistics, and academic rigor.",
                'education': "\n\nMODE: Education. Focus on clarity, learning outcomes, and age-appropriate explanations."
            }
            
            instruction = mode_instructions.get(industry_mode, "")
            if instruction:
                system_prompt += instruction
        
        # Build messages
        messages = [
            Message(role='system', content=system_prompt),
            Message(role='user', content=user_prompt)
        ]
        
        # Add chat history if present
        if chat_history:
            # Insert history between system and current question
            history_messages = [
                Message(role=msg['role'], content=msg['content'])
                for msg in chat_history[-10:]  # Last 10 messages
            ]
            messages = [messages[0]] + history_messages + [messages[1]]
        
        return messages
    
    def build_simple_prompt(
        self,
        system_instruction: str,
        user_content: str
    ) -> List[Message]:
        """Build simple two-message prompt."""
        return [
            Message(role='system', content=system_instruction),
            Message(role='user', content=user_content)
        ]
    
    def get_available_templates(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates.keys())
    
    def add_template(self, name: str, template: PromptTemplate):
        """Add or update a template."""
        self.templates[name] = template


# Singleton instance
_prompt_builder_instance: Optional[PromptBuilder] = None


def get_prompt_builder(config_path: Optional[str] = None) -> PromptBuilder:
    """Get singleton prompt builder instance."""
    global _prompt_builder_instance
    if _prompt_builder_instance is None:
        _prompt_builder_instance = PromptBuilder(config_path)
    return _prompt_builder_instance
