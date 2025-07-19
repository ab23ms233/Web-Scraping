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

    while True:
        print("Choose any one of the following:")
        print("1. Scrape list of genres")
        print("2. Scrape book titles of a genre")
        print("3. Scrape details of a book")
        print("4. Scrape all book titles")
        print("6. Exit")
        print()
        choice = input("Enter choice: ")
        print()

        while True:

            if choice.isdigit() and int(choice) in [1, 2, 3, 4, 6]:
                choice = int(choice)
            else:
                print(invalid_text)
                choice = input("Enter choice: ")
                print()
            
            if choice == 1:
                result = book_scraper.genre_list()
                print(Fore.CYAN + "Genres found:")

                for genre in result:
                    print(f"- {genre}")
                print()
            elif choice == 2:
                genre = input("Enter the name of the genre: ")
                print()

                while True:
                    try:
                        result[genre] = book_scraper.scrape_books_from_genre(genre)
                        break
                    except Exception:
                        print(Fore.RED + f"No books found for genre {genre}")
                        genre = input("Enter the name of the genre: ")
                        print()
                print()
            
            elif choice == 3:
            