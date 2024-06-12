import os
from datetime import datetime, timedelta

from crewai_tools import BaseTool
from exa_py import Exa


class SearchAndContents(BaseTool):
    """
    Searches the web based on a search query for the latest results. Results are only from the last week.
    Uses the Exa API.
    This also returns the contents of the search results.

    Attributes:
        name (str): The name of the tool.
        description (str): A description of the tool.
    """

    name: str = "Search and Contents Tool"
    description: str = (
        """Searches the web based on a search query for the latest results.
        Results are only from the last week.
        Uses the Exa API.
        This also returns the contents of the search results.
        """
    )

    def _run(self, search_query: str) -> str:  # dead: disable
        """
        Searches the web based on a search query for the latest results. Results are only from the last week.
        Uses the Exa API.
        This also returns the contents of the search results.

        Parameters:
            search_query (str): The search query.

        Returns:
            search_results (str): The search results.
        """

        exa = Exa(api_key=os.getenv("EXA_API_KEY"))

        one_week_ago = datetime.now() - timedelta(days=7)
        date_cutoff = one_week_ago.strftime("%Y-%m-%d")

        search_results = exa.search_and_contents(
            query=search_query,
            use_autoprompt=True,
            start_published_date=date_cutoff,
            text={"include_html_tags": False, "max_characters": 8000},
        )

        return str(search_results)


class FindSimilar(BaseTool):
    """
    Searches for similar articles to a given article using the Exa API. Takes in a URL of the article.

    Attributes:
        name (str): The name of the tool.
        description (str): A description of the tool.
    """

    name: str = "Find Similar Tool"
    description: str = (
        "Searches for similar articles to a given article using the Exa API. Takes in a URL of the article"
    )

    def _run(self, article_url: str) -> str:  # dead: disable
        """
        Searches for similar articles to a given article using the Exa API.

        Args:
            article_url (str): The URL of the article.

        Returns:
            search_results (str): The search results.

        """

        one_week_ago = datetime.now() - timedelta(days=7)
        date_cutoff = one_week_ago.strftime("%Y-%m-%d")

        exa = Exa(api_key=os.getenv("EXA_API_KEY"))

        search_results = exa.find_similar(
            url=article_url, start_published_date=date_cutoff
        )

        return str(search_results)


class GetContents(BaseTool):
    """
    Gets the contents of a specific article using the Exa API. Takes in the ID of the article.

    Attributes:
        name (str): The name of the tool.
        description (str): A description of the tool.

    """

    name: str = "Get Contents Tool"
    description: str = (
        """
        Gets the contents of a specific article using the Exa API.
        Takes in the ID of the article in a list, like this: ['https://www.cnbc.com/2024/04/18/my-news-story'].
        """
    )

    def _run(self, article_ids: str) -> str:  # dead: disable
        """
        Gets the contents of a specific article using the Exa API.

        Args:
            article_ids (str): The IDs of the articles.

        Returns:
            contents (str): The contents of the article.
        """

        exa = Exa(api_key=os.getenv("EXA_API_KEY"))

        contents = exa.get_contents(article_ids)
        return str(contents)
