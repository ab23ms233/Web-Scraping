from colorama import Fore, init
from Class_Scraping import BookScraping
import os

def main():
    init(autoreset=True)
    invalid_text = Fore.RED + "WRONG input. Enter again"

    print()
    print(Fore.LIGHTYELLOW_EX + "Welcome to the Quotes Scraping Application!")

    book_scraper = BookScraping()
    result = dict()

    print(Fore.LIGHTBLUE_EX + f"Website used for scraping: {BookScraping.base_url}")
    print()