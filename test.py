from sklearn import linear_model
import pandas as pd
import numpy as np
import quandl as quandl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import mplcursors as mplcursors



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
fig.update_layout(template="plotly_dark")
mplcursors.cursor(hover=True)
fig.update_xaxes(title="Date")
fig.update_yaxes(title="Price", type='log', showgrid=True)
fig.show()


# ## efgrthyjukihjgfsedwaefsgdhfgjyhklñhjgfdsdawsfgdhfjkl,hgfdsaersdtyhfjugknhfbcdawefrgtyhjuk
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