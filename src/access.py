import json
import os
import re

import requests
from bs4 import BeautifulSoup

import config
from EnemyType import EnemyType


def read_enemy_type_index(p_type: EnemyType) -> tuple[list[str], list[str]]:
    """ reads enemies' index of given enemy type """

    assert isinstance(p_type, EnemyType)

    names = []
    urls = []

    url = config.PREFIX + '/wiki/Enemy'

    match p_type:
        case EnemyType.NORMAL:
            url += '/Normal'
        case EnemyType.ELITE:
            url += '/Elite'
        case EnemyType.BOSS:
            url += '/Boss'
        case EnemyType.ECHO_OF_WAR:
            url += '/Echo_of_War'
        case _:
            raise Exception('ERROR: Unhandled EnemyType {}'.format(p_type))

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    res = soup.select('table.wikitable.sortable')[0]

    for tag in res.select('span.hidden a'):
        names.append(tag['title'])
        urls.append(tag['href'])

    return names, urls


def read_enemies_index() -> tuple[list[str], list[str]]:
    """ reads all enemies' index """

    n_names, n_urls = read_enemy_type_index(EnemyType.NORMAL)
    e_names, e_urls = read_enemy_type_index(EnemyType.ELITE)
    b_names, b_urls = read_enemy_type_index(EnemyType.BOSS)
    ew_names, ew_urls = read_enemy_type_index(EnemyType.ECHO_OF_WAR)

    return n_names + e_names + b_names + ew_names, n_urls + e_urls + b_urls + ew_urls


def read_enemy_data(p_url: str) -> dict:
    """  """

    assert isinstance(p_url, str)

    url = config.PREFIX + p_url

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    query = soup.select('a[title="Damage RES"]')
    damage_res = {}
    if not query:
        for key in config.DAMAGE_DICT.values():
            damage_res[key] = None
    else:
        for key, tag in enumerate(query[0].parent.parent.parent.contents[-1].select('td')):
            damage_res[config.DAMAGE_DICT[key]] = int(re.search(r'(\d+)', tag.string.strip()).group(1))

    query = soup.select('a[title="Debuff RES"]')
    debuff_res = {}
    if not query:
        for key in config.DEBUFF_DICT.values():
            debuff_res[key] = None
    else:
        for key, tag in enumerate(query[0].parent.parent.parent.contents[-1].select('td')):
            debuff_res[config.DEBUFF_DICT[key]] = int(re.search(r'(\d+)', tag.string.strip()).group(1))

    query = soup.select('a[title="Effect RES"]')
    effect_res = None
    if query:
        effect_res = int(re.search(r'(\d+)', query[0].parent.parent.parent.contents[1].select('td')[-1].string).group(1))

    return {'damage res': damage_res, 'debuff res': debuff_res, 'effect res': effect_res}


def update():

    # get all currently available enemies' urls
    current_enemies_names, current_enemies_urls = read_enemies_index()

    # check if 'data' folder exists
    if not os.path.exists('../data'):
        # create if not
        os.mkdir('../data')

    # check if enemies' index file exists
    if not os.path.isfile('../data/enemies_index.json'):
        # create if not and fill
        with open('../data/enemies_index.json', 'w') as f:
            json.dump([], f)

        # mark them for info retrieval
        new_enemies_urls = current_enemies_urls
        new_enemies_names = current_enemies_names
    else:
        # read its contents if it does
        with open('../data/enemies_index.json', 'r') as f:
            indexed_enemies_urls = json.load(f)

        # mark those of currently available enemies' urls that are not indexed for info retrieval
        indexes = [i for i, current_enemy_url in enumerate(current_enemies_urls) if current_enemy_url not in indexed_enemies_urls]

        new_enemies_urls = [current_enemies_urls[i] for i in indexes]
        new_enemies_names = [current_enemies_names[i] for i in indexes]

    # list with info retrieved
    new_enemies = []
    # for every new enemy url
    for key, new_enemy_url in enumerate(new_enemies_urls):
        # read info
        info = read_enemy_data(new_enemy_url)
        # and append it to list
        new_enemies.append({
            'name':       new_enemies_names[key],
            'url':        new_enemy_url,
            'damage res': info['damage res'],
            'debuff res': info['debuff res'],
            'effect res': info['effect res']
        })

    # check if enemies' info file exists
    if not os.path.isfile('../data/enemies.json'):
        # create if not and fill
        with open('../data/enemies.json', 'w') as f:
            json.dump(new_enemies, f)
    else:
        # read if it does
        with open('../data/enemies.json', 'r') as f:
            indexed_enemies = json.load(f)
        # update with new info
        indexed_enemies += new_enemies
        # write back into file
        with open('../data/enemies.json', 'w') as f:
            json.dump(indexed_enemies, f)

    # read enemies' index file
    with open('../data/enemies_index.json', 'r') as f:
        indexed_enemies_urls = json.load(f)
    # update with new urls
    indexed_enemies_urls += new_enemies_urls
    # write back into file
    with open('../data/enemies_index.json', 'w') as f:
        json.dump(indexed_enemies_urls, f)

    return
