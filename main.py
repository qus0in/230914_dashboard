import streamlit as st
import data
from datetime import date

def bond():
    col1, col2 = st.columns(2)
    with col1:
        earn = st.number_input('기준수익률(%)',
            value=5, step=1, min_value=0, max_value=20) / (1 - 0.154)
    with col2:
        expire = st.selectbox('기간', ['3년', 'ISA'])
        if expire == '3년':
            days = 365 * 3
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
    col1, col2 = st.columns(2)
    with col1:
        money = st.number_input('투자금 (원)',
            min_value=0, step=1, value=80_000_000)
    with col2:
        cnt = st.number_input('포함 종목 수', value=4, min_value=1, max_value=10)
    with st.spinner('데이터 로딩 중...'):
        score = data.get_universe_score()
        table = score\
            .query(f'점수 >= {score.점수.quantile((10 - cnt) / 10)} & 점수 > 0')\
            .sort_values('점수', ascending=False)
    table['유닛'] = (table.점수 * money / 5)\
        .apply(lambda x: int(x / 100000) * 100000)
    st.write(f'🧮 합계 : {format(table.유닛.sum(), ",")}원')
    st.dataframe(table,
        use_container_width=True,
        hide_index=True,
        height=175,
    )

if __name__ == '__main__':
    st.set_page_config('대시보드', '😭')
    tab1, tab2 = st.tabs(['채권', 'ETF'])
    with tab1:
        try:
            bond()
        except:
            st.info('발빠진 쥐')

    with tab2:
        etf()