alf123
======
    1.計算MA(移動平均)

    MA=最近N日累計收盤價/ N日

    2.計算MD(移動標準差)

    MD=平方根(最近M日累計(收盤價- MA)*(收盤價- MA)/M)

    3.計算MB、UP、DN

    MB= I- 1日MA

    UP= MB+ 2* MD 

    DN= MB- 2* MD

方法是:如果上漲超過UP為買進訊號, 買進訊號出現之後, 如果下跌至穿越MB為賣出訊號

N與M為可以調整的變數, 預設N=10, M=30
