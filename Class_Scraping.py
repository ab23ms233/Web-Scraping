import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Literal
import json
import random
import time
from colorama import Fore, init
import difflib


class CommonMethods:
    """
    A base class for common methods used in scraping applications.

    Instance Attributes:
    ---------------------------
        timeout: int 
            Timeout for requests in seconds.
        session: requests.Session 
            A requests session for making HTTP requests. Sessions are more efficient for multiple requests.
        header: Dict[str, str] 
            Headers to mimic a browser request.
        delay: List[int] 
            Random delay between requests to avoid increasing traffic on the server.

    Methods:
    ------------------------
    - `write_to_json`: Writes the scraped data to a JSON file.
    - `write_to_text`: Writes the scraped data to a text file.
    """
    def __init__(self) -> None:
        """
        Initializes the class with a session, headers, and timeout settings.

        Attributes:
            timeout (int): Timeout for requests in seconds. Recommended to keep it low to avoid long waits.
            session (requests.Session): A requests session for making HTTP requests. Sessions are more efficient for multiple requests.
            header (Dict[str, str]): Headers to mimic a browser request.
            delay (List[int]): Random delay between requests to avoid increasing traffic on the server.
        """
        self.timeout = 5
        self.session = requests.Session()
        self.header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"}      # Chrome browser string
        self.delay = [1, 2]

    @staticmethod
    def write_to_json(data: Dict[str, Dict[str, Any]], filename: str, mode: Literal['w', 'a']) -> None:
        """
        Writes the scraped data to a JSON file. Intended for storing quotes of an author or author details.
        
        Parameters:
            data (Dict[str, Dict[str, Any]]): The data to be written to the JSON file.
            filename (str): The name of the file where the data will be saved.
            mode (Literal['w', 'a']): The mode in which to open the file. 'w' for write (overwrites existing file), 'a' for append (adds to existing file).

        Raises:
            TypeError: If `filename` is not a string.
            ValueError: If `mode` is not 'w' or 'a'.
            TypeError: If `data` is not a dictionary.

        Example:
        ```python
        data = {
            "Author 1": {"Quote 1": ["tag1", "tag2"], "Quote 2": ["tag3"]},
            "Author 2": {"Quote 3": ["tag4"]}
        }
        QuoteScraping.write_to_json(data, "quotes.json", mode='w')
        """
        if not isinstance(data, dict):
            raise TypeError(Fore.RED + "Data must be a dictionary")
        if not isinstance(filename, str):
            raise TypeError(Fore.RED + "Filename must be a string")
        if mode not in ['w', 'a']:
            raise ValueError(Fore.RED + "Mode must be 'w' for write or 'a' for append")
        
        if mode == 'w':
            with open(file=filename, mode='w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        
        else:       # For appending data to existing file, read previous data first
            with open(file=filename, mode='r', encoding='utf-8') as f:
                previous_data = json.load(f)

                # Append current data into previous dictionary
                for i in data:
                    if i in previous_data:
                        previous_data[i].update(data[i])
                    else:
                        previous_data[i] = data[i]
            
            # Write final dictionary
            with open(file=filename, mode='w', encoding='utf-8') as f:
                json.dump(previous_data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def write_to_text(data: List[str], filename: str, mode: Literal['a', 'w']) -> None:
        """
        Writes the scraped data to a text file. Intended for storing author list.

        Parameters:
            data (List[str]): The data to be written to the text file.
            filename (str): The name of the file where the data will be saved.
            mode (Literal['a', 'w']): The mode in which to open the file. 'a' for append (adds to existing file), 'w' for write (overwrites existing file).

        Raises:
            TypeError: If `filename` is not a string.
            ValueError: If `mode` is not 'a' or 'w'.
            TypeError: If `data` is not a list.
         
        Example:
        ```python
        data = ["Author 1", "Author 2", "Author 3"]
        QuoteScraping.write_to_text(data, "authors.txt", mode='w')
        """
        if not isinstance(data, list):
            raise TypeError(Fore.RED + "Data must be a list")
        if not isinstance(filename, str):
            raise TypeError(Fore.RED + "Filename must be a string")
        if mode not in ['a', 'w']:
            raise ValueError(Fore.RED + "Mode must be 'a' for append or 'w' for write")
        
        with open(file=filename, mode=mode) as f:
            for i in data:
                element = str(i) + '\n'
                f.write(element)

class QuoteScraping(CommonMethods):
    """ 
    A class for scraping quotes and author information from a quotes website.
 
    Class Attributes:
    ----------------------
        base_url: str
            The base URL of the quotes website.
    
    Instance Attributes:
    ------------------------
        timeout: int 
            Timeout for requests in seconds.
        session: requests.Session 
            A requests session for making HTTP requests. Sessions are more efficient for multiple requests.
        header: Dict[str, str] 
            Headers to mimic a browser request.
        delay: List[int] 
            Random delay between requests to avoid increasing traffic on the server.
        author_details: Dict[str, str]
                A dictionary to store author names and their corresponding URLs. It is used to avoid repeated scraping of the same author.
 
    Methods:
    ----------------------------
    - `author_list`: Scrapes the list of authors from the quotes website.
    - `scrape_author_quotes`: Scrapes quotes by a specific author.
    - `scrape_author_info`: Scrapes information about a specific author.
    - `scrape_all_quotes`: Scrapes all quotes from the quotes website.
    - `scrape_all_authors`: Scrapes information about all authors from the quotes website.
    - `write_to_json`: Writes the scraped data to a JSON file (inherited from `CommonMethods`).
    - `write_to_text`: Writes the scraped data to a text file (inherited from `CommonMethods`).

    Example:
    ----------------------------
    ```python
    scraper = QuoteScraping()
    authors = scraper.author_list()
    print(authors)
    ```
    """
    base_url = "https://quotes.toscrape.com/"
    init(autoreset=True)

    def __init__(self) -> None:
        super().__init__()
        self.author_urls = dict()

    def author_list(self) -> List[str]:
        """
        Scrapes the list of authors from the quotes website.

        Returns:
            List[str]: A list of unique author names found on the site.
        """
        author_set = set()      # To avoid duplicate entries

        if len(self.author_urls) == 0:
            url = QuoteScraping.base_url  
            page_count = 0

            while url:
                try:
                    response = self.session.get(url, timeout=self.timeout, headers=self.header)
                except requests.exceptions.RequestException as e:
                    raise Exception(f"Error fetching {url}: {e}")

                page_count += 1
                print(Fore.GREEN + f"Scraping page {page_count}...")

                soup = BeautifulSoup(response.text, "html.parser")
                authors = soup.select("small.author")

                # Scrape all authors in current page
                for author in authors:
                    name = author.get_text(strip=True)
                    author_set.add(name)

                    if name not in self.author_urls:
                        about_href = author.find_parent("div", class_="quote").find("a", class_=None)["href"]
                        author_url = QuoteScraping.base_url + about_href
                        self.author_urls[name] = author_url

                self.author_urls["last page"] = page_count
                next_button = soup.find("li", class_="next")

                if next_button:
                    next_href = next_button.find("a")["href"]
                    url = QuoteScraping.base_url + next_href
                    time.sleep(random.uniform(self.delay[0], self.delay[1]))
                else:
                    self.author_urls["next href"] = None
                    break
            
            return list(author_set)
        
        else:
            if self.author_urls["next href"]:
                for name in self.author_urls:
                    if name in ["last page", "next href"]:
                        continue
                    author_set.add(name)

                url = QuoteScraping.base_url + self.author_urls["next href"]
                page_count = self.author_urls["next page"]

                while url:
                    try:
                        response = self.session.get(url, timeout=self.timeout, headers=self.header)
                    except requests.exceptions.RequestException as e:
                        raise Exception(f"Error fetching {url}: {e}")

                    page_count += 1
                    print(Fore.GREEN + f"Scraping page {page_count}...")

                    soup = BeautifulSoup(response.text, "html.parser")
                    authors = soup.select("small.author")

                    # Scrape all authors in current page
                    for author in authors:
                        name = author.get_text(strip=True)
                        author_set.add(name)

                        if name not in self.author_urls:
                            about_href = author.find_parent("div", class_="quote").find("a", class_=None)["href"]
                            author_url = QuoteScraping.base_url + about_href
                            self.author_urls[name] = author_url

                    self.author_urls["last page"] = page_count
                    next_button = soup.find("li", class_="next")

                    if next_button:
                        next_href = next_button.find("a")["href"]
                        url = QuoteScraping.base_url + next_href
                        time.sleep(random.uniform(self.delay[0], self.delay[1]))
                    else:
                        self.author_urls["next href"] = None
                        break
                
                return list(author_set)
                    
            else:
                names = list(self.author_urls.keys())
                names.remove("last page")
                names.remove("next href")
                return names
            
    def scrape_author_quotes(self, author: str, print_quotes: bool = True) -> Dict[str, List[str]]:
        """
        Scrapes quotes by a specific author from the quotes website.
        
        Parameters:
            author (str): The name of the author whose quotes are to be scraped.
            print_quotes (bool): If True, prints the quotes and their tags to the console. Default is True.
        
        Returns:
            dict: A dictionary where keys are quotes and values are lists of tags associated with each quote.
        
        Raises:
            TypeError: If the author name is not a string.
            TypeError: If `print_quotes` is not a boolean.
            ValueError: If no quotes are found for the specified author.
            Exception: If there is an error fetching the page.
        
        Example:
        ```python
        scraper = QuoteScraping()
        scraper.scrape_author_quotes("Albert Einstein")
        ```
        """
        if not isinstance(author, str):
            raise TypeError(Fore.RED + "Author name must be a string.")
        if not isinstance(print_quotes, bool):
            raise TypeError(Fore.RED + "print_quotes must be a boolean value.")
        
        page_count = 0
        author_quotes = dict()
        author = author.lower().strip()
        url = QuoteScraping.base_url

        while url:
            try:
                response = self.session.get(url, timeout=self.timeout, headers=self.header)
            except requests.exceptions.RequestException as e:
                raise Exception(Fore.RED + f"Error fetching {url}: {e}")

            page_count += 1
            print(Fore.GREEN + f"Searching page {page_count}...")
            print()
            soup = BeautifulSoup(response.text, "html.parser")
            authors = soup.find_all("small", class_="author")   # All authors in current page

            for auth in authors:
                name = auth.get_text(strip=True).lower()
                similarity = difflib.SequenceMatcher(None, name, author, autojunk=True).ratio()

                # If name matches, scrape quote and tags
                if similarity >= 0.85:
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
            raise ValueError(Fore.RED + f"No quotes found for author {author}.")
        
        return author_quotes
        
    def get_author_url(self, author: str) -> str:
        """
        Gets the URL of a specific author from the quotes website.

        Parameters:
            author (str): The name of the author whose URL is to be fetched.

        Returns:
            str: The URL of the author on the quotes website.

        Raises:
            TypeError: If the author name is not a string.
            ValueError: If the author is not found on the site.
            Exception: If there is an error fetching the page.

        Example:
        ```python
        scraper = QuoteScraping()
        author_url = scraper.get_author_url("Albert Einstein")
        print(author_url)
        """
        if not isinstance(author, str):
            raise TypeError(Fore.RED + "author must be a string")
        
        author = author.lower().strip()      # Normalizing author name
        similarity_cutoff = 0.85        # Passed author name and actual author name must have this similarity to be considered

        if len(self.author_urls) != 0:    # Checking if author_url is present   
            match = difflib.get_close_matches(author, self.author_urls.keys(), n=1, cutoff=0.85)

            if match:       # If author_url is already present
                name = match[0]
                author_url = self.author_urls[name]
                return author_url

            else:       # If author_url is not present
                page_count = self.author_urls["last page"]    # Last page that was fully scraped
                next_href = self.author_urls["next href"]    # href for next page to be scraped
                url = QuoteScraping.base_url + next_href    # url for current page

        else:       # If author_url is not present
            page_count = 0
            url = QuoteScraping.base_url

        if page_count == 1:
            print(f"Author not found in page 1")
        else:
            print(f"Author not found in pages 1-{page_count}")
        
        while url:
            try:
                response = self.session.get(url, timeout=self.timeout, headers=self.header)
            except requests.exceptions.RequestException as e:
                raise Exception(Fore.RED + f"Error fetching {url}: {e}")
            
            page_count += 1
            print(Fore.GREEN + f"Searching page {page_count}...")
            soup = BeautifulSoup(response.text, "html.parser")          
            authors = soup.find_all("small", class_="author")       # All authors in current page

            for auth in authors:
                name = auth.get_text(strip=True)
                normalised_name = name.lower()      # Normalizing author name

                quote = auth.find_parent("div", class_="quote")
                about_href = quote.find("a", class_=None)["href"]
                author_url = QuoteScraping.base_url + about_href    # Scraping author_url

                self.author_urls[normalised_name] = author_url   # Storing author name and url, even if it does not match, for later use
                similarity = difflib.SequenceMatcher(isjunk=None, a=normalised_name, b=author).ratio()

                if similarity >= similarity_cutoff:      # If author name matches
                    return author_url
            
            # Pagination
            next_button = soup.find("li", class_="next")
            self.author_urls["last page"] = page_count      # Updating last page scraped

            if next_button:
                next_href = next_button.find("a")["href"]
                url = QuoteScraping.base_url + next_href
                self.author_urls["next href"] = next_href       # Updating next page to be scraped
                time.sleep(random.uniform(self.delay[0], self.delay[1]))    # Reduce traffic on website
            else:
                self.author_urls["next href"] = None
                break
            
        raise ValueError(Fore.RED + f"Author {author} not found.")

    def scrape_author_info(self, author_url: str, print_info: bool = True) -> Dict[str, str]:
        """
        Scrapes information about a specific author from their URL.
        
        Parameters:
            author_url (str): The URL of the author whose information is to be scraped.
            print_info (bool): If True, prints the author's information to the console. Default is True.
        
        Returns:
            dict: A dictionary containing the author's birth date, location, and a brief bio.
        
        Raises:
            TypeError: If the author_url is not a string.
            TypeError: If `print_info` is not a boolean.
            Exception: If there is an error fetching the page.
        
        Example:
        ```python
        scraper = QuoteScraping()
        
        ```
        """
        if not isinstance(author_url, str):
            raise TypeError(Fore.RED + "author_url must be a string.")
        if not isinstance(print_info, bool):
            raise TypeError(Fore.RED + "print_info must be a boolean value.")

        try:
            author_response = self.session.get(author_url, timeout=self.timeout, headers=self.header)
        except requests.exceptions.RequestException as e:
            raise Exception(Fore.RED + f"Error fetching {author_url}: {e}")
        
        author_soup = BeautifulSoup(author_response.text, "html.parser")

        name = author_soup.select_one("h3.author-title").get_text(strip=True)      # Author name
        born = author_soup.select_one("span.author-born-date").get_text(strip=True)
        location = author_soup.select_one("span.author-born-location").get_text(strip=True)
        description = author_soup.select_one("div.author-description").get_text(strip=True)
        description = ".".join(description.split('.', maxsplit=6)[:5])      # Display only part of the description to keep it short

        if print_info:
            print()
            print(f"👤 Author: {name}")
            print(f"🎂 Born: {born}")
            print(f"📍 Location: {location}")
            print(f"📝 Bio: {description}")
            print("-" * 60)

        author_info = {"Born": born, "Location": location, "Bio": description}
        return author_info

    def scrape_all_quotes(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Scrapes all quotes from the quotes website.
        
        Returns:
            dict: A dictionary where keys are author names and values are dictionaries with tags as keys and lists of quotes as values.
        
        Raises:
            Exception: If there is an error fetching the page.
        
        Example:
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
                raise Exception(Fore.RED + f"Error fetching {url}: {e}")

            soup = BeautifulSoup(response.text, "html.parser")
            quotes = soup.find_all("div", class_="quote")       # Find all quotes in 1 page

            page_count += 1
            print(Fore.GREEN + f"Scraping page {page_count}...")

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
        """
        Scrapes information about all authors from the quotes website.
        
        Returns:
            dict: A dictionary where keys are author names and values are dictionaries with their birth date, location, and bio.
        
        Raises:
            Exception: If there is an error fetching the page.
        
        Example:
        ```python
        scraper = QuoteScraping()
        all_authors = scraper.scrape_all_authors()
        ```
        """
        author_details = dict()      # Author details are stored here

        if len(self.author_urls) == 0:
            page_count = 0
            url = QuoteScraping.base_url

        else:
            for name in self.author_urls:
                if name in ["last page", "next_href"]:
                    continue

                author_url = self.author_urls[name]
                author_details[name] = self.scrape_author_info(author_url, print_info=False)
            
            if self.author_urls["next href"]:
                url = QuoteScraping.base_url + self.author_urls["next href"]
                page_count = self.author_urls["last page"]

        while url:
            try:
                response = requests.get(url, timeout=5, headers=self.header)     # Getting response from website
            except requests.exceptions.RequestException as e:
                raise Exception(Fore.RED + f"Error fetching {url}: {e}")
            
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
                    self.author_urls[name] = author_url

                    author_response = requests.get(author_url)
                    author_soup = BeautifulSoup(author_response.text, "html.parser")

                    born = author_soup.find("span", class_="author-born-date").get_text(strip=True)
                    location = author_soup.find("span", class_="author-born-location").get_text(strip=True)[3:]
                    description = author_soup.select_one("div.author-description").get_text(strip=True)
                    author_details[name] = {"Born": born, "Location": location, "Bio": description}

                    time.sleep(random.uniform(self.delay[0], self.delay[1]))        # Delay requests to reduce traffic on website
            
            print()
            self.author_urls["last page"] = page_count
            next_button = soup.find("li", class_="next")        # Next button at the end of page for author_details
            
            if next_button:     # If next_buuton is availbale
                next_href = next_button.find("a")["href"]
                url = QuoteScraping.base_url + next_href      # url for next page
                time.sleep(random.uniform(self.delay[0], self.delay[1]))        # Delay requests to reduce traffic on website
            else:
                url = None
                self.author_urls["next href"] = None
            
        return author_details



class BookScraping(CommonMethods):
    """
    A class for scraping books and their information from a books website.

    Class Attributes:
    -----------------------------
        base_url: str
            The base URL of the books website.
        rating_map: Dict[str, int]
            A dictionary mapping rating text to numerical values.

    Instance Attributes:
    ------------------------
        timeout: int 
            Timeout for requests in seconds.
        session: requests.Session 
            A requests session for making HTTP requests. Sessions are more efficient for multiple requests.
        header: Dict[str, str] 
            Headers to mimic a browser request.
        delay: List[int] 
            Random delay between requests to avoid increasing traffic on the server.

    Methods:
    ----------------------------
    - `genre_list`: Scrapes the list of genres from the books website.
    - `scrape_books_from_genre`: Scrapes books from a specific genre on the books website.
    - `scrape_book_info`: Scrapes information about a specific book from its URL.
    - `scrape_all_books`: Scrapes all books from the books website.
    - `write_to_json`: Writes the scraped data to a JSON file (inherited from `CommonMethods`).
    - `write_to_text`: Writes the scraped data to a text file (inherited from `CommonMethods`).

    Example:
    -----------------------------
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
        """
        Scrapes the list of genres from the books website.
        
        Returns:
            List[str]: A list of genres available on the site.
        
        Raises:
            Exception: If there is an error fetching the page.
        
        Example:
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
        """ 
        Scrapes books from a specific genre on the books website.
        
        Parameters:
            genre_name (str): The name of the genre to scrape books from
        
        Returns:
            tuple: A tuple containing two lists:
            - A list of book titles in the specified genre.
            - A list of corresponding book URLs.
        
        Raises:
            TypeError: If `genre_name` is not a string.
            ValueError: If `genre_name` is not present in the list of genres.
            Exception: If there is an error fetching the page.
        
        Example:
        ```python
        scraper = BookScraping()
        books, urls = scraper.scrape_books_from_genre("science")
        print(books)
        print(urls)
        ```
        """
        if not isinstance(genre_name, str):
            raise TypeError(Fore.RED + "genre_name must be a string")
        
        genre_name = genre_name.lower()
        genre_list = list(map(lambda x: x.lower(), self.genre_list()))

        if genre_name not in [genre for genre in genre_list]:
            raise ValueError(Fore.RED + "genre_name not present")
        
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
                raise Exception(Fore.RED + f"Error fetching {url}: {e}")
            
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
    
    def scrape_book_info(self, book_url: str, print_info: bool = True) -> Dict[str, str]:
        """
        Scrapes information about a specific book from its URL.
        
        Parameters:
            book_url (str): The URL of the book to scrape information from.
            print_info (bool): If True, prints the book's information to the console. Default is True.
        
        Returns:
            dict: A dictionary containing the book's UPC, price, rating, availability, and URL.
        
        Raises:
            TypeError: If `book_url` is not a string.
            Exception: If there is an error fetching the page.
        
        Example:
        ```python
        scraper = BookScraping()
        book_info = scraper.scrape_book_info("https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
        print(book_info)
        ```
        """
        if not isinstance(book_url, str):
            raise TypeError(Fore.RED + "book_url must be a string")
        if not isinstance(print_info, bool):
            raise TypeError(Fore.RED + "print_info must be a boolean value")
        
        try:
            response = self.session.get(url=book_url, timeout=self.timeout, headers=self.header)
        except requests.exceptions.RequestException as e:
            raise Exception(Fore.RED + f"Error fetching {book_url}: {e}")
        
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
        
        if print_info:
            print(Fore.YELLOW + f"📦 UPC: {upc}")
            print(Fore.GREEN + f"💰 Price: {price}")
            print(Fore.BLUE + f"⭐ Rating: {rating} out of 5")
            print(Fore.LIGHTYELLOW_EX + f"📍 Availability: {availability}")
            print(Fore.CYAN + f"🔗 URL: {book_url}")
            print("-" * 60)

        book_info = {"UPC": upc, "Price": price, "Rating": rating, "Availability": availability, "URL": book_url}     # Recording data
        return book_info
        
    def scrape_all_books(self) -> Tuple[List[str], List[str]]:
        """
        Scrapes all books from the books website.
        
        Returns:
            tuple: A tuple containing two lists:
            - A list of book titles.
            - A list of corresponding book URLs.
        
        Raises:
            Exception: If there is an error fetching the page.

        Example:
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
                raise Exception(Fore.RED + f"Error fetching {url}: {e}")
            
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
    
    def __init__(self) -> None:
        super().__init__()
        self.book_url, self.book_list = self.scrape_all_books()  # Scraping all books at the start