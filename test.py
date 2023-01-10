from sklearn import linear_model
import pandas as pd
import numpy as np
import quandl as quandl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import mplcursors as mplcursors
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


### Import historical bitcoin price from quandl
df = quandl.get("BCHAIN/MKPRU", api_key="uDZs24A6xnhxLEtxGD61").reset_index()
df["Date"] = pd.to_datetime(df["Date"])
df.sort_values(by="Date", inplace=True)
df = df[df["Value"] > 0]


### RANSAC Regression
def LinearReg(ind, value):
    X = np.array(np.log(ind)).reshape(-1, 1)
    y = np.array(np.log(value))
    ransac = linear_model.RANSACRegressor(residual_threshold=1000000, random_state=0)    #Originally residual_threshold = 2.989
    ransac.fit(X, y)
    LinearRegRANSAC = ransac.predict(X)
    return LinearRegRANSAC

df["LinearRegRANSAC"] = LinearReg(df.index, df.Value)

#### Plot
fig = make_subplots()
fig.add_trace(go.Scatter(x=df["Date"], y=df["Value"], name="Price", line=dict(color="gold")))
fig.add_trace(go.Scatter(x=df["Date"], y=np.exp(df["LinearRegRANSAC"]), name="Ransac", line=dict(color="lightgreen")))
fig.add_trace(go.Scatter(x=df["Date"], y=16*np.exp(df["LinearRegRANSAC"]), name="Ransac*16", line=dict(color="red")))
fig.add_trace(go.Scatter(x=df["Date"], y=8*np.exp(df["LinearRegRANSAC"]), name="Ransac*8", line=dict(color="orange")))
fig.add_trace(go.Scatter(x=df["Date"], y=4*np.exp(df["LinearRegRANSAC"]), name="Ransac*4", line=dict(color="yellow")))
# fig.add_trace(go.Scatter(x=df["Date"], y=3*np.exp(df["LinearRegRANSAC"]), name="Ransac*3", line=dict(color="yellow")))
fig.add_trace(go.Scatter(x=df["Date"], y=2*np.exp(df["LinearRegRANSAC"]), name="Ransac*2", line=dict(color="green")))
fig.add_trace(go.Scatter(x=df["Date"], y=0.5*np.exp(df["LinearRegRANSAC"]), name="Ransac*0.5", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=df["Date"], y=0.25*np.exp(df["LinearRegRANSAC"]), name="Ransac*0.25", line=dict(color="darkblue")))


# ## CONTINUE WITH THIS LATER TO ANALYZE STRATEGY
# # Initialize the trading account balance and bitcoin holdings
# balance = 1000
# btc_holdings = 0
# # Iterate through the data and execute trades based on your strategy
# for index, row in df.iterrows():
#     # If the price crosses below the lower line, buy bitcoin
#     if row['Value'] < row['Price'] and balance > 0:
#         btc_to_buy = balance / row['Value']
#         btc_holdings += btc_to_buy
#         balance -= btc_to_buy * row['Value']
#     # If the price crosses above the upper line, sell bitcoin
#     elif row['Value'] > row['Price'] and btc_holdings > 0:
#         balance += btc_holdings * row['Value']
#         btc_holdings = 0

# # Print the final balance of the trading account
# print(balance)

# BTC Cycle Tops:
x = [304, 1212, 2686, 4110]
y = [np.log(35), np.log(1151), np.log(19498.68), np.log(67562.17)]

# # Plot your data
# plt.plot(x, y, 'ro',label="Original Data")

# Brute force to avoid errors
x = np.array(x, dtype=float) #transform your data in a numpy array of floats 
y = np.array(y, dtype=float) #so the curve_fit can work

# Create function to fit data, a,b,c coefficients curve_fit calculates. Must use mathematical knowledge to find
# function that ressembles data
def func(x, a, b, c): #,d):
    return a * np.log(b * x) + c

# Make the curve_fit
popt, pcov = curve_fit(func, x, y)

t_a = popt[0]
t_b = popt[1]
t_c = popt[2]     # Top

# # Print the coefficients and plot the funcion
# plt.plot(x, func(x, *popt), label="Fitted Curve") #same as line above \/
# #plt.plot(x, popt[0]*x**3 + popt[1]*x**2 + popt[2]*x + popt[3], label="Fitted Curve") 
# plt.legend(loc='upper left')
# plt.show()

# dates = ["09/06/2011", "03/12/2013", "16/12/2017", "09/11/2021"]
# z = [datetime.strptime(d, "%d/%m/%Y").date() for d in dates] 
# fig.add_trace(go.Scatter(x=z, y=np.exp(func(x, *popt)), name="Fitted Curve", line=dict(color="white")))

# BTC Bottoms:
x1 = [467, 1617, 3049, 3503, 4487]
y1 = [np.log(2.29), np.log(175.6), np.log(3242.42), np.log(4830.21), np.log(15759.61)]

# Brute force to avoid errors
x1 = np.array(x1, dtype=float) #transform your data in a numpy array of floats 
y1 = np.array(y1, dtype=float) #so the curve_fit can work

# make the curve_fit
popt, pcov = curve_fit(func, x1, y1)
b_a = popt[0]
b_b = popt[1]
b_c = popt[2]     # Bottom

# Dates for graphing purposes:
start_date = "10/08/2010"       # State initial date
start_date = datetime.strptime(start_date, "%d/%m/%Y")  # Convert string to datetime
end_date = datetime.now() + timedelta(days=1095)         # Determine end date in datetime
days_past = (end_date - start_date).days                # Count days past
days = np.arange(days_past + 1)                         # Assign index from first to last day 
date_generated = pd.date_range(start_date, periods=days[-1])    # Convert back to dates in strings

# Obtain values using logarithmic equation found for top and bottom:
y_values_t = [np.exp(t_a*np.log((days+1)*t_b)+t_c) for days in days]
y_values_b = [np.exp(b_a*np.log((days+1)*b_b)+b_c) for days in days]

y_values_t2 = [0.75*np.exp(t_a*np.log((days+1)*t_b)+t_c) for days in days]
y_values_b2 = [0.5*np.exp(b_a*np.log((days+1)*b_b)+b_c) for days in days]
y_values_b3 = [1.25*np.exp(b_a*np.log((days+1)*b_b)+b_c) for days in days]

# Figure trace addition
# Top Bands:
fig.add_trace(go.Scatter(x=date_generated, y=y_values_t, name="T", line=dict(color="red")))
fig.add_trace(go.Scatter(x=date_generated, y=y_values_t2, name="T2", line=dict(color="orange")))
# Bottom Bands:
fig.add_trace(go.Scatter(x=date_generated, y=y_values_b3, name="B3", line=dict(color="white")))
fig.add_trace(go.Scatter(x=date_generated, y=y_values_b, name="B", line=dict(color="lightgreen")))
fig.add_trace(go.Scatter(x=date_generated, y=y_values_b2, name="B2", line=dict(color="green")))

# Figure Layout
fig.update_layout(template="plotly_dark")
mplcursors.cursor(hover=True)
fig.update_xaxes(title="Date")
fig.update_yaxes(title="Price", type='log', showgrid=True)
fig.update_layout(yaxis_range=[-2,6])
fig.show()

print("Done")