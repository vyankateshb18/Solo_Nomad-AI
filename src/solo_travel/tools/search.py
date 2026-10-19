"""Bounded search tools with explicit guardrails against infinite loops."""
import logging
from crewai.tools import tool
from duckduckgo_search import DDGS
from solo_travel.config import get_settings

logger = logging.getLogger(__name__)


@tool("Search Internet")
def search_internet(query: str) -> str:
    """
    Search the web for up-to-date travel info, hostels, transit options, and attractions.
    Returns concise snippets bounded to top results.
    """
    settings = get_settings()
    max_results = settings.SEARCH_MAX_RESULTS

    clean_query = query.strip()
    if not clean_query:
        return "Search query was empty."

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(clean_query, max_results=max_results))

        if not results:
            return f"No results found for '{clean_query}'."

        formatted_snippets = []
        for idx, item in enumerate(results, start=1):
            title = item.get("title", "Untitled")
            body = item.get("body", "No description")
            url = item.get("href", "")
            formatted_snippets.append(f"[{idx}] {title}\nSummary: {body}\nSource: {url}")

        return "\n\n".join(formatted_snippets)

    except Exception as exc:
        logger.warning(f"Search tool encountered an error for query '{clean_query}': {exc}")
        return f"Error executing search: {str(exc)}"
