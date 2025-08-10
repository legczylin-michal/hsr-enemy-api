from dataclasses import dataclass

from hsr_api.types import DamageType, DebuffType


@dataclass
class Enemy:
	name: str
	url: str
	damage_res: dict[DamageType, int]
	debuff_res: dict[DebuffType, int]
	effect_res: int
