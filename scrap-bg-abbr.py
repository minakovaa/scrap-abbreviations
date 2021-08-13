import aiohttp
import asyncio
import re
import typing as tp
from bs4 import BeautifulSoup


HEADERS_MAC = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.11 (KHTML, like Gecko)'
                             ' Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',

               'Connection': 'keep-alive',
               }


async def scrap_bg_abbr(event_loop):
    tasks = []

    async with aiohttp.ClientSession(loop=event_loop, headers=HEADERS_MAC) as session:
        for i in range(1, 345, 1):  # 345 pages
            pages_list_phrases = f'https://frazite.com/abbrevs-{i}.html'
            tasks.append(
                asyncio.create_task(
                    fetch_url(session, pages_list_phrases)
                )
            )

        html_responses = await asyncio.gather(*tasks)

        # Return dict with abbreviations as keys and their descriptions as values
        # Values may be not unique
        abbr_descr = await parse_html_resoonses(html_responses, session, event_loop)

    return abbr_descr


async def fetch_url(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            html = await response.text()
            return html
        else:
            print(f'Url: {url}, response status: {response.status}')
            return None


async def parse_html_resoonses(html_responses, session, event_loop):
    abbreviations_link = {}
    for html in html_responses:
        abbreviations_link.update(
            find_links_and_get_abbr(html, session, event_loop)
        )

    tasks = []
    for abbreviation, link in abbreviations_link.items():
        tasks.append(
            asyncio.create_task(
                get_abbreviations_description(session, abbreviation, link)
            )
        )

    # abbreviations_description - is list of tuples (abbreviation, description)
    abbreviations_description = await asyncio.gather(*tasks)

    return dict(abbreviations_description)


def find_links_and_get_abbr(html, session, event_loop):
    soup = BeautifulSoup(html, 'html.parser')
    row_block = soup.find_all(class_='row')

    # key - abbreviation, value - link to page with description
    abbreviations_link = dict()

    for a in row_block[1].find_all('a', href=True):
        href = a['href']
        if a.contents and isinstance(a.contents[0], str):
            text = a.contents[0]

            if is_abbreviation(text):
                abbreviations_link[text] = 'https://frazite.com/' + href

    return abbreviations_link


async def get_abbreviations_description(session, abbreviation, link):
    """
        Return: tp.List[tp.Tuple[str, str]]
                list of pairs: (abbreviation, description)
    """
    # TODO: parse abbr page
    pass


def is_abbreviation(text):
    return text.isupper()


event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(scrap_bg_abbr(event_loop))
