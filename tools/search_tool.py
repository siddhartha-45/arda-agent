"""
Search Tool - DuckDuckGo web search wrapper
"""

import json
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS


class SearchTool:
    """Wrapper for DuckDuckGo search"""

    def __init__(self):
        """Initialize search tool"""
        self.ddgs = DDGS()
        self.max_retries = 3
        self.timeout = 30

    def search(
        self,
        query: str,
        num_results: int = 5,
        region: str = "us-en",
        safesearch: str = "moderate"
    ) -> List[Dict[str, Any]]:
        """
        Perform web search using DuckDuckGo

        Args:
            query: Search query string
            num_results: Number of results to return
            region: Region code (us-en, fr-fr, etc.)
            safesearch: Safe search level (off, moderate, strict)

        Returns:
            List of search results with title, body, href, source
        """
        try:
            results = self.ddgs.text(
                query,
                max_results=num_results,
                region=region,
                safesearch=safesearch
            )

            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'body': result.get('body', ''),
                    'href': result.get('href', ''),
                    'source': 'DuckDuckGo',
                    'relevance_score': 0.8  # DuckDuckGo ranking
                })

            return formatted_results

        except Exception as e:
            print(f"Search error: {e}")
            return [{
                'title': 'Search Error',
                'body': f'Error performing search: {str(e)}',
                'href': '',
                'source': 'Error',
                'relevance_score': 0.0
            }]

    def search_news(
        self,
        query: str,
        num_results: int = 5,
        region: str = "us-en",
        timelimit: str = "m"
    ) -> List[Dict[str, Any]]:
        """
        Search for recent news

        Args:
            query: Search query
            num_results: Number of results
            region: Region code
            timelimit: Time limit (d=day, w=week, m=month, y=year)

        Returns:
            List of news results
        """
        try:
            results = self.ddgs.news(
                query,
                max_results=num_results,
                region=region,
                timelimit=timelimit
            )

            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'body': result.get('body', ''),
                    'href': result.get('href', ''),
                    'source': result.get('source', 'News'),
                    'date': result.get('date', ''),
                    'relevance_score': 0.85,
                    'type': 'news'
                })

            return formatted_results

        except Exception as e:
            print(f"News search error: {e}")
            return []

    def deep_search(
        self,
        query: str,
        num_results: int = 10
    ) -> Dict[str, Any]:
        """
        Perform comprehensive search across multiple sources

        Args:
            query: Search query
            num_results: Results per source

        Returns:
            Dictionary with results from multiple sources
        """
        return {
            'query': query,
            'web_results': self.search(query, num_results),
            'news_results': self.search_news(query, num_results=min(5, num_results)),
            'timestamp': __import__('time').time()
        }

    def compare_sources(
        self,
        query: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Search and compare information across sources for specific keywords

        Args:
            query: Base search query
            keywords: Keywords to track across sources

        Returns:
            Comparison analysis
        """
        results = self.search(query, num_results=10)

        comparison = {
            'query': query,
            'keyword_mentions': {},
            'sources': []
        }

        for keyword in keywords:
            count = 0
            for result in results:
                content = (result.get('title', '') + ' ' + result.get('body', '')).lower()
                if keyword.lower() in content:
                    count += 1
            comparison['keyword_mentions'][keyword] = count

        comparison['sources'] = results

        return comparison
