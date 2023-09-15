import requests
import pandas as pd
import FinanceDataReader as fdr
import streamlit as st

def get_bond_data():
    URL = 'https://www.shinhansec.com/siw/wealth-management/bond-rp/590401/data.do'
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('NOT OK')

def get_bond_table():
    data = get_bond_data()
    df = pd.DataFrame(data.get('body').get('반복데이타0'))
    # 종목명 (0), 매도수익률 (1), 투자기간 (2), 표면금리 (4),
    # 신용도 (5), 종목코드 (6), 현재가 (7), 매수수익률(13), 
    df = df.iloc[:, [0, 3, 2, 4, 5, 7, 1]]
    df.columns = ['종목명', '거래금액', '투자기간', '표면금리', '신용도',
                '현재가', '수익률']
    df.거래금액 = df.거래금액.astype(int)
    df = df.loc[df.거래금액 >df.거래금액.mean()]
    df.수익률 = df.수익률.astype(float)
    df.투자기간 = df.투자기간.astype(int)
    df.신용도 = df.신용도.str.strip()
    return df.query(
        'not (신용도.str.contains("B") & not 신용도.str.contains("BBB"))'
    ).drop(columns=['거래금액']).reset_index(drop=True)

@st.cache_data
def get_universe_data():
    URL = 'https://finance.naver.com/api/sise/etfItemList.nhn'
    response = requests.get(URL, dict(etfType=0))
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('NOT OK')

def get_universe_table():
    etfItemList = get_universe_data().get('result').get('etfItemList')
    df = pd.DataFrame(etfItemList).dropna()
    return df.iloc[:, [0, 2]].reset_index(drop=True)

def get_universe_score():
    names = get_universe_table()
    universe = ['139230', '455850', '091180', '455860', '244580',
                '132030', '261220', '261240', '114800', '251340']
    data = [(u, names.query(f'itemcode == "{u}"').iloc[0,1],
             get_score(u)) for u in universe]
    return pd.DataFrame(data, columns=['종목코드', '이름', '점수'])

def get_score(code, risk=0.01):
    periods = [5, 8, 13, 21, 34]
    data = fdr.DataReader(code)
    close = data.Close
    scores = [close.rolling(p).mean().iloc[-1] < close.iloc[-1] for p in periods]
    concat = lambda x, y, z: pd.concat([x, y], axis=1).apply(z, axis=1)
    tr = concat(data.High, data.Close.shift(1), max)\
         - concat(data.Low, data.Close.shift(1), min)
    aatr = tr.ewm(max(periods)).mean().iloc[-1] / close.iloc[-1]
    risk_control = min(1, risk / aatr)
    return int(sum(scores) / len(periods) * risk_control * 1000) / 1000