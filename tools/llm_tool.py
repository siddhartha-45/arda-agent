"""
LLM Tool - Interface to Groq API with Llama3 model
"""

import os
import json
from typing import Optional, Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMTool:
    """Wrapper for Groq API using Llama 3.2 model"""

    def __init__(self):
        """Initialize Groq client with API key"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please set it in .env file"
            )
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        self.max_tokens = 2048
        self.temperature = 0.7

    def call(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Call Llama3 model via Groq API

        Args:
            prompt: The user prompt/query
            temperature: Sampling temperature (0-1), defaults to 0.7
            max_tokens: Maximum tokens in response, defaults to 2048
            system_prompt: Optional system prompt for context

        Returns:
            Model response as string
        """
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens

        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stop=None
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            raise

    def analyze_json(
        self,
        data: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """
        Analyze structured data and return JSON response

        Args:
            data: Dictionary to analyze
            query: Analysis question

        Returns:
            Parsed JSON response
        """
        prompt = f"""
Analyze this data and respond with valid JSON.

Data: {json.dumps(data, indent=2)}

Query: {query}

Provide response as valid JSON only, no markdown formatting.
"""
        response = self.call(prompt)

        try:
            # Try to extract JSON if wrapped in markdown
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response

            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"raw_response": response}

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract key entities from text

        Args:
            text: Text to extract from

        Returns:
            Dictionary of extracted entities
        """
        prompt = f"""
Extract key entities from this text. Return as JSON with categories like:
entities, dates, numbers, locations, people, organizations

Text: {text}

Return valid JSON only.
"""
        return self.analyze_json({"text": text}, "Extract key entities")

    def score_relevance(
        self,
        text: str,
        query: str
    ) -> float:
        """
        Score relevance of text to query (0.0-1.0)

        Args:
            text: Text to score
            query: Reference query

        Returns:
            Relevance score between 0.0 and 1.0
        """
        prompt = f"""
Rate how relevant this text is to the query on a scale of 0 to 100.

Query: {query}

Text: {text}

Respond with only a number between 0 and 100.
"""
        try:
            response = self.call(prompt).strip()
            score = float(response)
            return min(100, max(0, score)) / 100.0
        except (ValueError, AttributeError):
            return 0.5

    def summarize(self, text: str, max_length: int = 500) -> str:
        """
        Summarize text

        Args:
            text: Text to summarize
            max_length: Maximum length of summary

        Returns:
            Summarized text
        """
        prompt = f"""
Summarize this text in maximum {max_length} characters.

Text: {text}

Provide only the summary, no preamble.
"""
        return self.call(prompt)
