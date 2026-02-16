import os
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


class TranslationService:
    """
    Multilingual translation service using Groq LLM
    Supports: English, Hindi, Telugu, Tamil
    """

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu",
        "ta": "Tamil"
    }

    def __init__(self):
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.3  # Lower temp for more accurate translation
        )

    def detect_language(self, text: str) -> str:
        """
        Detect the language of input text

        Args:
            text: Input text

        Returns:
            Language code (en, hi, te, ta)
        """
        prompt = PromptTemplate(
            template="""Detect the language of the following text and respond with ONLY the language code.

Supported languages:
- en: English
- hi: Hindi
- te: Telugu
- ta: Tamil

Text: {text}

Respond with ONLY the two-letter code (en/hi/te/ta):""",
            input_variables=["text"]
        )

        response = (prompt | self.llm).invoke({"text": text[:500]})
        detected = response.content.strip().lower()

        # Validate
        if detected not in self.SUPPORTED_LANGUAGES:
            return "en"  # Default to English

        return detected

    def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Translate text from source language to English

        Args:
            text: Input text
            source_lang: Source language code

        Returns:
            Translated English text
        """
        if source_lang == "en":
            return text  # Already English

        lang_name = self.SUPPORTED_LANGUAGES.get(source_lang, "Unknown")

        prompt = PromptTemplate(
            template="""Translate the following {source_language} text to English.
Maintain the original meaning and context.

{source_language} Text:
{text}

English Translation:""",
            input_variables=["source_language", "text"]
        )

        response = (prompt | self.llm).invoke({
            "source_language": lang_name,
            "text": text
        })

        return response.content.strip()

    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translate English text to target language

        Args:
            text: English text
            target_lang: Target language code

        Returns:
            Translated text
        """
        if target_lang == "en":
            return text  # Already English

        lang_name = self.SUPPORTED_LANGUAGES.get(target_lang, "English")

        prompt = PromptTemplate(
            template="""Translate the following English text to {target_language}.
Maintain the original meaning, tone, and formatting (including bullet points, headings, etc.).

English Text:
{text}

{target_language} Translation:""",
            input_variables=["target_language", "text"]
        )

        response = (prompt | self.llm).invoke({
            "target_language": lang_name,
            "text": text
        })

        return response.content.strip()

    def process_user_input(self, text: str) -> Dict[str, Any]:
        """
        Process user input: detect language and translate to English if needed

        Args:
            text: User input text

        Returns:
            Dict with:
                - original_text: Original input
                - detected_language: Detected language code
                - english_text: Text in English
        """
        detected_lang = self.detect_language(text)
        english_text = self.translate_to_english(text, detected_lang)

        return {
            "original_text": text,
            "detected_language": detected_lang,
            "english_text": english_text
        }

    def process_response(self, english_response: str, target_lang: str) -> str:
        """
        Translate English response to user's language

        Args:
            english_response: Response in English
            target_lang: Target language code

        Returns:
            Translated response
        """
        return self.translate_from_english(english_response, target_lang)


# Global instance
translation_service = TranslationService()
