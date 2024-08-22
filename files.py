import pandas as pd

data = pd.read_excel("file_example_XLSX_50.xlsx")
result = data.to_string()
print(result)