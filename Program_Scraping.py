from colorama import Fore, init
from Class_Scraping import QuoteScraping

def main():
    init(autoreset=True)
    invalid_text = Fore.RED + "WRONG input. Enter again"

    print()
    print(Fore.LIGHTYELLOW_EX + "Welcome to the Quotes Scraping Application!")

    quote_scraper = QuoteScraping()
    result = dict()

    print(Fore.LIGHTBLUE_EX + "Website used for scraping: https://quotes.toscrape.com/")
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
                print("Authors found:")

                for author in result:
                    print(author)
                print()

            elif choice == 2:
                author = input(Fore.CYAN + "Enter the name of the author: ")
                result[author] = quote_scraper.scrape_author_quotes(author)
            elif choice == 3:
                author = input(Fore.CYAN + "Enter the name of the author: ")
                result[author] = quote_scraper.scrape_author_info(author)
            elif choice == 4:
                result = quote_scraper.scrape_all_quotes()
                print(Fore.LIGHTGREEN_EX + "Successfully scraped all quotes")
            elif choice == 5:
                result = quote_scraper.scrape_all_authors()
                print(Fore.LIGHTGREEN_EX + "Successfully scraped all author details")
            elif choice == 6:
                print(Fore.LIGHTYELLOW_EX + "Thanks for using the Scraping Application")
                return
            else:
                print(invalid_text)
                break

            print("What's next on your mind?")
            print("1. Continue scraping and save the data to a json file")
            print("2. Continue scraping without saving the data")
            print("3. Save the data to a json file and exit")

            if choice in [2, 3]:
                print('''4. Continue scraping and add more data to the existing dataset (don't save yet)\n
This means you will be performing the same operation''')

            while True:
                next_choice = int(input())
                print()

                if next_choice == 1:
                    same_op = False
                    file = input("Enter the name of the file (json): ")
                    quote_scraper.write_to_json(result, file)
                    print(Fore.LIGHTGREEN_EX + "Successfully recorded all data")
                    break

                elif next_choice == 2:
                    same_op = False
                    break

                elif next_choice == 3:
                    file = input("Enter the name of the file (json): ")
                    quote_scraper.write_to_json(result, file)
                    print(Fore.LIGHTGREEN_EX + "Successfully recorded all data")
                    print()
                    print(Fore.LIGHTYELLOW_EX + "Thanks for using the Scraping Application")
                    return
                
                elif next_choice == 4 and choice in [2, 3]:
                    same_op = True
                    break

                else:
                    print(invalid_text)
                
            if not same_op:
                break










