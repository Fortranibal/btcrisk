import csv
import datetime
import quandl

import requests


file = open("BTC-MKPRU.csv", 'a', newline = '')

# import quandl
# quandl.ApiConfig.api_key = "uDZs24A6xnhxLEtxGD61"

# # # Your CoinDesk API key
# # api_key = "YOUR_API_KEY_HERE"

# # Open the CSV file for reading
# with open("BTC-MKPRU.csv", "r") as f:
#   # Create a CSV reader
#   reader = csv.reader(f)

#   # Skip the header row
#   next(reader)

# #   data = nasdaqdatalink.get("FRED/GDP", start_date="2001-12-31", end_date="2005-12-31")
# # curl "https://data.nasdaq.com/api/v3/datasets/FRED/GDP.csv?collapse=annual&rows=6&order=asc&column_index=1&api_key=YOURAPIKEY"
# # "https://data.nasdaq.com/data/BCHAIN/MKPRU-bitcoin-market-price-usd"

#   # Get the latest date from the CSV file
#   latest_date = None
#   for row in reader:
#     latest_date = row[-1]

# # If there is no latest date, set the start date to 2010-07-17
# if latest_date is None:
#   start_date = "2010-07-17"
# else:
#   # Convert the latest date to a datetime object
#   latest_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d")

#   # Set the start date to the day after the latest date
#   start_date = (latest_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

# # Set the end date to today
# end_date = datetime.datetime.now().strftime("%Y-%m-%d")

# # # The URL for the CoinDesk API
# url = f"https://api.coindesk.com/v1/bpi/historical/close.csv?start={start_date}&end={end_date}&api_key={api_key}"

# # Send a request to the CoinDesk API
# response = requests.get(url)

# # Read the CSV data from the response
# csv_data = response.text

# # Open the CSV file for writing
# with open("bitcoin_prices.csv", "a", newline="") as f:
#   # Create a CSV writer
#   writer = csv.writer(f)

#   # Iterate through the rows in the CSV data
#   for row in csv.reader(csv_data.splitlines()):
#     # Write the row to the CSV file
#     writer.writerow(row)

# print("Done!")

# Obtain latest date curently available in CSV - start_date
with open('BTC-MKPRU.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    last_row = None         # Get the last row in the CSV file
    for row in reader:
        last_row = row
    # The first element in the last row is the date
    start_date1 = last_row[0]
    date1 = datetime.datetime.strptime(start_date1, '%Y-%m-%d')
    start_date = date1 + datetime.timedelta(days=1)

# Set the end date to today
end_date = datetime.datetime.now().strftime("%Y-%m-%d")

# Fetch the data from Quandl
data = quandl.get('BCHAIN/MKPRU', start_date=start_date, end_date=end_date)

# Append the new data to the CSV file
with open('BTC-MKPRU.csv', 'a', newline='') as csv_file:
    writer = csv.writer(csv_file)
    for index, row in data.iterrows():
        writer.writerow([index, row['Value']])

# data_to_append = []

# file = open("BTC-MKPRU.csv", 'a', newline = '')
# writer = csv.writer(file)

# writer.writerows(data_to_append)
