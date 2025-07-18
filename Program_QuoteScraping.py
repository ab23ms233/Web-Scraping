from colorama import Fore, init
from Class_Scraping import QuoteScraping
import os

def main():
    init(autoreset=True)
    invalid_text = Fore.RED + "WRONG input. Enter again"

    print()
    print(Fore.LIGHTYELLOW_EX + "Welcome to the Quotes Scraping Application!")

    quote_scraper = QuoteScraping()
    result = dict()

    print(Fore.LIGHTBLUE_EX + f"Website used for scraping: {QuoteScraping.base_url}")
    print()

    while True:
        print("Choose any one of the following:")
        print("1. Scrape list of authors")
        print("2. Scrape quotes of an author")
        print("3. Scrape the details of an author")
        print("4. Scrape all quotes")
        print("5. Scrape details of all authors")
        print("6. Exit")
        print()

        choice = int(input("Enter choice: "))
        print()

        while True:
            if choice == 1:
                result = quote_scraper.author_list()
                print()
            elif choice == 2:
                author = input("Enter the name of the author: ")
                print()

                while True:
                    try:
                        result[author] = quote_scraper.scrape_author_quotes(author)
                        break
                    except Exception:
                        print(Fore.RED + f"No quotes found for author {author}")
                        author = input("Enter the name of the author: ")
                        print()
                print()
            elif choice == 3:
                author = input("Enter the name of the author: ")
                print()

                while True:
                    try:
                        result[author] = quote_scraper.scrape_author_info(author)
                        break
                    except Exception:
                        print()
                        print(Fore.RED + f"No info found for author {author}")
                        author = input("Enter the name of the author: ")
                        print()
                print()
            elif choice == 4:
                result = quote_scraper.scrape_all_quotes()
                print()
                print(Fore.LIGHTGREEN_EX + "Successfully scraped all quotes")
                print()
            elif choice == 5:
                result = quote_scraper.scrape_all_authors()
                print()
                print(Fore.LIGHTGREEN_EX + "Successfully scraped all author details")
                print()
            elif choice == 6:

                if len(result) != 0:
                    while True:
                        save = input("Do you want to save your data (y/n)?: ").lower().strip()

                        if save == 'y':
                            if isinstance(result, list):
                                is_list = True 
                                file = input("Enter the name of the file (.txt): ")
                            elif isinstance(result, dict):
                                is_list = False
                                file = input("Enter the name of the file (.json): ")

                            if os.path.exists(file) and os.path.getsize(file) != 0:
                                while True:
                                    erase = input(Fore.LIGHTRED_EX + "Do you want to erase previous data (y/n)? ").lower().strip()

                                    if erase == 'y':
                                        mode = 'w'
                                        break
                                    elif erase == 'n':
                                        mode = 'a'
                                        break
                                    else:
                                        print(invalid_text)
                            else:
                                mode = 'w'

                            if is_list:
                                QuoteScraping.write_to_text(data=result, filename=file, mode=mode)
                            else:
                                QuoteScraping.write_to_json(data=result, filename=file, mode=mode)
                            break

                        elif save == 'n':
                            break

                        else:
                            print(invalid_text)

                print(Fore.LIGHTYELLOW_EX + "Thanks for using the Scraping Application")
                return
            else:
                print(invalid_text)
                break

            print("What's next on your mind?")
            print("1. Continue scraping and save the data to a file")
            print("2. Continue scraping without saving the data")
            print("3. Save the data to a file and exit")

            if choice in [2, 3]:
                print('''4. Continue scraping and add more data to the existing dataset (don't save yet)
This means you will be performing the same operation''')
                print()

            while True:
                next_choice = int(input())
                print()

                if next_choice in [1, 3]:
                    same_op = False

                    if choice == 1:
                        file = input("Enter the name of the file (.txt): ")
                    else:
                        file = input("Enter the name of the file (.json): ")

                    if os.path.exists(file) and os.path.getsize(file) != 0:
                        while True:
                            erase = input(Fore.LIGHTRED_EX + "Do you want to erase previous data (y/n)? ").lower().strip()

                            if erase == 'y':
                                mode = 'w'
                                break
                            elif erase == 'n':
                                mode = 'a'
                                break
                            else:
                                print(invalid_text)
                    else:
                        mode = 'w'
                    
                    if choice == 1:
                        QuoteScraping.write_to_text(data=result, filename=file, mode=mode)
                    else:
                        QuoteScraping.write_to_json(data=result, filename=file, mode=mode)

                    print(Fore.LIGHTGREEN_EX + "Successfully recorded all data")
                    print()

                    if next_choice == 3:
                        print(Fore.LIGHTYELLOW_EX + "Thanks for using the Scraping Application")
                        return
                    
                    result = dict()
                    break

                elif next_choice == 2:
                    same_op = False
                    result = dict()
                    break                    
                
                elif next_choice == 4 and choice in [2, 3]:
                    same_op = True
                    break

                else:
                    print(invalid_text)
                
            if not same_op:
                break


if __name__ == "__main__":
    main()










