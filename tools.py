"""
Search Tool Integration for AI Research Agent
Uses Tavily API for web search
"""

import os
import sys
from typing import List, Dict, Any
from tavily import TavilyClient
from dotenv import load_dotenv

# Find the .env file - go up until we find it
def find_env_file():
    """Find .env file by walking up directories"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        env_path = os.path.join(current_dir, '.env')
        if os.path.exists(env_path):
            return env_path
        current_dir = os.path.dirname(current_dir)
    return None

# Load environment variables
env_path = find_env_file()
if env_path:
    print(f"✅ Found .env at: {env_path}")
    load_dotenv(env_path)
else:
    print("❌ Could not find .env file")
    print("Please create .env in the root directory with your API keys")

class SearchTool:
    def __init__(self):
        """Initialize the search tool with Tavily API"""
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            print("⚠️  Warning: TAVILY_API_KEY not found in .env file")
            print("Current directory:", os.getcwd())
            print("Please add: TAVILY_API_KEY=your_key_here to .env file")
            self.client = None
        else:
            print(f"✅ TAVILY_API_KEY found: {self.api_key[:8]}...")
            self.client = TavilyClient(api_key=self.api_key)
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform a web search using Tavily"""
        if not self.client:
            return [{"error": "Tavily client not initialized. Check API key."}]
        
        try:
            print(f"🔍 Searching for: {query}")
            results = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            
            formatted_results = []
            for result in results.get("results", []):
                formatted_results.append({
                    "title": result.get("title", "No title"),
                    "content": result.get("content", "No content"),
                    "url": result.get("url", "No URL"),
                    "score": result.get("score", 0)
                })
            
            print(f"✅ Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            print(f"❌ {error_msg}")
            return [{"error": error_msg}]
    
    def format_for_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM context"""
        if not results:
            return "No search results found."
        
        formatted = "\n\n=== SEARCH RESULTS ===\n"
        for i, result in enumerate(results, 1):
            if "error" in result:
                formatted += f"\n[{i}] Error: {result['error']}\n"
            else:
                formatted += f"\n[{i}] {result.get('title', 'Untitled')}\n"
                formatted += f"URL: {result.get('url', 'N/A')}\n"
                content = result.get('content', 'No content')
                formatted += f"Content: {content[:300]}...\n"
            formatted += "-" * 50 + "\n"
        
        return formatted

# Test the search tool
if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Testing SearchTool")
    print("=" * 50)
    
    # Check if API key exists
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ TAVILY_API_KEY not found in .env file")
        print(f"\nCurrent directory: {os.getcwd()}")
        print(f"Looking for .env at: {env_path}")
        print("\nPlease add your Tavily API key to the .env file:")
        print("1. Open the .env file in root directory")
        print("2. Add: TAVILY_API_KEY=your_api_key_here")
        print("3. Save the file and run this test again")
    else:
        print(f"✅ TAVILY_API_KEY found: {api_key[:8]}...")
        
        # Create tool instance
        tool = SearchTool()
        
        # Test search
        test_query = "What is LangGraph?"
        print(f"\n🔬 Testing search for: '{test_query}'")
        
        results = tool.search(test_query, max_results=2)
        
        if results and "error" not in results[0]:
            print("\n✅ Search successful!")
            print(tool.format_for_context(results))
        else:
            print(f"\n❌ Search failed: {results[0].get('error')}")
    
    print("\n" + "=" * 50)