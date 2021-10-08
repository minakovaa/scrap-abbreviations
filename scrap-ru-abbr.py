import aiohttp
import asyncio
import re
import os
from bs4 import BeautifulSoup, element

from scrap import is_abbreviation, save_abbreviation_to_json, \
                  load_abbreviations_from_json, fetch_url, \
                  HEADERS_MAC

POSTFIXES_ON_NETLER_RU = ['', '-b', '-v', '-g', '-d', '-e', '-zh', '-z', '-i', '-j',
                          '-k', '-l', '-m', '-n', '-o', '-p', '-r', '-s', '-t', '-u',
                          '-f', '-h', '-c', '-ch', '-sh', '-sch', '-ea', '-ju', '-ja']


async def scrap_ru_abbr(event_loop):
    tasks = []

    async with aiohttp.ClientSession(loop=event_loop, headers=HEADERS_MAC) as session:
        for postfix in POSTFIXES_ON_NETLER_RU:
            page_with_abbreviations = f'http://netler.ru/slovari/abbreviature{postfix}.htm'
            tasks.append(
                asyncio.create_task(
                    fetch_url(session, page_with_abbreviations)
                )
            )

        html_responses = await asyncio.gather(*tasks)

        # Return dict with abbreviations as keys and their descriptions as values
        # Values may be not unique
        abbr_descr = parse_html_resoonses_netler_ru(html_responses)

    return abbr_descr


def parse_html_resoonses_netler_ru(html_responses):
    # Key - abbreviation, value - description
    # For example:
    # {"АБ": ["авиационная база (авиабаза)", "авиационная бомба"], ...}
    abbreviations_description = {}
    for html in html_responses:
        abbreviations_description.update(get_abbr_and_descriptions_netler_ru(html))

    return abbreviations_description


def get_abbr_and_descriptions_netler_ru(html):
    soup = BeautifulSoup(html, 'html.parser')
    p_blocks = soup.find_all('p')

    # key - abbreviation, value - description
    abbreviations_description = dict()

    for p in p_blocks:
        bold_abbr = p.find('b')
        if bold_abbr and len(bold_abbr.getText()) < 8:
            abbreviation = bold_abbr.getText()
            description = p.getText()

            description = re.sub(r'[\n\r\t]', '', description)

            description = description.split(" –", 1)
            if len(description) > 1:
                description = description[1]
            else:
                print(f'Error with abbreviation {abbreviation}')
                continue

            description = [re.sub(r'(^ *\d+\. )|(^ )', '', descr) for descr in description.split(';')]

            abbreviations_description.update({abbreviation: description})

    return abbreviations_description


def main_async_scrap_ru_abbreviations():
    event_loop = asyncio.get_event_loop()
    ru_abbr = event_loop.run_until_complete(scrap_ru_abbr(event_loop))

    return ru_abbr


if __name__ == "__main__":
    ru_json_filename = 'abbreviations/ru-abbr.json'

    if os.path.exists(ru_json_filename):
        ru_abbr = load_abbreviations_from_json(ru_json_filename)
    else:
        ru_abbr = main_async_scrap_ru_abbreviations()
        save_abbreviation_to_json(ru_abbr, ru_json_filename)

    print(f"There are {len(ru_abbr.keys())} Russian abbreviations")
