"""
Custom tools for the Agentic Trip Planner
"""
from crewai.tools import tool
from duckduckgo_search import DDGS

@tool("Search Internet")
def search_internet(query: str) -> str:
    """
    Search the web for up-to-date travel info, attractions, hotels, flights, and weather.
    Always returns concise snippets.
    """
    try:
        # Limit to top 3 results to keep context concise and fast
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
        if not results:
            return f"No results found for '{query}'."
            
        formatted_results = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            formatted_results.append(f"{i}. {title}: {body}")
            
        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error executing search: {str(e)}"
