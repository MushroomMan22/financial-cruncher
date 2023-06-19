import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from config import *

def get_historical_data(stock_symbol):
    # Fetch the historical data using yfinance
    stock_data = yf.download(stock_symbol, start=datetime.now()-timedelta(days=TIME), end=datetime.now())

    # Extract the adjusted close prices and corresponding dates
    prices = stock_data['Adj Close']
    dates = stock_data.index.strftime('%Y-%m-%d')
    return dates, prices  

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

def plotStockData(dates, prices):
    plt.plot(dates, prices)
    plt.xlabel("Time")
    plt.ylabel("Adjusted Close Price")
    plt.title(f"{stock_symbol} Weekly Adjusted Close Prices")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def makeFakeRSIPurchases(time, price, rsi, rsiLow, rsiHigh, purchaseAmt, sellAmt, graph):
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
    if (graph == True):
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

def findBestRSI(time, price,rsi):
    bestLow = -1
    bestHigh = -1
    bestProfit = 0
    for l in range(100):
        for h in range(100):
            testProfit = makeFakeRSIPurchases(time, price, rsi,l,h,1,1,False)
            if (testProfit > bestProfit):
                bestHigh = h
                bestLow = l
                bestProfit = testProfit
    return bestHigh, bestLow

def calculate_macd(dates, prices, fast_period=12, slow_period=26, signal_period=9):
    # Calculate the MACD line
    ema_fast = pd.Series(prices, index=dates).ewm(span=fast_period, min_periods=fast_period).mean()
    ema_slow = pd.Series(prices, index=dates).ewm(span=slow_period, min_periods=slow_period).mean()
    macd_line = (ema_fast - ema_slow)

    # Calculate the MACD signal line
    macd_signal_line = macd_line.ewm(span=signal_period, min_periods=signal_period).mean()

    # Calculate the MACD histogram
    macd_histogram = macd_line - macd_signal_line
    return macd_line, macd_signal_line

def calculate_bollinger_bands(dates,prices, window=20, num_std=2):
    rolling_mean = pd.Series(prices,index=dates).rolling(window=window).mean()
    rolling_std = pd.Series(prices,index=dates).rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return rolling_mean, upper_band, lower_band
def graphboilerBands(dates, prices):
    rolling_mean, upper_band, lower_band = calculate_bollinger_bands(dates,prices)
    # Plotting the stock prices
    plt.plot(dates,prices, label='Stock Prices')

    # Plotting the Bollinger Bands
    #plt.plot(dates, prices)
    plt.plot(rolling_mean, label='Rolling Mean')
    plt.plot(upper_band, label='Upper Band', color = 'g')
    plt.plot(lower_band, label='Lower Band', color = 'r')

    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Stock Price with Bollinger Bands')
    plt.legend()
    plt.show()
def Strategy(dates, prices, rsiLow, rsiHigh):
    rsi = calculate_rsi(prices)
    macd, signal = calculate_macd(dates,prices)
    #rolling_mean, upper_band, lower_band = calculate_bollinger_bands()
    buyPoint = False
    sellPoint = False
    LookforBuy = True
    allbuyPoints = []
    allsellPoints = []
    buys = []
    sells = []

    for index, value in enumerate(dates):
        #oversold conditions
        if (rsi[index] < rsiLow):
            if (macd[dates[index]] > signal[dates[index]]):
                allbuyPoints.append(index)
                if (LookforBuy):
                    buys.append(index)
                    LookforBuy = False
        #overbought conditions
        if (rsi[index] > rsiHigh):
            if (macd[dates[index]] < signal[dates[index]]):
                allsellPoints.append(index)
                if not LookforBuy:
                    sells.append(index)
                    LookforBuy = True
        #last day condition
        if (index == len(dates) - 1):
            sells.append(index)
    #checking for positive buys
    positiveBuys = 0
    for index,value in enumerate(buys):
        if (prices[buys[index]] < prices[sells[index]]):
            positiveBuys += 1
    if (len(buys) > 0):
        print("Percentage:" + str(positiveBuys / len(buys)))
    #purchasing
    makePurchases(dates, prices, buys, sells, True)
    #plotting
    plt.plot(dates, prices)
    for value in allbuyPoints:
        #plt.scatter(dates[value], prices[value],color = 'green')
        pass
    for value in allsellPoints:
        #plt.scatter(dates[value], prices[value], color = 'red')
        pass
    for value in buys:
        plt.scatter(dates[value], prices[value],color = 'lime')
    for value in sells:
        plt.scatter(dates[value], prices[value], color = 'orange')
    plt.show()
    #MACD Crossover
        #consider when the macd line crosses above the signal line bullish
        #consider when the macd line crosses below the signal line bearish
    #Volatility Squeeze
        #when the volatility reaches a 6th month low and 6th month minimum distance apart
    #Mean Reversion
        #when the price touches the upper band it will normally go back to the middle
        #when the price touches the lower band it will normally go back towards the top
def makeMacdPurchases(dates, prices, macd,signal, graph):
    initial_balance = 10000  # Initial account balance
    balance = initial_balance  # Current account balance
    shares = 0  # Number of shares held
    transaction_history = []  # List to store transaction history

    for i in range(1, len(dates)):
        if (macd[i-1] < signal[i-1]) and (macd[i] > signal[i]):  # Buy signal (MACD crosses over signal)
            if balance > 0:
                # Calculate the amount to purchase based on the available balance
                stockprice = prices[i]
                max_shares = int(balance / stockprice)
                if (max_shares > 4):
                    purchase_shares = int(max_shares)
                    purchase_amount = purchase_shares * stockprice

                    # Update balance and shares
                    balance -= purchase_amount
                    shares += purchase_shares

                    # Add transaction to the history
                    transaction = {'Date': dates[i], 'Type': 'Buy', 'Shares': purchase_shares, 'Price': stockprice, 'balance':balance}
                    transaction_history.append(transaction)
                
        elif (macd[i-1] > signal[i-1]) and (macd[i] < signal[i]):  # Sell signal (MACD crosses below signal)
            if shares > 0:
                # Calculate the amount to sell based on the available shares
                stockprice = prices[i]
                sell_shares = int(shares)
                if (sell_shares > 0):
                    sell_amount = sell_shares * stockprice
                    # Update balance and shares
                    balance += sell_amount
                    shares -= sell_shares
                    # Add transaction to the history
                    transaction = {'Date': dates[i], 'Type': 'Sell', 'Shares': sell_shares, 'Price': stockprice,'balance':balance}
                    transaction_history.append(transaction)
        if i == len(dates) - 1:
            #sell everything
            if (shares > 0):
                stockprice = prices[i]
                sell_shares = shares
                sell_amount = sell_shares * stockprice

                # Update balance and shares
                balance += sell_amount
                shares -= sell_shares

                # Add transaction to the history
                transaction = {'Date': dates[i], 'Type': 'Sell', 'Shares': sell_shares, 'Price': stockprice, 'balance':balance}
                transaction_history.append(transaction)
    if (graph == True):
        plotTransactions(transaction_history, initial_balance, dates, prices)
        plt.plot(macd,label="MACD")
        plt.plot(signal,label="Signal")
        plt.legend()
        plt.show()
    if (len(transaction_history) > 0):
        return transaction_history[-1]['balance']
    else:
        return 0
def findBestMacdPeriods(dates,prices):
    bestProfit = 0
    bestFast = -1
    bestSlow = -1
    bestSignal = -1
    for fastIndex in range(1,20):
        for slowIndex in range(10,40):
            for signalIndex in range(1,20):
                macd, signal = calculate_macd(dates,prices,fastIndex,slowIndex,signalIndex)
                testProfit = makeMacdPurchases(dates,prices,macd,signal,False)
                #print("Proft:" + str(testProfit),fastIndex,slowIndex,signalIndex)
                if (testProfit > bestProfit):
                    bestFast = fastIndex
                    bestSignal = signalIndex
                    bestSlow = slowIndex
                    bestProfit = testProfit
    macd, signal = calculate_macd(dates,prices,bestFast,bestSlow,bestSignal)
    print(bestFast,bestSlow,bestSignal)
    return macd,signal
def makePurchases(dates, prices,buyList,sellList, graph):
    initial_balance = 10000  # Initial account balance
    balance = initial_balance  # Current account balance
    shares = 0  # Number of shares held
    transaction_history = []  # List to store transaction history
    for i in range(0, len(dates)):
        if i in buyList:  # Buy signal (RSI is below 30)
            if balance > 0:
                # Calculate the amount to purchase based on the available balance
                stockprice = prices[i]
                max_shares = int(balance / stockprice)
                if (max_shares > 4):
                    purchase_shares = int(max_shares)
                    purchase_amount = purchase_shares * stockprice

                    # Update balance and shares
                    balance -= purchase_amount
                    shares += purchase_shares

                    # Add transaction to the history
                    transaction = {'Date': dates[i], 'Type': 'Buy', 'Shares': purchase_shares, 'Price': stockprice, 'balance':balance}
                    transaction_history.append(transaction)
                

        elif i in sellList:  # Sell signal (RSI is above 70)
            if shares > 0:
                # Calculate the amount to sell based on the available shares
                stockprice = prices[i]
                sell_shares = int(shares)
                if (sell_shares > 0):
                    sell_amount = sell_shares * stockprice

                    # Update balance and shares
                    balance += sell_amount
                    shares -= sell_shares

                    # Add transaction to the history
                    transaction = {'Date': dates[i], 'Type': 'Sell', 'Shares': sell_shares, 'Price': stockprice,'balance':balance}
                    transaction_history.append(transaction)
        if i == len(dates) - 1:
            #sell everything
            if (shares > 0):
                stockprice = prices[i]
                sell_shares = shares
                sell_amount = sell_shares * stockprice

                # Update balance and shares
                balance += sell_amount
                shares -= sell_shares

                # Add transaction to the history
                transaction = {'Date': dates[i], 'Type': 'Sell', 'Shares': sell_shares, 'Price': stockprice, 'balance':balance}
                transaction_history.append(transaction)
    if (graph == True):
        plotTransactions(transaction_history, initial_balance, dates, prices)
    if (len(transaction_history) > 0):
        return transaction_history[-1]['balance']
    else:
        return 0
def graphAllTechnicalIndicators(dates, prices):
    #graph price,rsi, macd
    #graph green and red dots for buy and sell points
     #plot ax1
     # Create the figure and axes
    rsi = calculate_rsi(prices)
    bestHigh, bestLow = findBestRSI(dates,prices, rsi)
    macd,signal = calculate_macd(dates,prices)
    halfbuyPoints = []
    halfsellPoints = []
    allbuyPoints = []
    allsellPoints = []
    for index in range(0,len(dates)):
        if (rsi[index] < bestLow) ^ (macd[dates[index]] > signal[dates[index]]):
            halfbuyPoints.append(index) 
        else:
            allbuyPoints.append(index)
        #overbought conditions
        if (rsi[index] > bestHigh) ^ (macd[dates[index]] < signal[dates[index]]):
            halfsellPoints.append(index)    
        else:
            allsellPoints.append(index)
     #graphs
     #PRICE
    fig, axs  = plt.subplots(2, 2, figsize=(10, 8))
    axs[0,0].plot(dates, prices, label="Close")
    axs[0,0].set_title(f"{stock_symbol} Stock Price")
    axs[0,0].legend()

    # Plot RSI
    axs[0,1].plot(dates, rsi, label="RSI")
    axs[0,1].hlines(bestLow, 0, len(dates), linestyles='dotted')
    axs[0,1].hlines(bestHigh, 0, len(dates), linestyles='dotted')
    axs[0,1].legend()

    #PLOT MACD
    axs[1,0].plot(dates,macd, label="MACD")
    axs[1,0].plot(dates,signal, label="Signal")
    for index in range(1,len(dates)):
        print(macd[index], signal[index])
        if ((macd[index - 1] < signal[index - 1] and macd[index] > signal[index]) or (macd[index - 1] > signal[index - 1] and macd[index] < signal[index])):
            axs[1,0].scatter(dates[index], macd[index], marker='o', color='orange')
    axs[1,0].legend()
    #plot indicators
    axs[1,1].plot(dates, prices, label="Close")
    for value in allbuyPoints:
        axs[1,1].scatter(dates[value], prices[value], marker='o', color='green')
    for value in allsellPoints:
        axs[1,1].scatter(dates[value], prices[value], marker='o', color='red')
    for value in halfbuyPoints:
        axs[1,1].scatter(dates[value], prices[value], marker='o', color='lime')
    for value in halfsellPoints:
        axs[1,1].scatter(dates[value], prices[value], marker='o', color='orange')
    plt.show()

if __name__ == "__main__":
    stock_symbol = input("Enter the stock symbol: ")
    dates, prices = get_historical_data(stock_symbol)
    bestHigh, bestLow = findBestRSI(dates,prices, calculate_rsi(prices))
    #print(makeFakeRSIPurchases(dates,prices,calculate_rsi(prices), bestLow,bestHigh, 1,1,True))
    Strategy(dates, prices,bestLow, bestHigh)
    #rsi = calculate_rsi(prices)
    #graphAllTechnicalIndicators(dates,prices)
