import pandas as pd

from hsr_api import indexer
from hsr_api.calculations import Calculations


def main():
	indexer.update()
	
	calc = Calculations()
	
	## Kafka
	# perform calculations. Every debuff Kafka applies has 100% base chance
	result = calc.ehr_to_guarantee_debuff("shock", 100, p_columns_include="*")
	# convert into pandas data frame
	df = pd.DataFrame.from_dict(result)
	# remove entries where you need infinite amount of EHR (due to 100% resistance)
	df = df[df["ehr"] != float("+inf")].reset_index(drop=True)
	# EHR to debuff almost every enemy in game
	print(df["ehr"].max())
	# output > 100.0
	
	# Conclusion: Kafka wants 100% EHR. As easy as that
	
	## Black Swan
	# perform calculations. Black Swan's normal attack has 65% chance to apply stack of Arcana, whereas skill has 100%
	result = calc.ehr_to_guarantee_debuff("arcana", [65, 100], p_columns_include="*")
	# convert into pandas data frame
	df = pd.DataFrame.from_dict(result)
	# remove entries where you need infinite amount of EHR (due to 100% resistance)
	df = df[df["ehr"] != float("+inf")].reset_index(drop=True)
	# EHR to debuff almost every enemy in game
	print(df.groupby("base")["ehr"].max())
	# output > 65     207.692308
	# 		 > 100    100.000000
	# ~208% EHR is "quite" a lot, let's investigate who does belong this amount to.
	print(df.loc[df["base"] == 65].sort_values(by="ehr"))
	# output >                   "Speartip"    65  ...          40  156.410256
	# 		 > Swarm: True Sting (Complete)    65  ...          50  207.692308
	# so actually it is only one enemy in entire game! Let's see how probable is to inflict Arcana with normal attack
	# if Black Swan has 156.410256% EHR
	# perform calculations
	result = calc.real_chance_to_debuff("arcana", 65, 156.410256, "Swarm: True Sting (Complete)")
	# convert into pandas data frame
	df = pd.DataFrame.from_dict(result)
	# real chance to debuff Swarm: True Sting (Complete) with normal attack while having ~156% EHR.
	print(df)
	# output > Swarm: True Sting (Complete)    83.333333
	# which isn't that bad at all! 156% EHR is a good amount to have, though you'll definitely lose on some ATK.
	# What if you aim at skill only, so you want to have ony 100% EHR?
	# perform calculations
	result = calc.real_chance_to_debuff("arcana", 65, 100, p_columns_include="*")
	# convert into pandas data frame
	df = pd.DataFrame.from_dict(result)
	# remove entries where chance to debuff is 0 but only due to 100% effect resistance
	df = df[df["effect res"] != 100].sort_values(by="real chance").reset_index(drop=True)
	# print result
	print(df)
	# output >                   Swarm: True Sting (Complete)  ...         65.0
	# 		 >                     Hellcharred Shadow General  ...         78.0
	# 		 >            Sublime, Radiant, Avatar of the Sky  ...         78.0
	# 		 >                First Genius, Entelechy, Zandar  ...         78.0
	# 		 > Starcrusher Swarm King: Skaracabaz (Synthetic)  ...         78.0
	# again, that's not really bad for normal attack, considering we are interested to consistently apply Arcana with skill
	
	# Conclusion: for Black Swan one wants either 156% EHR to guarantee inflicting Arcana with both normal attack and skill
	# on "all enemies" in game or just 100% to be sure it applies on every enemy with skill
	
	## Hysilens
	# There are no calculations needed really. Every debuff she applies is unique (so only affected by enemy's effect resistance)
	# and has 100% base chance application. So real chance to inflict will calculate exactly like Black Swan's Arcana
	# application with skill => 100% EHR. As easy as that
	
	return


if __name__ == "__main__":
	main()
