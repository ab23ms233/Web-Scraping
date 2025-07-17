import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import json
import random
import time
from colorama import Fore, init

class QuoteScraping:
    """ 
    A class for scraping quotes and author information from a quotes website.
 
    **Class Attributes:**
    `base_url`: The base URL of the quotes website.
    
    **Instance Attributes:**
    - `timeout`: Timeout for requests in seconds.
    - `session`: A requests session for making HTTP requests. Sessions are more efficient for multiple requests.
    - `header`: Headers to mimic a browser request.
    - `delay`: Random delay between requests to avoid increasing traffic on the server.
 
    **Methods:**
    - `author_list`: Scrapes the list of authors from the quotes website.
    - `scrape_author_quotes`: Scrapes quotes by a specific author.
    - `scrape_author_info`: Scrapes information about a specific author.
    - `scrape_all_quotes`: Scrapes all quotes from the quotes website.
    - `scrape_all_authors`: Scrapes information about all authors from the quotes website.
    - `write_to_json`: Writes the scraped data to a JSON file.

    **Example:**
    ```python
    scraper = QuoteScraping()
    authors = scraper.author_list()
    print(authors)
    ```
    """
    base_url = "https://quotes.toscrape.com/"
    init(autoreset=True)

    def __init__(self) -> None:
        """
        Initializes the class with a session, headers, and timeout settings.

        **Attributes:**
        - `timeout`: Timeout for requests in seconds. Recommended to keep it low to avoid long waits.
        - `session`: A requests session for making HTTP requests. Sessions are more efficient for multiple requests.
        - `header`: Headers to mimic a browser request.
        - `delay`: Random delay between requests to avoid increasing traffic on the server.
        """
        self.timeout = 5
        self.session = requests.Session()
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"}      # Chrome browser string
        self.delay = [1.5, 3]

    def author_list(self) -> List[str]:
        """
        Scrapes the list of authors from the quotes website.

        **Returns:**
        `List[str]`: A list of unique author names found on the site.
        """
        url = QuoteScraping.base_url
        author_set = set()
        page_count = 0

        while url:
            try:
                response = self.session.get(url, timeout=self.timeout, headers=self.header)
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error fetching {url}: {e}")
            
            page_count += 1
            print(f"Scraping page {page_count}...")
            
            soup = BeautifulSoup(response.text, "html.parser")
            authors = soup.select("small.author")
            
            author_set.update([author.get_text(strip=True) for author in authors])
            next_button = soup.find("li", class_="next")

            if next_button:
                next_href = next_button.find("a")["href"]
                url = QuoteScraping.base_url + next_href
                time.sleep(random.uniform(self.delay[0], self.delay[1]))
            else:
                break

        return list(author_set)
    
    def scrape_author_quotes(self, author: str, print_quotes: bool = True) -> Dict[str, List[str]]:
        """ Scrapes quotes by a specific author from the quotes website.
        
        **Parameter:**
        - `author` (str): The name of the author whose quotes are to be scraped.
        - `print_quotes` (bool): If True, prints the quotes and their tags to the console. Default is True.
        
        **Returns:**
        `Dict[str, List[str]]`: A dictionary where keys are quotes and values are lists of tags associated with each quote.
        
        **Raises:**
        - `TypeError`: If the author name is not a string.
        - `TypeError`: If `print_quotes` is not a boolean.
        - `ValueError`: If no quotes are found for the specified author.
        - `Exception`: If there is an error fetching the page.
        
        **Example:**
        ```python
        scraper = QuoteScraping()
        scraper.scrape_author_quotes("Albert Einstein")
        ```
        """
        if not isinstance(author, str):
            raise TypeError("Author name must be a string.")
        if not isinstance(print_quotes, bool):
            raise TypeError("print_quotes must be a boolean value.")
        
        page_count = 0
        author_quotes = dict()
        author = author.lower().strip()
        url = QuoteScraping.base_url

        while url:
            try:
                response = self.session.get(url, timeout=self.timeout, headers=self.header)
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error fetching {url}: {e}")

            page_count += 1
            print(Fore.GREEN + f"Searching page {page_count}...")
            print()
            soup = BeautifulSoup(response.text, "html.parser")
            authors = soup.find_all("small", class_="author")

            for auth in authors:
                name = auth.get_text(strip=True).lower()

                if name == author:
                    quote = auth.find_parent("div", class_="quote")
                    text = quote.select_one("span.text").get_text(strip=True)
                    tags = [tag.get_text(strip=True) for tag in quote.select("a.tag")]

                    if print_quotes:
                        print(Fore.MAGENTA + f"📜 Quote: {text}")
                        print(Fore.CYAN + f"🏷️  Tags: {', '.join(tags)}")
                        print("-" * 60)

                    author_quotes[text] = tags
            
            print()
            next_button = soup.find("li", class_="next")

            if next_button:
                next_href = next_button.find("a")["href"]
                url = QuoteScraping.base_url + next_href
                time.sleep(random.uniform(self.delay[0], self.delay[1]))
            else:
                break
        
        if len(author_quotes) == 0:
            raise ValueError(f"No quotes found for author {author}.")
        
        return dict(author_quotes)
    
    def scrape_author_info(self, author: str, print_info: bool = True) -> Dict[str, str]:
        """ Scrapes information about a specific author from the quotes website.
        
        **Parameter:**
        - `author` (str): The name of the author whose information is to be scraped.
        - `print_info` (bool): If True, prints the author's information to the console. Default is True.
        
        **Returns:**
        `Dict[str, str]`: A dictionary containing the author's birth date, location, and a brief bio.
        
        **Raises:**
        - `TypeError`: If the author name is not a string.
        - `TypeError`: If `print_info` is not a boolean.
        - `ValueError`: If the author is not found on the site.
        - `Exception`: If there is an error fetching the page.
        
        **Example:**
        ```python
        scraper = QuoteScraping()
        scraper.scrape_author_info("Albert Einstein")
        ```
        """
        if not isinstance(author, str):
            raise TypeError("Author name must be a string.")
        if not isinstance(print_info, bool):
            raise TypeError("print_info must be a boolean value.")
        
        page_count = 0
        author = author.lower()
        url = QuoteScraping.base_url

        while url:
            try:
                response = self.session.get(url, timeout=self.timeout, headers=self.header)
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error fetching {url}: {e}")
            
            page_count += 1
            print(Fore.GREEN + f"Searching page {page_count}...")
            soup = BeautifulSoup(response.text, "html.parser")          
            authors = soup.find_all("small", class_="author")

            for auth in authors:
                name = auth.get_text(strip=True)

                if name.lower() == author:
                    quote = auth.find_parent("div", class_="quote")
                    about_href = quote.find("a", class_=None)["href"]
                    author_url = QuoteScraping.base_url + about_href

                    author_response = self.session.get(author_url, timeout=self.timeout, headers=self.header)
                    author_soup = BeautifulSoup(author_response.text, "html.parser")

                    born = author_soup.select_one("span.author-born-date").get_text(strip=True)
                    location = author_soup.select_one("span.author-born-location").get_text(strip=True)
                    description = author_soup.select_one("div.author-description").get_text(strip=True)
                    description = ".".join(description.split('.', maxsplit=6)[:5])

                    if print_info:
                        print()
                        print(f"👤 Author: {name}")
                        print(f"🎂 Born: {born}")
                        print(f"📍 Location: {location}")
                        print(f"📝 Bio: {description}")
                        print("-" * 70)

                    author_info = {"Born": born, "Location": location, "Bio": description}
                    return author_info
            
            next_button = soup.find("li", class_="next")

            if next_button:
                next_href = next_button.find("a")["href"]
                url = QuoteScraping.base_url + next_href
                time.sleep(random.uniform(self.delay[0], self.delay[1]))
            else:
                break

            raise ValueError(f"Author {author} not found.")
    
    def scrape_all_quotes(self) -> Dict[str, Dict[str, List[str]]]:
        """ Scrapes all quotes from the quotes website.
        
        **Returns:**
        `Dict[str, Dict[str, List[str]]]`: A dictionary where keys are author names and values are dictionaries with tags as keys and lists of quotes as values.
        
        **Raises:**
        - `Exception`: If there is an error fetching the page.
        
        **Example:**
        ```python
        scraper = QuoteScraping()
        all_quotes = scraper.scrape_all_quotes()
        ```
        """
        data = defaultdict(lambda: defaultdict(list))       # Quote data is stored here
        page_count = 0
        url = QuoteScraping.base_url

        while url:
            try:
                response = self.session.get(url, timeout=self.timeout, headers=self.header)     # Getting response from website
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error fetching {url}: {e}")

            soup = BeautifulSoup(response.text, "html.parser")
            quotes = soup.find_all("div", class_="quote")       # Find all quotes in 1 page

            page_count += 1
            print(f"Scraping page {page_count}...")

            for quote in quotes:
                text = quote.find("span", class_="text").get_text(strip=True)       # quote_text
                author = quote.find("small", class_="author").get_text(strip=True)      # author
                tags = [tag.get_text(strip=True) for tag in quote.find_all("a", class_="tag")]      # tags associated with the quote

                for tag in tags:
                    data[author][tag].append(text)      # Listing all quotes by author and tag

            next_button = soup.find("li", class_="next")        # Next button at the end of page for author_details

            if next_button:     # If next_buuton is availbale
                next_href = next_button.find("a")["href"]
                url = QuoteScraping.base_url + next_href      # url for next page
                time.sleep(random.uniform(self.delay[0], self.delay[1]))        # Delay requests to reduce traffic on website for next_page
            else:
                url = None

        return dict(data)

    def scrape_all_authors(self) -> Dict[str, str]:
        """ Scrapes information about all authors from the quotes website.
        
        **Returns:**
        `Dict[str, str]`: A dictionary where keys are author names and values are dictionaries with their birth date, location, and bio.
        
        **Raises:**
        - `Exception`: If there is an error fetching the page.
        
        **Example:**
        ```python
        scraper = QuoteScraping()
        all_authors = scraper.scrape_all_authors()
        ```
        """
        author_details = dict()      # Author details are stored here
        page_count = 0
        url = QuoteScraping.base_url
        
        while url:
            try:
                response = requests.get(url, timeout=5, headers=self.header)     # Getting response from website
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error fetching {url}: {e}")

            soup = BeautifulSoup(response.text, "html.parser")
            authors = soup.select("small.author")

            page_count += 1
            print(Fore.GREEN + f"Scraping page {page_count}...")
            print(Fore.CYAN + "Reading authors: ")

            for auth in authors:
                name = auth.get_text(strip=True)      # author name

                if name not in author_details:        # Scraping author details if not scraped
                    print(name)
                    quote = auth.find_parent("div", class_="quote") 
                    about_href = quote.find("a", class_=None)["href"]
                    author_url = QuoteScraping.base_url + about_href

                    author_response = requests.get(author_url)
                    author_soup = BeautifulSoup(author_response.text, "html.parser")

                    born = author_soup.find("span", class_="author-born-date").get_text(strip=True)
                    location = author_soup.find("span", class_="author-born-location").get_text(strip=True)[3:]
                    description = author_soup.select_one("div.author-description").get_text(strip=True)

                    author_details[name] = {"Born": born, "Location": location, "Bio": description}
                    time.sleep(random.uniform(self.delay[0], self.delay[1]))        # Delay requests to reduce traffic on website

            print()
            next_button = soup.find("li", class_="next")        # Next button at the end of page for author_details

            if next_button:     # If next_buuton is availbale
                next_href = next_button.find("a")["href"]
                url = QuoteScraping.base_url + next_href      # url for next page
                time.sleep(random.uniform(self.delay[0], self.delay[1]))        # Delay requests to reduce traffic on website
            else:
                url = None

        return author_details
    
    @staticmethod
    def write_to_json(data: Dict[str, Any], filename: str) -> None:
        """ Writes the scraped data to a JSON file.
        
        **Parameters:**
        - `data` (Dict[str, Any]): The data to be written to the JSON file.
        - `filename` (str): The name of the file where the data will be saved.

        **Raises:**
        - `TypeError`: If `filename` is not a string or `data` is not a dictionary.
        """
        if not isinstance(filename, str):
            raise TypeError("Filename must be a string")
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
        
        with open(file=filename, mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


class BookScraping(QuoteScraping):
    """
    A class for scraping books and their information from a books website.

    **Class Attributes:**
    - `base_url`: The base URL of the books website.
    - `rating_map`: A dictionary mapping rating text to numerical values.

    **Instance Attributes:**
    - `timeout`: Timeout for requests in seconds.
    - `session`: A requests session for making HTTP requests. Sessions are more efficient for multiple requests.
    - `header`: Headers to mimic a browser request.
    - `delay`: Random delay between requests to avoid increasing traffic on the server.

    **Methods:**    
    - `genre_list`: Scrapes the list of genres from the books website.
    - `scrape_books_from_genre`: Scrapes books from a specific genre on the books website.
    - `scrape_book_info`: Scrapes information about a specific book from its URL.
    - `scrape_all_books`: Scrapes all books from the books website.
    - `write_to_json`: Writes the scraped data to a JSON file (inherited from `QuoteScraping`).

    **Example:**
    ```python
    scraper = BookScraping()
    genres = scraper.genre_list()
    print(genres)
    ```
    """
    base_url = "https://books.toscrape.com/"
    rating_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    init(autoreset=True)
    
    def genre_list(self) -> List[str]:
        """ Scrapes the list of genres from the books website.
        
        **Returns:**
        `List[str]`: A list of genres available on the site.
        
        **Raises:**
        `Exception`: If there is an error fetching the page.
        
        **Example:**
        ```python
        scraper = BookScraping()
        genres = scraper.genre_list()
        print(genres)
        ```
        """
        try:
            response = self.session.get(url=BookScraping.base_url, timeout=self.timeout, headers=self.header)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching {BookScraping.base_url}: {e}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        side_panel = soup.find("ul", class_="nav nav-list")
        genres = side_panel.select("ul ul li")

        genre_list = [genre.find("a").get_text(strip=True) for genre in genres]
        return genre_list
    
    def scrape_books_from_genre(self, genre_name: str) -> Tuple[List[str], List[str]]:
        """ Scrapes books from a specific genre on the books website.
        
        **Parameter:**
        - `genre_name` (str): The name of the genre to scrape books from
        
        **Returns:**
        `Tuple[List[str], List[str]]`: A tuple containing two lists:
        - A list of book titles in the specified genre.
        - A list of corresponding book URLs.
        
        **Raises:**
        - `TypeError`: If `genre_name` is not a string.
        - `ValueError`: If `genre_name` is not present in the list of genres.
        - `Exception`: If there is an error fetching the page.
        
        **Example:**
        ```python
        scraper = BookScraping()
        books, urls = scraper.scrape_books_from_genre("science")
        print(books)
        print(urls)
        ```
        """
        if not isinstance(genre_name, str):
            raise TypeError("genre_name must be a string")
        
        genre_name = genre_name.lower()
        genre_list = list(map(lambda x: x.lower(), self.genre_list()))

        if genre_name not in [genre for genre in genre_list]:
            raise ValueError("genre_name not present")
        
        book_list = []
        book_url = []
        genre_index = genre_list.index(genre_name) + 2

        base_url = BookScraping.base_url + f"catalogue/category/books/{genre_name}_{genre_index}/index.html"
        url = base_url
        page_count = 0

        # Scraping a Genre
        while url:
            page_count += 1

            try:
                response = self.session.get(url=url, timeout=self.timeout, headers=self.header)
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error fetching {url}: {e}")
            
            print(Fore.GREEN + f"Scraping page {page_count}...")
            soup = BeautifulSoup(response.text, "html.parser")

            # All the books in the current page of the genre
            books = soup.select("article.product_pod")
            book_list.extend([book.h3.select_one("a")["title"] for book in books])
            hrefs = [book.h3.select_one("a")["href"] for book in books]
            book_url.extend([(BookScraping.base_url + "catalogue/" + href[9:]) for href in hrefs])

            # Looking for next button in the same genre
            next_button = soup.find("li", class_="next")

            if next_button:
                next_href = next_button.find("a")["href"]
                url = base_url.replace("index.html", next_href)
                time.sleep(random.uniform(self.delay[0], self.delay[1]))
            else:
                break
        
        return (book_list, book_url)
    
    def scrape_book_info(self, book_url: str) -> Dict[str, str]:
        """ Scrapes information about a specific book from its URL.
        
        **Parameter:**
        - `book_url` (str): The URL of the book to scrape information from.
        
        **Returns:**
        `Dict[str, str]`: A dictionary containing the book's UPC, price, rating, availability, and URL.
        
        **Raises:**
        - `TypeError`: If `book_url` is not a string.
        - `Exception`: If there is an error fetching the page.
        
        **Example:**
        ```python
        scraper = BookScraping()
        book_info = scraper.scrape_book_info("https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
        print(book_info)
        ```
        """
        if not isinstance(book_url, str):
            raise TypeError("book_url must be a string")
        
        try:
            response = self.session.get(url=book_url, timeout=self.timeout, headers=self.header)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching {book_url}: {e}")
        
        soup = BeautifulSoup(response.text, "html.parser")

        availability = soup.select_one("p", class_="instock availability").get_text(strip=True)      # availability
        price = soup.select_one("p.price_color").get_text(strip=True)       # price
        rating_text = soup.select_one("p.star-rating")["class"][-1].lower()
        rating = BookScraping.rating_map[rating_text]

        table = soup.find("table", class_="table table-striped")
        rows = table.select("tr")

        for row in rows:
            if row.select_one("th").get_text(strip=True) == 'UPC':
                upc = row.select_one("td").get_text(strip=True)     # UPC

        book_info = {"UPC": upc, "Price": price, "Rating": rating, "Availability": availability, "URL": book_url}     # Recording data
        return book_info
        
    def scrape_all_books(self) -> Tuple[List[str], List[str]]:
        """ Scrapes all books from the books website.
        
        **Returns:**
        `Tuple[List[str], List[str]]`: A tuple containing two lists:
        - A list of book titles.
        - A list of corresponding book URLs.
        
        **Raises:**
        `Exception`: If there is an error fetching the page.

        **Example:**
        ```python
        scraper = BookScraping()
        books, urls = scraper.scrape_all_books()
        print(books)
        print(urls)
        """
        url = BookScraping.base_url
        book_list = []
        book_url = []
        page_count = 0

        while url:
            page_count += 1

            try:
                response = self.session.get(url=url, timeout=self.timeout, headers=self.header)
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error fetching {url}: {e}")
            
            print(Fore.GREEN + f"Scraping page {page_count}...")
            soup = BeautifulSoup(response.text, "html.parser")

            books = soup.select("article.product_pod")
            book_list.extend([book.h3.select_one("a")["title"] for book in books])
            hrefs = [book.h3.select_one("a")["href"] for book in books]
            book_url.extend([(BookScraping.base_url + "catalogue/" + href[9:]) for href in hrefs])

            # Looking for next button in the same genre
            next_button = soup.find("li", class_="next")

            if next_button:
                next_href = next_button.find("a")["href"]

                if page_count == 1:
                    url = url + next_href
                else:
                    url = BookScraping.base_url + "catalogue/" + next_href

                time.sleep(random.uniform(self.delay[0], self.delay[1]))
            else:
                break
        
        return (book_list, book_url)