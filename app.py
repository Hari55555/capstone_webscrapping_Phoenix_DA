from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data/usd?start_date=2020-01-01&end_date=2021-06-30')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('tbody')
rows = table.find_all('tr')
row_length = len(rows)


temp = [] #initiating a list 

for row in rows:
    cols = row.find_all(['td','th'])
    cols = [ele.text.strip() for ele in cols]
    temp.append([ele for ele in cols if ele])

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('Date','Market_Cap','Volume', 'Open', 'Close' ))

#insert data wrangling here
pd.options.display.float_format = '{:.2f}'.format
df['Date'] = df['Date'].astype('datetime64')
df['Market_Cap'] = df['Market_Cap'].replace({'\$': '', ',': ''}, regex=True)
df['Market_Cap'] = df['Market_Cap'].astype('int64')
df['Volume'] = df['Volume'].replace({'\$': '', ',': ''}, regex=True)
df['Volume'] = df['Volume'].astype('int64')
df['Open'] = df['Open'].replace({'\$': '', ',': ''}, regex=True)
df['Open'] = df['Open'].astype('float64')
df['Close'] = df['Close'].replace({'\$': '','N/A': '2279.35', ',': ''}, regex=True)
df['Close'] = df['Close'].astype('float64')

class _IntArrayFormatter(pd.io.formats.format.GenericArrayFormatter):

    def _format_strings(self):
        formatter = self.formatter or (lambda x: ' {:,}'.format(x))
        fmt_values = [formatter(x) for x in self.values]
        return fmt_values

pd.io.formats.format.IntArrayFormatter = _IntArrayFormatter

df = df.set_index('Date')
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Volume"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df["Volume"].plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)