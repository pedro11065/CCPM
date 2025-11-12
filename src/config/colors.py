from colorama import Fore, Style

def red(text):
    return Fore.RED + Style.BRIGHT + text + Style.RESET_ALL

def green(text):
    return Fore.GREEN + Style.BRIGHT + text + Style.RESET_ALL

def yellow(text):
    return Fore.YELLOW + Style.BRIGHT + text + Style.RESET_ALL

def blue(text):
    return Fore.BLUE + Style.BRIGHT + text + Style.RESET_ALL

def magenta(text):
    return Fore.MAGENTA + Style.BRIGHT + text + Style.RESET_ALL

def cyan(text):
    return Fore.CYAN + Style.BRIGHT + text + Style.RESET_ALL

def white(text):
    return Fore.WHITE + Style.BRIGHT + text + Style.RESET_ALL

def reset(text):
    return Style.RESET_ALL + text