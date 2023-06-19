from model import Model
from view import View
from tkinter import messagebox

class Controller:
    def __init__(self):
        # Transmits events from the VIEW object to the MODEL and sends data back
        self.MODEL = Model(self)
        self.VIEW = View(self)

    def StartUp(self):
        pass

    def RunSearch(self, ticker, timeperiod):
        if ticker != '':
            try:
                dates, prices = self.SearchTicker(ticker, timeperiod)
            except:
                messagebox.showerror(title='Error', message='Invalid ticker!')
            try:
                bestHigh, bestLow = self.MODEL.findBestRSI(dates,prices)
            except:
                messagebox.showerror(title='Error', message=f'Failed to find the best RSI for {ticker}')

    def SearchTicker(self, ticker, timeperiod):
        time = 0
        val = ''
        for c in timeperiod:
            if c.isdigit():
                val += c
        val = int(val)
        if 'months' in timeperiod:
            time = val/12*365
        elif 'year' in timeperiod:
            time = val*365
        else:
            messagebox.showerror(title='Error', message='Invalid search time!')
        try:
            dates, prices = self.MODEL.get_historical_data(ticker.upper(), time)
            return dates, prices
        except Exception as e:
            raise e
