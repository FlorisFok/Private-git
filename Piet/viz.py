import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import matplotlib.pyplot as plt
import sys

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']   
         
creds = ServiceAccountCredentials.from_json_keyfile_name(
            r"C:\Users\s147057\Documents\CS50\Database-6141813cd99e.json", scope)

client = gspread.authorize(creds)


ts = time.localtime()
now = f"{ts.tm_year}{ts.tm_mon}{ts.tm_mday}_{ts.tm_hour}:{ts.tm_min}"

sheet  = client.open('Test').sheet1

for item in sys.argv[1:]:
	cell = sheet.find(item)
	col_start = cell.col - 1

	TIME_COL = col_start
	NAME_COL = col_start + 1
	COUNT_COL = col_start + 2

	time_list = sheet.col_values(TIME_COL)
	name = sheet.col_values(NAME_COL)[0]
	count_list = sheet.col_values(COUNT_COL)

	f_time = time_list[0]

	time_num = []
	first = True
	for t in time_list:
		T = t.split('.')
		T = [int(i) for i in T]

		num = T[-2]*60+T[-1]

		if first:
			first_num = num
			time_num.append(0)
			first = False
		else:
			time_num.append(num-first_num)
	print(name)

	plt.scatter(time_num, count_list)
	plt.title(name)
	plt.xlabel(f'min, 0 = {f_time}')
	plt.ylabel('voorraad')
	plt.ylim(plt.ylim()[::-1])
plt.show()


