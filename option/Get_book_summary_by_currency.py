import requests
import pandas as pd
import math

class Get_book_summary_by_currency():
    def __init__(self , currency):
        self.url = f"https://deribit.com/api/v2/public/get_book_summary_by_currency?currency={currency}&kind=option"
        self.get_data() # 爬取資料
        self.underlying_indexs_Date()  # 將 underlying_indexs 按照日期順序重排一遍 (使用 underlying_indexs_toDatetime )
        
    def get_data(self):
        url = self.url
        options = requests.get(url).json()['result']
        # 將 option 按照交割日期分類
        und_index = pd.DataFrame(options).groupby("underlying_index")
        underlying_indexs = und_index.size().index
        options_perDate = {}
        for underlying_index in underlying_indexs:
            options_perDate[underlying_index] = und_index.get_group(underlying_index)
        self.underlying_indexs = underlying_indexs
        self.options_perDate = options_perDate
        #print(options_perDate[underlying_indexs[0]].head(3))
    
    # 將 11FEB22 轉換成 2022-02-11 的函數
    def underlying_indexs_toDatetime(self , underlying_index):
        from itertools import groupby
        import calendar  # 用法 https://blog.csdn.net/u010891397/article/details/86632214
        import datetime
        s = underlying_index.split('-')[-1]
        day_month_year = [''.join(list(g)) for k, g in groupby(s, key=lambda x: x.isdigit())]
        day = int(day_month_year[0])
        month_letter = day_month_year[1][0]+day_month_year[1][1:].lower()  # ex. Jan、Feb
        month = int(list(calendar.month_abbr).index(month_letter))
        year = int(day_month_year[2])
        date = datetime.date(2000+year , month , day)
        return date
    
    # 將 underlying_indexs 按照日期順序重排一遍 (使用 underlying_indexs_toDatetime )
    def underlying_indexs_Date(self):
        underlying_indexs = self.underlying_indexs
        underlying_indexs_Date = pd.Series(underlying_indexs).apply(self.underlying_indexs_toDatetime)
        underlying_indexs_Date = pd.Series(list(underlying_indexs_Date) , index=underlying_indexs)
        underlying_indexs_Date = underlying_indexs_Date.sort_values()
        self.sorted_Datetime = underlying_indexs_Date    
        self.sorted_Date = list(underlying_indexs_Date.index)
        
    def maxPainPrice(self , options_perDate):
        instrument_name = pd.Series(options_perDate['instrument_name'].values)
        settlePrice = instrument_name.apply(lambda x: x.split('-')[2])
        call_put = instrument_name.apply(lambda x: x.split('-')[3])
        open_interest = pd.Series(options_perDate['open_interest'].values * call_put.apply(lambda x:1 if(x=='C') else -1))
        oi_df = pd.concat([settlePrice,call_put,open_interest],axis=1)#.set_index(0)
        # 計算用來計算 max pain price 的最小單位 (ex.BTC 一顆 41000 就取前兩位數再除二 1000/2=500)
        power = int(math.log( settlePrice.median() , 10 ))
        if(power < 0):
          power -= 1
        base_index = 10 ** (power -1)
        # 計算每個價格 opion 買方的獲利
        def option_profit(oidf_row):
            profit = (int(oidf_row['price']) - int(oidf_row[0]))*int(oidf_row[2])
            if profit<0:
                profit =0
            return profit
        maxPainPrice = 0
        maxPainPriceProfit = 999999999999999999999999999999
        priceList = []
        sumProfitList =  []
        for price in range( int(settlePrice.min()) , int(settlePrice.max()) , int(base_index/2)):
            oi_dff = oi_df.copy()
            oi_dff.loc[: , 'price'] = price
            oi_dff.loc[: , 'profit'] = oi_dff.apply(option_profit , axis=1)
            sumProfit = oi_dff.loc[: , 'profit'].sum()
            # 求出最大痛點價格
            if sumProfit < maxPainPriceProfit:
                maxPainPriceProfit = sumProfit
                maxPainPrice = price
            priceList += [price]
            sumProfitList += [sumProfit]
        sumProfitEachPrice = pd.Series(sumProfitList , index=priceList)
        callOpenInterest = open_interest.apply(lambda x:x if(x>0) else 0).sum()
        putOpenInterest = open_interest.apply(lambda x:0 if(x>0) else x).sum()
        #print(oi_df)
        return {'callOpenInterest':callOpenInterest , 'putOpenInterest':putOpenInterest , 'maxPainPrice':maxPainPrice , 'maxPainPriceProfit':maxPainPriceProfit , 'sumProfitEachPrice':sumProfitEachPrice}