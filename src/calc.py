import json
import re

import config

with open('../data/enemies.json', 'r') as f:
    data = json.load(f)


class HSR:
    @staticmethod
    def __chance(base, ehr, eff_res, deb_res=0):
        return base * (100 + ehr) / 100 * (100 - eff_res) / 100 * (100 - deb_res) / 100

    @staticmethod
    def __guarantee(base, eff_res, deb_res=0):
        try:
            result = 100 * 100 / (base * (100 - eff_res) / 100 * (100 - deb_res) / 100) - 100
        except ZeroDivisionError:
            result = float('+inf')

        return result

    @staticmethod
    def search(name):
        result = []

        for enemy in data:
            if re.search(rf'(?i)({name})', enemy['name']):
                result.append(enemy)

        return result

    @staticmethod
    def __eff_res_bonus(level):
        if level < 50:
            return 0
        elif level > 75:
            return 10
        else:
            return (level - 50) * 0.4

    @staticmethod
    def debuff_chance(p_base, p_ehr, p_type, p_name, p_level):
        """ calculate real chance to debuff character """

        enemies = HSR.search(p_name)

        if isinstance(p_base, (int, float)):
            p_base = [p_base]

        if isinstance(p_ehr, (int, float)):
            p_ehr = [p_ehr]

        result = {}

        for enemy in enemies:
            effect_res = enemy['effect res'] + HSR.__eff_res_bonus(p_level)
            if effect_res > 100:
                effect_res = 100
            debuff_res = 0 if p_type not in config.DEBUFF_DICT.values() else enemy['debuff res'][p_type]

            result[enemy['name']] = {f'base={base} ehr={ehr}': HSR.__chance(base, ehr, effect_res, debuff_res) for base in p_base for ehr in p_ehr}

        return result

    @staticmethod
    def debuff_guarantee(p_base, p_type, p_name, p_level):
        """ minimal EHR to 100% debuff character """

        enemies = HSR.search(p_name)

        if isinstance(p_base, (int, float)):
            p_base = [p_base]

        result = {}

        for enemy in enemies:
            effect_res = enemy['effect res'] + HSR.__eff_res_bonus(p_level)
            if effect_res > 100:
                effect_res = 100
            debuff_res = 0 if p_type not in config.DEBUFF_DICT.values() else enemy['debuff res'][p_type]

            result[enemy['name']] = {f'base={base}': HSR.__guarantee(base, effect_res, debuff_res) for base in p_base}

        return result
