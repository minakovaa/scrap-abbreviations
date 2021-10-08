import aiohttp
import asyncio
import re
import os
from bs4 import BeautifulSoup, element

from scrap import is_abbreviation, save_abbreviation_to_json, \
                  load_abbreviations_from_json, fetch_url, \
                  HEADERS_MAC

NUMBER_OF_FRAZITE_COM_PAGES = 345


async def scrap_bg_abbr(event_loop):
    tasks = []

    async with aiohttp.ClientSession(loop=event_loop, headers=HEADERS_MAC) as session:
        for i in range(1, NUMBER_OF_FRAZITE_COM_PAGES, 1):
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

    return {abbr: descr for pair in abbreviations_description for abbr, descr in pair.items()}


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
    html = await fetch_url(session, link)

    soup = BeautifulSoup(html, 'html.parser')
    first_p_block = soup.find('p')  # Find first <p>

    if first_p_block:
        description = ' '.join([content for content in first_p_block.contents[1:]
                                if type(content) is element.NavigableString])
    else:
        print(abbreviation)
        return {}

    description = re.sub(r'[\n\r]', '', description)
    description = [re.sub(r'(^ *\d+\. )|(^ )', '', descr) for descr in description.split(';')]

    return {abbreviation: description}


def main_async_scrap_bg_abbreviations():
    event_loop = asyncio.get_event_loop()
    bg_abbr = event_loop.run_until_complete(scrap_bg_abbr(event_loop))

    return bg_abbr


if __name__ == "__main__":
    bg_json_filename = "abbreviations/bg-abbr.json"

    if os.path.exists(bg_json_filename):
        bg_abbr = load_abbreviations_from_json(bg_json_filename)
    else:
        bg_abbr = main_async_scrap_bg_abbreviations()
        save_abbreviation_to_json(bg_abbr, 'abbreviations/bg-abbr.json')

    print(f"There are {len(bg_abbr.keys())} Bulgarian abbreviations")
