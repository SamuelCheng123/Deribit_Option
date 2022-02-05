# Deribit_Option

## Get_book_summary_by_currency
API 接口 : `https://deribit.com/api/v2/public/get_book_summary_by_currency` 
透過這個街口獲取 Deribit 上不同交割日期的比特幣期權合約數據
```
options = Get_book_summary_by_currency(currency='BTC')
options.sorted_Date
```
result:
```
['SYN.BTC-6FEB22',
 'SYN.BTC-7FEB22',
 'BTC-11FEB22',
 'BTC-18FEB22',
 'BTC-25FEB22',
 'BTC-25MAR22',
 'SYN.BTC-29APR22',
 'BTC-24JUN22',
 'BTC-30SEP22',
 'BTC-30DEC22']
 ```
 可以看到 Deribit 提供幾天後就交割的周合約，四月六月交割的月合約，還有年底交割的合約
 每個合約交割時間都是當日的 16:00 (UTC+8)
 將其中一個日期輸入到 `options.options_perDate`
 `options.options_perDate[options.sorted_Date[0]]`
 ![image](https://user-images.githubusercontent.com/70627447/152637814-ba55132c-eca4-4f33-adad-827ff28e67c0.png)
拿到 2022/2/6 交割的合約信息，有標記價格、未平倉量等等資訊

現在來用這些計算 2/6 所有到期合約的最大痛點價格
```
option = options.options_perDate[options.sorted_Date[0]]
options.maxPainPrice(option)
```
result:
```
{'callOpenInterest': 885.5,
 'putOpenInterest': -1411.4,
 'maxPainPrice': 41000,
 'maxPainPriceProfit': 324000,
 'sumProfitEachPrice':
 39500      576500
 40000      399000
 40500      361500
 41000      324000
 41500      551500
 42000      779000
 42500     1132000}
 ```
 算出當合約交割時 BTC/USD 價格為多少的時候選擇權買方的收益 (沒有扣除獲得選擇權的成本)
 收益計算單位為USD，未平倉量單位則是BTC
