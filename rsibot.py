KEY = "H3PUK0L7U3UGOHGD"

import requests
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

# Function to fetch historical data for a stock
def get_historical_data(stock_symbol):
    # Enter your AlphaVantage API key here
    api_key = KEY

    # AlphaVantage API endpoint for getting weekly stock prices
    endpoint = "https://www.alphavantage.co/query"
    # Parameters for the API request
    params = {
        "function": "TIME_SERIES_WEEKLY_ADJUSTED",
        "symbol": stock_symbol,
        "apikey": api_key,
    }
    try:
        # Send the GET request to the AlphaVantage API
        response = requests.get(endpoint, params=params)
        data = response.json()
        # Parse the response to extract the historical data
        time_series = data["Weekly Adjusted Time Series"]
        # Lists to store the time (x-axis) and price (y-axis) data
        time = []
        price = []
        # Calculate the date one year ago from today
        one_year_ago = datetime.now() - timedelta(days=3650)
        # Iterate over the time series data and append the values to the lists
        for date, values in time_series.items():
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            # Only append data if it falls within the last year
            if date_obj >= one_year_ago:
                time.append(date)
                price.append(float(values["4. close"]))
                
        time.reverse()
        price.reverse()
        return time, price
    except requests.exceptions.RequestException as e:
        print("Error occurred while fetching data:", e)
#Calculate Rsi
def calculate_rsi(price,n=14):
    df = pd.DataFrame(price)
    delta = df.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ema_up = up.ewm(com=n - 1, min_periods=n).mean()
    ema_down = down.ewm(com=n - 1, min_periods=n).mean()
    rs = ema_up / ema_down
    rsi = 100 - (100 / (1 + rs))
    return rsi.to_numpy()


def makeFakePurchases(time, price, rsi, rsiHigh, rsiLow, purchaseAmt, sellAmt):
        # Simulate purchases
    initial_balance = 10000  # Initial account balance
    balance = initial_balance  # Current account balance
    shares = 0  # Number of shares held
    transaction_history = []  # List to store transaction history

    for i in range(1, len(time)):
        if rsi[i] < rsiLow:  # Buy signal (RSI is below 30)
            if balance > 0:
                # Calculate the amount to purchase based on the available balance
                stockprice = price[i]
                max_shares = int(balance / stockprice)
                if (max_shares > 4):
                    purchase_shares = int(max_shares * purchaseAmt)
                    purchase_amount = purchase_shares * stockprice

                    # Update balance and shares
                    balance -= purchase_amount
                    shares += purchase_shares

                    # Add transaction to the history
                    transaction = {'Date': time[i], 'Type': 'Buy', 'Shares': purchase_shares, 'Price': stockprice, 'balance':balance}
                    transaction_history.append(transaction)
                

        elif rsi[i] > rsiHigh:  # Sell signal (RSI is above 70)
            if shares > 0:
                # Calculate the amount to sell based on the available shares
                stockprice = price[i]
                sell_shares = int(shares * sellAmt)
                if (sell_shares > 0):
                    sell_amount = sell_shares * stockprice

                    # Update balance and shares
                    balance += sell_amount
                    shares -= sell_shares

                    # Add transaction to the history
                    transaction = {'Date': time[i], 'Type': 'Sell', 'Shares': sell_shares, 'Price': stockprice,'balance':balance}
                    transaction_history.append(transaction)
        if i == len(time) - 1:
            #sell everything
            if (shares > 0):
                stockprice = price[i]
                sell_shares = shares
                sell_amount = sell_shares * stockprice

                # Update balance and shares
                balance += sell_amount
                shares -= sell_shares

                # Add transaction to the history
                transaction = {'Date': time[i], 'Type': 'Sell', 'Shares': sell_shares, 'Price': stockprice, 'balance':balance}
                transaction_history.append(transaction)
    plotTransactions(transaction_history, initial_balance, time, price)
    if (len(transaction_history) > 0):
        return transaction_history[-1]['balance']
    else:
        return 0

def plotTransactions(transaction_history, initial_balance, time, price):


    # Prepare data for plotting
    balance_over_time = [initial_balance]
    dates = [time[0]]

    for transaction in transaction_history:
        dates.append(transaction['Date'])
        if (transaction['Type'] == 'Buy'):
            balance_over_time.append(balance_over_time[-1] - transaction['Shares'] * transaction['Price'])
        else:
            balance_over_time.append(balance_over_time[-1] + transaction['Shares'] * transaction['Price'])
        print(transaction)

    # Plot balance over time
    fig1 = plt.figure(figsize=(8, 6))
    plt.plot(dates, balance_over_time)
    plt.title('Account Balance Over Time')
    plt.xlabel('Date')
    plt.ylabel('Balance')
    plt.xticks(rotation=45)
    plt.grid(True)
    # Plot transaction markers
    for transaction in transaction_history:
        if transaction['Type'] == 'Buy':
            marker = 'o'
            color = 'green'
        else:
            marker = 'o'
            color = 'red'
        plt.scatter(transaction['Date'], balance_over_time[dates.index(transaction['Date'])], marker=marker, color=color)
    #plot stock price to compare
    fig2 = plt.figure(figsize=(8, 6))
    plt.plot(time, price, label="Price")
    plt.title('Stock Price over Time')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.xticks(rotation=45)

    plt.show()

def findBestRSI():
    bestLow = -1
    bestHigh = -1
    bestPurchasePercentage = 0
    bestSellPercentage = 0
    bestProfit = 0
    testPercentageRange = 1
    for i in range(100):
        for j in range(100):
             for a in range(testPercentageRange):
                 for b in range(testPercentageRange):
                    testProfit = makeFakePurchases(timeframe, stockprice, rsi,i,j,float((a+1)/testPercentageRange),float((b+1)/testPercentageRange))
                    if (testProfit > bestProfit):
                        bestLow = i
                        bestHigh = j
                        bestPurchasePercentage = float((a+1)/testPercentageRange)
                        bestSellPercentage = float((b+1)/testPercentageRange)
                        bestProfit = testProfit
    print(bestLow, bestHigh, bestPurchasePercentage, bestSellPercentage,bestProfit)

# Main program
if __name__ == "__main__":
    stock_symbol = input("Enter the stock symbol: ")
    timeframe, stockprice = get_historical_data(stock_symbol)
    rsi = calculate_rsi(stockprice)
    #findBestRSI()
    #print(rsi)
    print(makeFakePurchases(timeframe, stockprice, rsi,76,51,1,1))



# Plotting the stock prices
    """ fig, axs = plt.subplots(2,2, figsize = (10, 8))
    axs[0,0].plot(dates, prices, label='Stock Prices')

    # Plotting the MACD lines
    axs[1,0].plot(dates, macd_line, label='MACD Line')
    axs[1,0].plot(dates, macd_signal_line, label='Signal Line')

    # Plotting the MACD histogram
    axs[1,0].bar(dates, macd_histogram, label='MACD Histogram')

    axs[1,0].set_xlabel('Date')
    axs[1,0].set_ylabel('Price')
    axs[1,0].set_title('Stock Price with MACD')
    axs[1,0].legend()
    plt.show() """
    
    
