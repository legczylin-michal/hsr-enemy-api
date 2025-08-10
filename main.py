import pandas as pd

from hsr_api import indexer
from hsr_api.calculations import Calculations


def main():
	indexer.update()
	
	calc = Calculations()
	result = calc.ehr_to_guarantee_debuff("arcana", [65, 100], p_columns_include="*")
	
	df = pd.DataFrame.from_dict(result)
	
	df = df[df["effect res"] != 100]
	
	print(df.loc[df["base"] == 65, "ehr"].max())
	
	print(df.loc[df["base"] == 100, "ehr"].max())
	
	return


if __name__ == "__main__":
	main()
