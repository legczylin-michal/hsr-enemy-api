from enum import Enum

from hsr_api.exceptions import UnidentifiedDebuffTypeException


class AutoEnum(Enum):
	def __new__(cls):
		value = len(cls.__members__)
		obj = object.__new__(cls)
		obj._value_ = value
		return obj


class EnemyType(AutoEnum):
	NORMAL = ()
	ELITE = ()
	BOSS = ()
	ECHO_OF_WAR = ()


class DamageType(AutoEnum):
	PHYSICAL = ()
	FIRE = ()
	ICE = ()
	LIGHTNING = ()
	WIND = ()
	QUANTUM = ()
	IMAGINARY = ()


class DebuffType(AutoEnum):
	BLEED = ()
	BURN = ()
	FROZEN = ()
	SHOCK = ()
	WIND_SHEER = ()
	ENTANGLEMENT = ()
	IMPRISONMENT = ()
	CONTROL_EFFECTS = ()
	
	@staticmethod
	def from_string(s):
		match s:
			case "bleed":
				return DebuffType.BLEED
			case "burn":
				return DebuffType.BURN
			case "frozen":
				return DebuffType.FROZEN
			case "shock":
				return DebuffType.SHOCK
			case "wind sheer":
				return DebuffType.WIND_SHEER
			case "entanglement":
				return DebuffType.ENTANGLEMENT
			case "imprisonment":
				return DebuffType.IMPRISONMENT
			case "control effects":
				return DebuffType.CONTROL_EFFECTS
			case _:
				raise UnidentifiedDebuffTypeException(f"Unknown debuff: {s}")
