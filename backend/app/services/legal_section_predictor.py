import os
import json
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


class LegalSectionPredictor:
    """
    Predicts applicable legal sections (IPC, CrPC, BNS) from legal documents/FIRs
    Provides structured legal analysis
    """

    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.2  # Lower temp for more consistent structured output
        )

    def predict_sections(self, document_text: str, retrieved_context: str = "") -> Dict[str, Any]:
        """
        Predict applicable legal sections from document

        Args:
            document_text: The legal document/FIR text
            retrieved_context: Retrieved similar cases/context from RAG

        Returns:
            Structured dict with legal analysis
        """
        prompt = PromptTemplate(
            template="""You are an expert Indian legal analyst with deep knowledge of IPC, CrPC, and BNS. Analyze the following legal document/FIR and provide a comprehensive structured legal analysis.

Document/FIR Content:
{document}

Retrieved Legal Context (Similar Cases/Laws):
{context}

Based on the document and legal context, provide a detailed analysis in STRICT JSON format.

CRITICAL INSTRUCTIONS:
1. Carefully read the document to extract ALL relevant legal information
2. Identify specific section numbers if mentioned
3. Infer applicable sections based on the offense described
4. ALWAYS provide BOTH IPC and corresponding BNS sections
5. Provide practical legal guidance
6. Return ONLY valid JSON (no markdown, no code blocks, no extra text)

JSON Format:

{{
  "document_type": "FIR/Legal Notice/Complaint/Petition/Other",
  "case_summary": "Detailed 3-4 sentence summary covering who, what, when, where, and alleged offense",
  "key_parties": {{
    "complainant": "Name/description if mentioned",
    "accused": "Name/description if mentioned",
    "witnesses": "Names if mentioned"
  }},
  "applicable_sections": [
    {{
      "ipc_section": "420",
      "bns_section": "318",
      "title": "Cheating and dishonestly inducing delivery of property",
      "description": "Clear description of what this section covers",
      "relevance": "Specific reason why this applies to the case",
      "punishment": "Imprisonment up to 7 years and fine"
    }}
  ],
  "applicable_crpc_sections": [
    {{
      "section": "156",
      "title": "Police power to investigate cognizable case",
      "description": "What this section allows",
      "relevance": "Why it applies"
    }}
  ],
  "offense_details": {{
    "type": "Economic Offense/Violent Crime/Property Crime/etc",
    "severity": "Minor/Moderate/Serious/Heinous",
    "cognizable": "Yes/No",
    "bailable": "Yes/No",
    "compoundable": "Yes/No"
  }},
  "legal_consequences": "Detailed explanation of potential penalties, imprisonment duration, fines, and other consequences. Mention both IPC and BNS provisions.",
  "case_number": "FIR/Case number if mentioned in document",
  "similar_cases": [
    "State vs. ABC (2020) - Brief description of similar case",
    "XYZ vs. DEF (2019) - Brief description"
  ],
  "recommended_next_steps": [
    "File FIR at nearest police station within jurisdiction",
    "Gather all documentary evidence (receipts, emails, messages)",
    "Consult criminal lawyer for legal representation",
    "Apply for anticipatory bail if required",
    "Maintain record of all proceedings"
  ],
  "important_notes": [
    "This is a cognizable offense - police must register FIR",
    "Complaint should be filed within limitation period",
    "Legal advice from qualified lawyer recommended"
  ]
}}

IMPORTANT RULES:
- Extract EXACT section numbers if mentioned in the document
- If no sections mentioned, infer based on offense type
- ALWAYS map IPC sections to BNS equivalents (IPC 302→BNS 103, IPC 420→BNS 318, etc.)
- Use empty arrays [] if a category doesn't apply
- Be specific and detailed in explanations
- Focus on Indian Penal Code, CrPC, and Bharatiya Nyaya Sanhita
- Return ONLY valid JSON without any markdown formatting or code blocks

JSON Response:""",
            input_variables=["document", "context"]
        )

        response = (prompt | self.llm).invoke({
            "document": document_text[:3000],  # Limit length
            "context": retrieved_context[:2000]
        })

        # Parse JSON response
        try:
            # Clean response - remove markdown code blocks if present
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            result = json.loads(content)
            
            # Convert old format to new format if needed
            if 'applicable_ipc_sections' in result and 'applicable_sections' not in result:
                result['applicable_sections'] = []
                for ipc_sec in result.get('applicable_ipc_sections', []):
                    result['applicable_sections'].append({
                        'ipc_section': ipc_sec.get('section', ''),
                        'bns_section': 'TBD',
                        'title': ipc_sec.get('title', ''),
                        'description': ipc_sec.get('description', ''),
                        'relevance': ipc_sec.get('relevance', ''),
                        'punishment': ipc_sec.get('punishment', '')
                    })
            
            return result
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response content: {response.content[:500]}")
            # Fallback if JSON parsing fails
            return {
                "document_type": "Legal Document",
                "case_summary": "The document contains legal information that requires manual review for detailed analysis.",
                "key_parties": {
                    "complainant": "Not specified",
                    "accused": "Not specified",
                    "witnesses": "Not specified"
                },
                "applicable_ipc_sections": [],
                "applicable_crpc_sections": [],
                "applicable_bns_sections": [],
                "offense_details": {
                    "type": "To be determined",
                    "severity": "Unknown",
                    "cognizable": "Unknown",
                    "bailable": "Unknown",
                    "compoundable": "Unknown"
                },
                "legal_consequences": "Requires detailed legal review by a qualified professional",
                "case_number": "Not found in document",
                "similar_cases": [],
                "recommended_next_steps": [
                    "Consult with a qualified legal professional",
                    "Review the complete document for all details",
                    "Gather supporting evidence and documentation"
                ],
                "important_notes": [
                    "This is an automated analysis and may be incomplete",
                    "Professional legal advice is strongly recommended"
                ]
            }

    def analyze_fir(self, fir_text: str, context: str = "") -> Dict[str, Any]:
        """
        Specialized FIR analysis

        Args:
            fir_text: FIR document text
            context: Retrieved legal context

        Returns:
            Structured legal analysis
        """
        return self.predict_sections(fir_text, context)

    def explain_section(self, section_type: str, section_number: str) -> str:
        """
        Explain a specific legal section in simple terms

        Args:
            section_type: 'IPC', 'CrPC', or 'BNS'
            section_number: Section number

        Returns:
            Simplified explanation
        """
        prompt = PromptTemplate(
            template="""Explain {section_type} Section {section_number} in simple, easy-to-understand language.

Include:
1. What the section covers
2. Punishment/penalty (if applicable)
3. When it is typically applied
4. Example scenario

Keep the explanation under 150 words.

Explanation:""",
            input_variables=["section_type", "section_number"]
        )

        response = (prompt | self.llm).invoke({
            "section_type": section_type,
            "section_number": section_number
        })

        return response.content.strip()


# Global instance
legal_predictor = LegalSectionPredictor()
