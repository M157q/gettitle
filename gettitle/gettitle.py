#!/usr/bin/env python3

import argparse
import sys
import urllib

import pyperclip
from selenium import webdriver

import gettitle.special_sites
import gettitle.exceptions
import gettitle.handles


def set_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    # Prevent from "from tab crashed error"
    # <https://stackoverflow.com/questions/53902507/unknown-error-session-deleted-because-of-page-crash-from-unknown-error-cannot>
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Bypass CloudFlare
    # <https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec/53040904#53040904>
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    browser = webdriver.Chrome(options=options)

    return browser


def unset_browser(browser):
    browser.quit()


def get_args():
    p = argparse.ArgumentParser(
        description='Get webpage title(s) by url(s) from terminal.'
    )
    p.add_argument(
        'urls',
        metavar='url',
        type=str,
        nargs='+',
        help="url(s) of the webpage",
    )
    p.add_argument(
        '-s', '--syntax',
        choices=['md', 'rst'],
        default=None,
        help="choose output syntax. 'md' for Markdown, 'rst' for reStructuredText.",
    )
    p.add_argument(
        '-ul', '--unordered-list',
        action='store_true',
        help="Enable this option for using Unordered List. Only works when syntax is Markdown or reStructuredText.",
    )
    p.add_argument(
        '-c', '--compact',
        action='store_true',
        help="output in compact mode. (No empty line between each result.)",
    )
    p.add_argument(
        '-d', '--debug',
        action='store_true',
        help="print out webpage source code and title for debugging",
    )

    return p.parse_args()


def combine_title_and_url(args, title, url):
    title = title.strip()
    url = url.strip()

    if args.syntax == "md":
        title = title.replace('[', r'\[').replace(']', r'\]')
        s = "[{title}]({url})"

        if args.unordered_list:
            s = "- " + s

    elif args.syntax == "rst":
        s = "`{title} <{url}>`_"

        if args.unordered_list:
            s = "* " + s

    else:
        s = "{title}\n{url}"

    return s.format(title=title, url=url)


def check_and_reconstruct_url(url):
    url = url.strip()
    url_components = urllib.parse.urlparse(url)

    if not url:
        raise gettitle.exceptions.EmptyUrlError
    elif not url_components.scheme:
        url = "{}://{}".format('http', url)
        url_components = urllib.parse.urlparse(url)
    elif url_components.scheme not in ('http', 'https'):
        url_components = url_components._replace(scheme='http')

    return urllib.parse.urlunparse(url_components)


def visit_with_browser(browser, checked_url, debug=False):
    title, real_url = None, None

    try:
        browser.get(checked_url)
    except Exception as e:
        gettitle.handles.handle_error(e, debug)
    else:
        title = browser.title
        real_url = browser.current_url

    # Check if this website needs to be visited with Selenium
    for url, handler in gettitle.special_sites.URL_AND_HANDLER_MAPPING.items():
        if url in real_url:
            try:
                title, real_url = handler(browser)
            except Exception as e:
                gettitle.handles.handle_error(e, debug)
            else:
                break

    if debug:
        print(browser.page_source)

    return title, real_url


def get_title_and_url(browser, url, debug=False):
    try:
        checked_url = check_and_reconstruct_url(url)
    except gettitle.exceptions.EmptyUrlError:
        raise

    try:
        title, url = visit_with_browser(browser, checked_url, debug)
    except Exception as e:
        gettitle.handles.handle_error(e)

    return title.strip(), url.strip()


def get_titles_and_urls(browser, args):
    titles_and_urls = []

    for url_from_user in args.urls:
        try:
            title, url = get_title_and_url(browser, url_from_user, args.debug)
        except Exception:
            continue
        else:
            s = combine_title_and_url(args, title, url)
            if not args.compact:
                s += '\n'
            titles_and_urls.append(s)

        if args.debug:
            print(title, type(title))

    return titles_and_urls


def print_titles_and_urls(titles_and_urls):
    if titles_and_urls:
        print('=' * 80)
        print('\n'.join(titles_and_urls))
        print('=' * 80)


def clipboard_available():
    copy_board, paste_board = pyperclip.determine_clipboard()
    no_copy_board, no_paste_board = pyperclip.init_no_clipboard()

    if repr(type(copy_board)) == repr(type(no_copy_board)):
        return False

    if repr(type(paste_board)) == repr(type(no_paste_board)):
        return False

    return True


def copy_result_to_clipboard_for_users(titles_and_urls, debug=False):
    '''
    This function currently only support Linxu users with `xclip` installed.
    '''
    text = '\n'.join(titles_and_urls)
    try:
        pyperclip.copy(text)
    except Exception as e:
        gettitle.handles.handle_error(e, debug)
    else:
        print("Copied to clipboard.")


def main():
    args = get_args()

    try:
        browser = set_browser()
    except Exception as e:
        gettitle.handles.handle_error(e)
    else:
        titles_and_urls = get_titles_and_urls(browser, args)
    finally:
        unset_browser(browser)

    print_titles_and_urls(titles_and_urls)

    if clipboard_available():
        copy_result_to_clipboard_for_users(titles_and_urls, args.debug)


if __name__ == '__main__':
    status = main()
    sys.exit(status)
