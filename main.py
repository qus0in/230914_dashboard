import streamlit as st
import data
from datetime import date

def bond():
    col1, col2 = st.columns(2)
    with col1:
        earn = st.number_input('기준수익률(%)',
            value=6.0, step=0.1, min_value=0.0, max_value=20.0)
    with col2:
        expire = st.selectbox('기간', ['5년', 'ISA'])
        if expire == '5년':
            days = 365 * 5
            earn /= (1 - 0.154)
        if expire == 'ISA':
            days = (date(2024, 11, 9) - date.today()).days
    table = data.get_bond_table().query(
        f'수익률 >= {earn} & 투자기간 <= {days}')\
        .sort_values('수익률', ascending=False)\
        .drop(columns=['투자기간'])
    # ((매도가+이표수입)/매수가-1)*(365/기간)
    st.write(f'💰 **결과** : {len(table)}건')
    st.dataframe(table,
        use_container_width=True,
        hide_index=True,
        height=350,
    )

def etf():
    col1, col2, col3 = st.columns(3)
    with col1:
        money = st.number_input('투자금 (원)',
            min_value=0, step=1_000_000, value=39_000_000)
    with col2:
        risk = st.number_input('리스크 조절 (%)', value=1.5, step=0.5, min_value=1.0, max_value=3.0)
    with col3:
        cnt = st.number_input('포함 종목 수', value=4, min_value=1, max_value=10)
    with st.spinner('데이터 로딩 중...'):
        score = data.get_universe_score()
        table = score.copy()
        table = score\
            .loc[score.점수 > score.query('종목코드 == "357870"').iloc[-1, 2]]\
            .sort_values('점수', ascending=False)
    table['유닛'] = (table.변동성.apply(lambda x: min(1, risk / x / 100)) * money / cnt)\
        .apply(lambda x: int(x / 100000) * 100000)
    table['IN'] = table.점수 > table.head(5)
    st.write(f'🧮 합계 (TOP{cnt}) : {format(table.head(cnt).유닛.sum(), ",")}원')
    st.dataframe(table,
        use_container_width=True,
        hide_index=True,
        height=213,
    )

if __name__ == '__main__':
    st.set_page_config('대시보드', '😭')
    tab1, tab2 = st.tabs(['채권', 'ETF'])
    with tab1:
        try:
            bond()
        except Exception as e:
            st.info('발빠진 쥐 🐭')
            st.error(e)

    with tab2:
        etf()