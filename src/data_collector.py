import requests
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        load_dotenv()
        self.news_api_key = os.getenv('NEWSAPI_KEY')
        self.news_api_url = "https://newsapi.org/v2/everything"
        self.page_size = 5  # Number of articles to fetch

    def _get_user_input(self, prompt, validation_func=None):
        """Helper function to get and validate user input."""
        while True:
            user_input = input(prompt).strip()
            if not user_input:
                logger.warning("Input cannot be empty. Please try again.")
                continue
            if validation_func and not validation_func(user_input):
                logger.warning("Invalid input. Please try again.")
                continue
            return user_input

    def collect_company_info(self):
        """Collect basic company information through user input."""
        logger.info("\n=== Company Information Collection ===")
        
        # Basic company information
        company_info = {
            'name': self._get_user_input("Company Name: "),
            'industry': self._get_user_input("Industry: "),
            'flagship_products': self._get_user_input("Flagship Products/Services (comma-separated): ").split(','),
            'achievements': self._get_user_input("Major Achievements (comma-separated): ").split(','),
            'brand_attributes': self._get_user_input("Brand Attributes (comma-separated): ").split(','),
            'year_founded': self._get_user_input("Year Founded: ", lambda x: x.isdigit() and len(x) == 4),
            'company_size': self._get_user_input("Company Size (e.g., 1-50, 51-200, 201-500): ")
        }

        # Press release specific information
        logger.info("\n=== Press Release Details ===")
        press_release_info = {
            'topic': self._get_user_input("Press Release Topic: "),
            'target_media': self._get_user_input("Target Media (e.g., tech blogs, business news): "),
            'target_audience': self._get_user_input("Target Audience: "),
            'tone': self._get_user_input("Desired Tone (professional/casual/formal): "),
            'key_message': self._get_user_input("Key Message to Convey: "),
            'call_to_action': self._get_user_input("Desired Call to Action: ")
        }

        return {**company_info, **press_release_info}

    def _fetch_news_articles(self, company_name):
        """Fetch news articles using NewsAPI."""
        try:
            params = {
                'q': company_name,
                'apiKey': self.news_api_key,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': self.page_size
            }
            response = requests.get(self.news_api_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json().get('articles', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news articles: {e}")
            return []

    def _display_articles(self, articles):
        """Display fetched articles to the user."""
        if not articles:
            logger.info("No news articles found.")
            return []

        logger.info("\n=== Found News Articles ===")
        for i, article in enumerate(articles, 1):
            logger.info(f"\n{i}. {article['title']}")
            logger.info(f"Source: {article['source']['name']}")
            logger.info(f"Published: {article['publishedAt']}")
            if article.get('description'):
                logger.info(f"Description: {article['description']}")

        return articles

    def _select_articles(self, articles):
        """Allow the user to select relevant articles."""
        if not articles:
            return []

        logger.info("\n=== Article Selection ===")
        selection = input("Select relevant articles (comma-separated numbers, or 'all'): ").strip().lower()

        if selection == 'all':
            return articles

        try:
            indices = [int(i.strip()) - 1 for i in selection.split(',')]
            return [articles[i] for i in indices if 0 <= i < len(articles)]
        except (ValueError, IndexError):
            logger.warning("Invalid selection. Using all articles.")
            return articles

    def collect_supplementary_data(self, company_name):
        """Collect and process supplementary data (news articles)."""
        logger.info("\nCollecting news articles...")
        
        articles = self._fetch_news_articles(company_name)
        displayed_articles = self._display_articles(articles)
        selected_articles = self._select_articles(displayed_articles)

        if not selected_articles:
            return None

        # Format selected articles
        formatted_articles = [
            {
                'title': article['title'],
                'source': article['source']['name'],
                'published_date': article['publishedAt'],
                'description': article.get('description', ''),
                'url': article['url']
            }
            for article in selected_articles
        ]

        return {'selected_news': formatted_articles}

# Example usage
if __name__ == "__main__":
    collector = DataCollector()
    company_data = collector.collect_company_info()
    supplementary_data = collector.collect_supplementary_data(company_data['name'])
    print("\nCollected Data:")
    print(company_data)
    print(supplementary_data)