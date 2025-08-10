import json
import os
import pickle
import re

from hsr_api import constants
from hsr_api.entities import Enemy
from hsr_api.exceptions import UnidentifiedDebuffTypeException
from hsr_api.types import DebuffType
from hsr_api.utils import uid_from_name


class Calculations:
	def __init__(self):
		with open(os.path.join(constants.ENEMIES_FOLDER_PATH, constants.INDEX_NAME), 'r') as file:
			self.enemies_index = json.load(file)
		
		return
	
	def search(self, p_name: str | None) -> list[Enemy]:
		"""  """
		
		assert isinstance(p_name, (str, type(None)))
		
		result: list[Enemy] = []
		
		for enemy_name in self.enemies_index:
			if p_name is None or re.search(rf"(?i)({p_name})", enemy_name):
				with open(
						os.path.join(constants.ENEMIES_FOLDER_PATH, uid_from_name(enemy_name) + ".pkl"), "rb"
				) as file:
					result.append(pickle.load(file))
		
		return result
	
	def real_chance_to_debuff(
			self,
			p_debuff_type: str | DebuffType,
			p_base_chances: (int | float | list[int | float]),
			p_ehr: (int | float | list[int | float]),
			p_name: None | str = None,
			p_level: int = 95,
			p_columns_include: None | str | list[str] = None
	) -> dict[str, object]:
		"""  """
		
		assert isinstance(p_debuff_type, (str, DebuffType))
		assert isinstance(p_base_chances, (int, float, list))
		if isinstance(p_base_chances, list):
			for item in p_base_chances:
				assert isinstance(item, (int, float))
		assert isinstance(p_ehr, (int, float, list))
		if isinstance(p_ehr, list):
			for item in p_ehr:
				assert isinstance(item, (int, float))
		assert isinstance(p_name, (type(None), str))
		assert isinstance(p_level, int)
		assert isinstance(p_columns_include, (type(None), str, list))
		if isinstance(p_columns_include, list):
			for item in p_columns_include:
				assert isinstance(item, str)
		
		if isinstance(p_base_chances, (int, float)):
			p_base_chances = [p_base_chances]
		
		if isinstance(p_ehr, (int, float)):
			p_ehr = [p_ehr]
		
		enemies: list[Enemy] = self.search(p_name)
		
		allowed_columns_names = ["base", "ehr", "debuff res", "effect res"]
		
		columns_names = ["name"]
		if isinstance(p_columns_include, type(None)):
			pass
		elif isinstance(p_columns_include, str) and p_columns_include == "*":
			for allowed_column in allowed_columns_names:
				columns_names.append(allowed_column)
		else:
			for column in p_columns_include:
				if column in allowed_columns_names:
					columns_names.append(column)
		columns_names.append("real chance")
		
		result = {}
		for column_name in columns_names:
			result[column_name] = []
		
		for enemy in enemies:
			effect_res, debuff_res = Calculations.__get_effect_debuff_res(enemy, p_level, p_debuff_type)
			
			for ehr in p_ehr:
				for chance in p_base_chances:
					result["name"].append(enemy.name)
					result["real chance"].append(
						Calculations.__real_chance_to_debuff(chance, ehr, effect_res, debuff_res)
					)
					
					if "base" in result.keys():
						result["base"].append(chance)
					
					if "ehr" in result.keys():
						result["ehr"].append(ehr)
					
					if "debuff res" in result.keys():
						result["debuff res"].append(debuff_res)
					
					if "effect res" in result.keys():
						result["effect res"].append(effect_res)
		
		return result
	
	def ehr_to_guarantee_debuff(
			self,
			p_debuff_type: str | DebuffType,
			p_base_chances: (int | float | list[int | float]),
			p_name: None | str = None,
			p_level: int = 95,
			p_columns_include: None | str | list[str] = None
	) -> dict[str, object]:
		"""  """
		
		assert isinstance(p_debuff_type, (str, DebuffType))
		assert isinstance(p_base_chances, (int, float, list))
		if isinstance(p_base_chances, list):
			for item in p_base_chances:
				assert isinstance(item, (int, float))
		assert isinstance(p_name, (type(None), str))
		assert isinstance(p_level, int)
		assert isinstance(p_columns_include, (type(None), str, list))
		if isinstance(p_columns_include, list):
			for item in p_columns_include:
				assert isinstance(item, str)
		
		if isinstance(p_base_chances, (int, float)):
			p_base_chances = [p_base_chances]
		
		enemies: list[Enemy] = self.search(p_name)
		
		allowed_columns_names = ["base", "debuff res", "effect res"]
		
		columns_names = ["name"]
		if isinstance(p_columns_include, type(None)):
			pass
		elif isinstance(p_columns_include, str) and p_columns_include == "*":
			for allowed_column in allowed_columns_names:
				columns_names.append(allowed_column)
		else:
			for column in p_columns_include:
				if column in allowed_columns_names:
					columns_names.append(column)
		columns_names.append("ehr")
		
		result = {}
		for column_name in columns_names:
			result[column_name] = []
		
		for enemy in enemies:
			effect_res, debuff_res = Calculations.__get_effect_debuff_res(enemy, p_level, p_debuff_type)
			
			for base in p_base_chances:
				result["name"].append(enemy.name)
				result["ehr"].append(Calculations.__ehr_to_guarantee_debuff(base, effect_res, debuff_res))
				
				if "base" in result.keys():
					result["base"].append(base)
				
				if "debuff res" in result.keys():
					result["debuff res"].append(debuff_res)
				
				if "effect res" in result.keys():
					result["effect res"].append(effect_res)
		
		return result
	
	@staticmethod
	def __eff_res_bonus(p_level):
		"""  """
		
		if p_level <= 50:
			return 0
		if p_level >= 75:
			return 10
		
		return (p_level - 50) * 0.4
	
	@staticmethod
	def __get_effect_debuff_res(enemy: Enemy, p_level: int, p_type) -> tuple[int, int]:
		"""  """
		
		try:
			effect_res = enemy.effect_res + Calculations.__eff_res_bonus(p_level)
			if effect_res > 100:
				effect_res = 100
			
			debuff_type_not_identified = True
			try:
				p_type = DebuffType.from_string(p_type)
				debuff_type_not_identified = False
			except UnidentifiedDebuffTypeException:
				pass
			debuff_res = 0 if debuff_type_not_identified else enemy.debuff_res[p_type]
		except TypeError:
			print(f"This > {enemy.name} < character has missing some values <")
			print("Most likely source page did not contain such information.")
			print("Using 0 instead.")
			
			effect_res = 0
			debuff_res = 0
		
		return effect_res, debuff_res
	
	@staticmethod
	def __real_chance_to_debuff(p_base_chance, p_ehr, p_eff_res, p_deb_res):
		"""  """
		
		return (p_base_chance * (100 + p_ehr) * (100 - p_eff_res) * (100 - p_deb_res)) / (100 ** 3)
	
	@staticmethod
	def __ehr_to_guarantee_debuff(p_base_chance, p_eff_res, p_def_res):
		try:
			result = (100 ** 4) / (p_base_chance * (100 - p_eff_res) * (100 - p_def_res)) - 100
		except ZeroDivisionError:
			result = float("+inf")
		
		return result
