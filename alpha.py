KEY = "H3PUK0L7U3UGOHGD"

import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Function to fetch historical data for a stock
def get_historical_data(stock_symbol):
    # Enter your AlphaVantage API key here
    api_key = KEY

    # AlphaVantage API endpoint for getting weekly stock prices
    endpoint = "https://www.alphavantage.co/query"

    # Parameters for the API request
    params = {
        "function": "TIME_SERIES_WEEKLY",
        "symbol": stock_symbol,
        "apikey": api_key,
    }

    try:
        # Send the GET request to the AlphaVantage API
        response = requests.get(endpoint, params=params)
        data = response.json()

        # Parse the response to extract the historical data
        time_series = data["Weekly Time Series"]
        

        
        # Lists to store the time (x-axis) and price (y-axis) data
        time = []
        open = []
        high = []
        low = []
        price = []
        volume = []


        # Calculate the date one year ago from today
        one_year_ago = datetime.now() - timedelta(days=3650)

        # Iterate over the time series data and append the values to the lists
        for date, values in time_series.items():
            date_obj = datetime.strptime(date, "%Y-%m-%d")

            # Only append data if it falls within the last year
            if date_obj >= one_year_ago:
                time.append(date)
                open.append(float(values["1. open"]))
                high.append(float(values["2. high"]))
                low.append(float(values["3. low"]))
                price.append(float(values["4. close"]))
                volume.append(float(values["5. volume"]))
        
        #Calculate Rsi
        def calculate_rsi(n=14):
            df = pd.DataFrame(price)
            delta = df.diff()
            up = delta.clip(lower=0)
            down = -delta.clip(upper=0)
            ema_up = up.ewm(com=n - 1, min_periods=n).mean()
            ema_down = down.ewm(com=n - 1, min_periods=n).mean()
            rs = ema_up / ema_down
            rsi = 100 - (100 / (1 + rs))
            return rsi

        rsi = calculate_rsi()
        print(rsi)


        # Reverse the lists to ensure correct chronological order
        time.reverse()
        open.reverse()
        high.reverse()
        low.reverse()
        price.reverse()
        volume.reverse()
        
        # Create the figure and axes
        fig, axs  = plt.subplots(2, 2, figsize=(10, 8))
        
        #plot ax1
        axs[0,0].plot(time, price, label="Close")
        axs[0,0].plot(time, open, label="Open")
        axs[0,0].plot(time, high, label="High")
        axs[0,0].plot(time, low, label="Low")
        axs[0,0].set_xlabel('Time')
        axs[0,0].set_ylabel('Price')
        axs[0,0].set_title(f"{stock_symbol} Stock Price")
        axs[0,0].legend()

        # Plot ax2
        axs[0,1].plot(time, volume, label="Volume")
        axs[0,1].set_xlabel('Time')
        axs[0,1].set_ylabel('Volume')
        axs[0,1].set_title(f"{stock_symbol} Stock Volume")
        axs[0,1].legend()

        #PLOT RSI
        axs[1,1].plot(time, rsi, label="RSI")
        
        #plt.xticks(rotation=45)
        plt.tight_layout()
        plt.legend()
        plt.show()

    except requests.exceptions.RequestException as e:
        print("Error occurred while fetching data:", e)


# Main program
if __name__ == "__main__":
    stock_symbol = input("Enter the stock symbol: ")
    get_historical_data(stock_symbol)
