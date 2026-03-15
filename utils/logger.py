import sys
from colorama import Fore, Style, init

init(autoreset=True)

class Logger:
    @staticmethod
    def info(message):
        print(f"{Fore.BLUE}[*]{Style.RESET_ALL} {message}")

    @staticmethod
    def success(message):
        print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {message}")

    @staticmethod
    def warning(message):
        print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {message}")

    @staticmethod
    def error(message):
        print(f"{Fore.RED}[-]{Style.RESET_ALL} {message}")

    @staticmethod
    def critical(message):
        print(f"{Fore.RED}{Style.BRIGHT}[CRITICAL] {message}")

    @staticmethod
    def prompt(message):
        return f"{Fore.CYAN}aura > {Style.RESET_ALL}"
