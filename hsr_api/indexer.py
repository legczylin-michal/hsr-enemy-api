import json
import os
import pickle

from bs4 import BeautifulSoup

from hsr_api import constants
from hsr_api.entities import Enemy
from hsr_api.types import EnemyType, DamageType, DebuffType
from hsr_api.utils import get_all_contents, uid_from_name


def update() -> None:
	"""  """
	
	update_initial()
	update_enemies()
	update_characters()
	
	return


def update_initial() -> None:
	"""  """
	
	# if data folder does not exist
	if not os.path.exists(constants.ROOT_FOLDER_NAME):
		# create it
		os.mkdir(constants.ROOT_FOLDER_NAME)
	
	return


def update_enemies() -> None:
	"""  """
	
	# read all current enemies index (names and URLs only)
	current_enemies_names, current_enemies_urls = read_enemies_index()
	
	# if data folder for enemies does not exist
	if not os.path.exists(constants.ENEMIES_FOLDER_PATH):
		# create it
		os.mkdir(constants.ENEMIES_FOLDER_PATH)
	
	# if file containing index of enemies does not exist
	if not os.path.exists(os.path.join(constants.ENEMIES_FOLDER_PATH, constants.INDEX_NAME)):
		# create it and initiate as empty
		with open(os.path.join(constants.ENEMIES_FOLDER_PATH, constants.INDEX_NAME), 'w') as file:
			json.dump([], file)
		
		# mark all current enemies as those to be updated
		new_enemies_names = current_enemies_names
		new_enemies_urls = current_enemies_urls
	else:
		# otherwise read present enemies' index file
		with open(os.path.join(constants.ENEMIES_FOLDER_PATH, constants.INDEX_NAME), 'r') as file:
			indexed_enemies_names = json.load(file)
		
		# evaluate enemies that have not been indexed yet
		indexes = [i for i, current_enemy_name in enumerate(current_enemies_names) if
			current_enemy_name not in indexed_enemies_names]
		
		# mark those enemies as those to be updated
		new_enemies_names = [current_enemies_names[i] for i in indexes]
		new_enemies_urls = [current_enemies_urls[i] for i in indexes]
	
	# if no new enemies to be indexed were detected
	if len(new_enemies_names) == 0:
		# then exit since there is nothing to update
		return
	
	# iterate over every enemy marked for update
	for i, new_enemy_name in enumerate(new_enemies_names):
		# retrieve full information
		damage_res, debuff_res, effect_res = read_enemy_data(constants.WIKI_URL + new_enemies_urls[i])
		# and save it
		with open(os.path.join(constants.ENEMIES_FOLDER_PATH, uid_from_name(new_enemy_name) + ".pkl"), 'wb+') as file:
			pickle.dump(Enemy(new_enemy_name, new_enemies_urls[i], damage_res, debuff_res, effect_res), file)
	
	# read present index file
	with open(os.path.join(constants.ENEMIES_FOLDER_PATH, constants.INDEX_NAME), "r") as file:
		indexed_enemies_names = json.load(file)
	# add indexes of new units
	indexed_enemies_names += new_enemies_names
	# update the file
	with open(os.path.join(constants.ENEMIES_FOLDER_PATH, constants.INDEX_NAME), "w") as file:
		json.dump(indexed_enemies_names, file)
	
	return


def update_characters() -> None:
	"""  """
	
	if not os.path.exists(constants.CHARACTERS_FOLDER_PATH):
		os.mkdir(constants.CHARACTERS_FOLDER_PATH)
	
	if not os.path.exists(os.path.join(constants.CHARACTERS_FOLDER_PATH, constants.INDEX_NAME)):
		with open(os.path.join(constants.CHARACTERS_FOLDER_PATH, constants.INDEX_NAME), 'w') as file:
			json.dump([], file)
	
	return


def read_enemies_index_by_type(p_enemy_type: EnemyType) -> tuple[list[str], list[str]]:
	"""  """
	
	assert isinstance(p_enemy_type, EnemyType)
	
	names = []
	urls = []
	
	url = constants.WIKI_URL + "/wiki/Enemy"
	
	match p_enemy_type:
		case EnemyType.NORMAL:
			url += "/Normal"
		case EnemyType.ELITE:
			url += "/Elite"
		case EnemyType.BOSS:
			url += "/Boss"
		case EnemyType.ECHO_OF_WAR:
			url += "/Echo_of_War"
		case _:
			raise NotImplementedError()
	
	soup = BeautifulSoup(get_all_contents(url), "html.parser")
	res = soup.select("table.wikitable.sortable")[0]
	
	for tag in res.select("span.hidden a"):
		names.append(tag["title"])
		urls.append(tag["href"])
	
	return names, urls


def read_enemies_index() -> tuple[list[str], list[str]]:
	"""  """
	
	n_names, n_urls = read_enemies_index_by_type(EnemyType.NORMAL)
	e_names, e_urls = read_enemies_index_by_type(EnemyType.ELITE)
	b_names, b_urls = read_enemies_index_by_type(EnemyType.BOSS)
	c_names, c_urls = read_enemies_index_by_type(EnemyType.ECHO_OF_WAR)
	
	return n_names + e_names + b_names + c_names, n_urls + e_urls + b_urls + c_urls


def read_enemy_data(p_url: str) -> tuple[dict[DamageType, int], dict[DebuffType, int], int]:
	"""  """
	
	assert isinstance(p_url, str)
	
	soup = BeautifulSoup(get_all_contents(p_url), "html.parser")
	
	damage_res = {}
	tag = soup.select_one("a[title='Damage RES']")
	if not tag:
		print(f"There was an error reading damage res for > {p_url} <.")
		print("Most likely page does not contain such information.")
		print("Using None instead.")
		
		for damage_type in list(DamageType):
			damage_res[damage_type] = None
	else:
		for i, tag in enumerate(tag.find_parent("table").find_all("tr")[-1].select("td")):
			damage_res[DamageType(i)] = int(str(tag.contents[0]).strip()[:-1])
	
	debuff_res = {}
	tag = soup.select_one("a[title='Debuff RES']")
	if not tag:
		print(f"There was an error reading debuff res for > {p_url} <.")
		print("Most likely page does not contain such information.")
		print("Using None instead.")
		
		for debuff_type in list(DebuffType):
			debuff_res[debuff_type] = None
	else:
		for i, tag in enumerate(tag.find_parent("table").find_all("tr")[-1].select("td")):
			debuff_res[DebuffType(i)] = int(str(tag.contents[0]).strip()[:-1])
	
	effect_res = None
	tag = soup.select_one("a[title='Effect RES']")
	if not tag:
		print(f"There was an error reading effect res for > {p_url} <.")
		print("Most likely page does not contain such information.")
		print("Using None instead.")
		
		effect_res = None
	else:
		effect_res = int(str(tag.find_parent("table").find_all("tr")[1].select("td")[-1].contents[0]).strip()[:-1])
	
	return damage_res, debuff_res, effect_res
