import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

class Model:
    def __init__(self, controller):
        # Class to hold data manipulation functions
        self.c = controller


    def get_historical_data(self, stock_symbol, time):
        # Fetch the historical data using yfinance
        try:
            stock_data = yf.download(stock_symbol, start=datetime.now()-timedelta(days=time), end=datetime.now())
            # Extract the adjusted close prices and corresponding dates
            prices = stock_data['Adj Close']
            dates = stock_data.index.strftime('%Y-%m-%d')
            return dates, prices  
        except Exception as e:
            print(e)
            raise e
    
    def calculate_rsi(self, price,n=14):
        try:
            df = pd.DataFrame(price)
            delta = df.diff()
            up = delta.clip(lower=0)
            down = -delta.clip(upper=0)
            ema_up = up.ewm(com=n - 1, min_periods=n).mean()
            ema_down = down.ewm(com=n - 1, min_periods=n).mean()
            rs = ema_up / ema_down
            rsi = 100 - (100 / (1 + rs))
            return rsi.to_numpy()
        except Exception as e:
            print(e)
            raise e
    
    def findBestRSI(self, time, prices):
        try:
            rsi = self.calculate_rsi(prices)
            bestLow = -1
            bestHigh = -1 
            bestProfit = 0
            for l in range(100):
                for h in range(100):
                    testProfit = self.makeFakeRSIPurchases(time, prices, rsi,l,h,1,1,False)
                    if (testProfit > bestProfit):
                        bestHigh = h
                        bestLow = l
                        bestProfit = testProfit
            return bestHigh, bestLow
        except Exception as e:
            print(e)
            raise e

    def makeFakeRSIPurchases(self, time, price, rsi, rsiLow, rsiHigh, purchaseAmt, sellAmt, graph):
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
            self.plotTransactions(transaction_history, initial_balance, time, price)
        if (len(transaction_history) > 0):
            return transaction_history[-1]['balance']
        else:
            return 0
        
    # def plotTransactions(transaction_history, initial_balance, time, price):
    #     # Prepare data for plotting
    #     balance_over_time = [initial_balance]
    #     dates = [time[0]]

    #     for transaction in transaction_history:
    #         dates.append(transaction['Date'])
    #         if (transaction['Type'] == 'Buy'):
    #             balance_over_time.append(balance_over_time[-1] - transaction['Shares'] * transaction['Price'])
    #         else:
    #             balance_over_time.append(balance_over_time[-1] + transaction['Shares'] * transaction['Price'])
    #         print(transaction)

    #     # Plot balance over time
    #     fig1 = plt.figure(figsize=(8, 6))
    #     plt.plot(dates, balance_over_time)
    #     plt.title('Account Balance Over Time')
    #     plt.xlabel('Date')
    #     plt.ylabel('Balance')
    #     plt.xticks(rotation=45)
    #     plt.grid(True)
    #     # Plot transaction markers
    #     for transaction in transaction_history:
    #         if transaction['Type'] == 'Buy':
    #             marker = 'o'
    #             color = 'green'
    #         else:
    #             marker = 'o'
    #             color = 'red'
    #         plt.scatter(transaction['Date'], balance_over_time[dates.index(transaction['Date'])], marker=marker, color=color)
    #     #plot stock price to compare
    #     fig2 = plt.figure(figsize=(8, 6))
    #     plt.plot(time, price, label="Price")
    #     plt.title('Stock Price over Time')
    #     plt.xlabel('Date')
    #     plt.ylabel('Price')
    #     plt.xticks(rotation=45)
    #     plt.show()