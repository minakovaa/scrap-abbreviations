import json

HEADERS_MAC = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.11 (KHTML, like Gecko)'
                             ' Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',

               'Connection': 'keep-alive',
               }


async def fetch_url(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            html = await response.text()
            return html
        else:
            print(f'Url: {url}, response status: {response.status}')
            return None


def is_abbreviation(text):
    return text.isupper()


def save_abbreviation_to_json(abbreviations: dict, json_filename: str):
    with open(json_filename, 'w') as fp:
        json.dump(abbreviations, fp, ensure_ascii=False)


def load_abbreviations_from_json(json_filename: str):
    loaded_bg_abbr = {}
    with open(json_filename, 'r') as fp:
        loaded_bg_abbr = json.load(fp)

    return loaded_bg_abbr


