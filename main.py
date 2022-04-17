from locale import currency
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, date
from aux_functions import *
from scrapper import *
import plotly.express as px
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

# ----------------------- LAYOUT ---------------------------
st.set_page_config(page_title="Stock Analyzer",layout="wide")
st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# ------- MAIN -------
header_cols = st.columns([3,1])
ticker = header_cols[1].text_input('Enter stock ticker', 'AAPL')

# Getting data
# ===============================
ticker_yahoo = yf.Ticker(ticker)

 # Chart data
data = ticker_yahoo.history(period="max")

close_data = pd.DataFrame(data["Close"])

last_quote = data['Close'].iloc[-1] # Last price
day_delta = data['Close'].iloc[-1] - data['Close'].iloc[-2] # Change in price

# 52 weeks high and low
end = datetime.now()
start = end - relativedelta(weeks=52)

data_52w = ticker_yahoo.history(start=start, end=end)
high_52w = data_52w['High'].max()
low_52w = data_52w['Low'].min()

# Basic info
df = get_stock_basic_data(ticker)

name = df.loc['Name', "Information"]
currency = df.loc['Currency', "Information"]
sector = df.loc['Sector', "Information"]
industry = df.loc['Industry', "Information"]
country = df.loc['Country', "Information"]
exchange = df.loc['Exchange', "Information"]
insider_ownership = df.loc['Insider Percentage', "Information"]
institutional_ownership = df.loc['Institution Percentage', "Information"]

shares = ticker_yahoo.info['sharesOutstanding'] / 1000000000
market_cap = round(last_quote * shares,2)


# convert string to datetime
ipo_date = df.loc['IPO', "Information"]
ipo_year = int(ipo_date[-4:])
today = date.today()
years = today.year - ipo_year

div_yield = df.loc["Dividend Yield", "Information"]
revenue_per_share = df.loc["Revenue per Share", "Information"]
eps = df.loc["EPS", "Information"]
fcf_per_share = df.loc["FCF per Share", "Information"]
div_per_share = df.loc["Dividend per Share", "Information"]
capex_per_share = df.loc["Capex per Share", "Information"]

try:
    div_payout = round(float(div_per_share) / float(eps),2)
except:
    div_payout = "- -"

summary = df.loc["Summary", "Information"]

ret_1_year = df.loc["Return 1 Year Stock", "Information"]
ret_3_year = df.loc["Return 3 Years Stock", "Information"]
ret_5_years = df.loc["Return 5 Years Stock", "Information"]
ret_1_year_sp500 = df.loc["Return 1 Year S&P 500", "Information"]
ret_3_year_sp500 = df.loc["Return 3 Years S&P 500", "Information"]
ret_5_years_sp500 = df.loc["Return 5 Years S&P 500", "Information"]

ret_1_year, ret_3_year, ret_5_years, ret_1_year_sp500, ret_3_year_sp500, ret_5_years_sp500 = clean_string_to_numeric([ret_1_year, ret_3_year, ret_5_years, ret_1_year_sp500, ret_3_year_sp500, ret_5_years_sp500])

cagr_ret_3_year = ((1 + (float(ret_3_year) / 100)) ** (1 / 3) -1) * 100
cagr_ret_5_years = ((1 + (float(ret_5_years) / 100)) ** (1 / 5) -1) * 100
cagr_ret_3_year_sp500 = ((1 + (float(ret_3_year_sp500) / 100)) ** (1 / 3) -1) * 100
cagr_ret_5_years_sp500 = ((1 + (float(ret_5_years_sp500) / 100)) ** (1 / 5) -1) * 100

ret_1_year_alpha = round(float(ret_1_year) - float(ret_1_year_sp500),2)
ret_3_year_alpha = round(float(ret_3_year) - float(ret_3_year_sp500),2)
ret_5_years_alpha = round(float(ret_5_years) - float(ret_5_years_sp500),2)
cagr_ret_3_year_alpha = round(float(cagr_ret_3_year) - float(cagr_ret_3_year_sp500),2)
cagr_ret_5_years_alpha = round(float(cagr_ret_5_years) - float(cagr_ret_5_years_sp500),2)

# Financials

fudamentals_df = get_stock_fundamental_data(ticker, True)


last_5_years_fundamentals = fudamentals_df.iloc[:,-5:]

enterprise_value = market_cap + (last_5_years_fundamentals.loc["Net Debt"].to_numpy()[-1]/1000)


# Showing data

header_cols[0].title(name + "   [" + ticker + "]")
main_columns = st.columns([2,1,1,1])

# Price Chart
fig = px.area(close_data, title = name + 'share price')

fig.update_xaxes(
    title_text = 'Date',
    rangeslider_visible = True,
    rangeselector = dict(
        buttons = list([
            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            dict(count = 3, label = '3Y', step = 'year', stepmode = 'backward'),
            dict(count = 5, label = '5Y', step = 'year', stepmode = 'backward'),
            dict(count = 10, label = '10Y', step = 'year', stepmode = 'backward'),
            dict(step = 'all')]
            ),
            font = dict(color = "#000000")
            )
            )

fig.update_yaxes(title_text = ticker + ' Close Price', tickprefix = '$')
fig.update_layout(template="plotly_dark", showlegend = False,
    title = {
        'text': name +' SHARE PRICE',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
       )

initial_range = [
    datetime.now() - relativedelta(years=3), datetime.now()
]

fig['layout']['xaxis'].update(range=initial_range)

main_columns[0].plotly_chart(fig)



# Summary Info
main_columns[1].metric("Price", str(round(last_quote,2)) + " " + currency, str(round(day_delta,2))  + " " + currency + " (" + str(round(day_delta/last_quote*100,2)) + "%)")
main_columns[2].metric("Sector & Industry", sector, industry,delta_color="off")
main_columns[3].metric("Country & Exchange", country, exchange, delta_color="off")
main_columns[1].metric("Market Cap & EV","{:,.0f}".format(market_cap) + " B",  "{:,.0f}".format(enterprise_value) + " B",delta_color="off")
main_columns[2].metric("Years & IPO Date", str(years), ipo_date, delta_color="off")
main_columns[3].metric("Dividend Yield & Payout", str(div_yield), str(div_payout) + "%", delta_color="off")

main_columns[1].metric("52 week high", str(round(high_52w,2)) + " " + currency, str(round(((last_quote / high_52w) -1) *100,2)) + "%")
main_columns[2].metric("Insider Ownership",insider_ownership)
main_columns[3].metric("Institutional Ownership", institutional_ownership)

# END OF SECTION 0

with st.expander("Share Return", expanded=True):
    share_return_columns = st.columns(5)
    share_return_columns[0].metric("Return 1 year", ret_1_year + "%", str(ret_1_year_alpha) + "%")
    share_return_columns[1].metric("Return 3 years", ret_3_year + "%", str(ret_3_year_alpha) + "%")
    share_return_columns[2].metric("Return 5 years", ret_5_years + "%", str(ret_5_years_alpha) + "%")
    share_return_columns[3].metric("CAGR 3 years", str(round(cagr_ret_3_year,2)) + "%", str(cagr_ret_3_year_alpha) + "%")
    share_return_columns[4].metric("CAGR 5 years", str(round(cagr_ret_5_years,2)) + "%", str(cagr_ret_5_years_alpha) + "%")

    st.markdown("**Return compared to sp500*")

    st.markdown("**Summary:**")
    st.write(summary)

# END OF SECTION 1  
    
    

with st.expander("Earnings & Growth", expanded=True):

    earnings_df = last_5_years_fundamentals.loc[["Revenue", "Gross Profit", "EBITDA", "Operating Income", "Net Income", "Free Cash Flow", "Dividends Paid"],:].copy()
    earnings_df = earnings_df.applymap('{:,.0f}'.format)

    growth_df = last_5_years_fundamentals.iloc[-115:-55,-1]

    new_growth_df = pd.DataFrame(index=["Revenue", "Gross Profit", "EBITDA", "Operating Income", "Net Income", "EPS Diluted", "Free Cash Flow", "FCF per share"],
                                columns=["Growth yy", "Growth 3y. av.", "Growth 5y. av.", "Growth 10y. av.", "CAGR"])

    for index, row in new_growth_df.iterrows():
        new_growth_df.at[index, "Growth yy"] = growth_df.loc[index+" growth yy"]
        new_growth_df.at[index, "Growth 3y. av."] = growth_df.loc[index+" growth 3y. av."]
        new_growth_df.at[index, "Growth 5y. av."] = growth_df.loc[index+" growth 5y. av."]
        new_growth_df.at[index, "Growth 10y. av."] = growth_df.loc[index+" growth 10y. av."]
        new_growth_df.at[index, "CAGR"] = growth_df.loc[index+" cagr"]

    new_growth_df = new_growth_df.applymap('{:.2%}'.format)
    
    buyback_rate = round(growth_df.at["Weighted Avg. Shares Outs. cagr"] * 100,2)

    # Metrics
    earnings_columns = st.columns(5)
    
    earnings_columns[0].metric("Revenue per share", revenue_per_share, delta_color="off")
    earnings_columns[1].metric("EPS", eps, delta_color="off")
    earnings_columns[2].metric("Free Cash Flow per share", fcf_per_share, delta_color="off")
    earnings_columns[3].metric("Dividend per share", div_per_share, delta_color="off")
    earnings_columns[4].metric("Buyback Rate", str(buyback_rate) + "%", delta_color="off")


    earnings_columns2 = st.columns(2)
    # Income
    earnings_columns2[0].write("Income Statement (mm):")
    earnings_columns2[0].table(data=earnings_df)

    # Growth
    earnings_columns2[0].write("Growth:")
    earnings_columns2[0].table(data=new_growth_df)        

    # Income Statement Chart

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=last_5_years_fundamentals.columns,
        y=last_5_years_fundamentals.loc["Revenue"],
        name='Revenue',
    ))
    fig.add_trace(go.Bar(
        x=last_5_years_fundamentals.columns,
        y=last_5_years_fundamentals.loc["Gross Profit"],
        name='Gross Profit',
    ))
    fig.add_trace(go.Bar(
        x=last_5_years_fundamentals.columns,
        y=last_5_years_fundamentals.loc["EBITDA"],
        name='EBITDA',
    ))
    fig.add_trace(go.Bar(
        x=last_5_years_fundamentals.columns,
        y=last_5_years_fundamentals.loc["Operating Income"],
        name='Operating Income',
    ))
    fig.add_trace(go.Bar(
        x=last_5_years_fundamentals.columns,
        y=last_5_years_fundamentals.loc["Net Income"],
        name='Net Income',
    ))
    fig.add_trace(go.Bar(
        x=last_5_years_fundamentals.columns,
        y=last_5_years_fundamentals.loc["Free Cash Flow"],
        name='Free Cash Flow',
    ))
    fig.add_trace(go.Bar(
        x=last_5_years_fundamentals.columns,
        y=last_5_years_fundamentals.loc["Dividends Paid"],
        name='Dividends Paid',
    ))
    fig.update_layout(barmode='group', xaxis_tickangle=-45, width=800, height=650)

    earnings_columns2[1].plotly_chart(fig)

# END OF SECTION 3

with st.expander("Profitability", expanded=True):
    # Returns
    prof_columns = st.columns(2)
    prof_columns[0].write("Returns:")


    returns_df = last_5_years_fundamentals.loc[["Return on Assets", "Return on Equity", "Return on Invested Capital"],:]
    returns_df["Average"] = returns_df.mean(axis=1)
    new_returns_df = returns_df.applymap('{:.2%}'.format)

    prof_columns[0].dataframe(data=new_returns_df)

    prof_columns[0].write("Margins:")
    margins_df = last_5_years_fundamentals.loc[["Gross Profit Ratio", "EBITDA ratio", "Operating Income ratio", "Net Income Ratio", "FCF Ratio"],:]
    margins_df.loc[["Gross Profit Ratio", "EBITDA ratio", "Operating Income ratio", "Net Income Ratio"]] = margins_df.loc[["Gross Profit Ratio", "EBITDA ratio", "Operating Income ratio", "Net Income Ratio"]] / 100
    margins_df["Average"] = margins_df.mean(axis=1)
    new_margins_df = margins_df.applymap('{:.2%}'.format)

    prof_columns[0].dataframe(data=new_margins_df)


    # Income Statement Chart
    fig = px.line(last_5_years_fundamentals.loc[["Return on Assets", "Return on Equity", "Return on Invested Capital"],:].T)
    fig.update_layout(xaxis_title=None, yaxis_title=None, width=800)

    prof_columns[1].plotly_chart(fig)


with st.expander("Financial Strength", expanded=True):
    

    fin_columns = st.columns([1,1,1,3])


    # fin_columns[0].markdown('##')
    fin_columns[0].markdown('### Financial Ratios:')
    fin_columns[1].markdown('##')
    fin_columns[1].markdown('#')
    fin_columns[2].markdown('##')
    fin_columns[2].markdown('#')

    # cash_and_short_term_invs
    cash_and_short_term_invs = last_5_years_fundamentals.loc["Cash & Short-Term Investments",:]
    delta_cash_and_short_term_invs = cash_and_short_term_invs.diff()
    cash_and_short_term_invs = cash_and_short_term_invs.map('{:,.0f}'.format)
    delta_cash_and_short_term_invs = delta_cash_and_short_term_invs.map('{:,.0f}'.format)
    fin_columns[0].metric("Cash & Short-Term Investments", cash_and_short_term_invs[-1],delta_cash_and_short_term_invs[-1])

    # total_debt
    total_debt = last_5_years_fundamentals.loc["Total Debt",:]
    delta_total_debt = total_debt.diff()
    total_debt = total_debt.map('{:,.0f}'.format)
    delta_total_debt = delta_total_debt.map('{:,.0f}'.format)
    fin_columns[1].metric("Total Debt", total_debt[-1],delta_total_debt[-1], delta_color="inverse")

    # net_debt
    net_debt = last_5_years_fundamentals.loc["Net Debt",:]
    delta_net_debt = net_debt.diff()
    net_debt = net_debt.map('{:,.0f}'.format)
    delta_net_debt = delta_net_debt.map('{:,.0f}'.format)
    fin_columns[2].metric("Net Debt", net_debt[-1],delta_net_debt[-1], delta_color="inverse")

    # debt_to_equity
    debt_to_equity = last_5_years_fundamentals.loc["Debt to Equity",:]
    delta_debt_to_equity = debt_to_equity.diff()
    debt_to_equity = debt_to_equity.map('{:,.2f}'.format)
    delta_debt_to_equity = delta_debt_to_equity.map('{:,.2f}'.format)
    fin_columns[0].metric("Debt to Equity", debt_to_equity[-1],delta_debt_to_equity[-1], delta_color="inverse")

    # debt_to_ebitda
    debt_to_ebitda = last_5_years_fundamentals.loc["Debt to EBITDA",:]
    delta_debt_to_ebitda = debt_to_ebitda.diff()
    debt_to_ebitda = debt_to_ebitda.map('{:,.2f}'.format)
    delta_debt_to_ebitda = delta_debt_to_ebitda.map('{:,.2f}'.format)
    fin_columns[1].metric("Debt to EBITDA", debt_to_ebitda[-1],delta_debt_to_ebitda[-1], delta_color="inverse")

    # interest_coverage
    interest_coverage = last_5_years_fundamentals.loc["Interest Coverage",:]
    delta_interest_coverage = interest_coverage.diff()
    interest_coverage = interest_coverage.map('{:,.2f}'.format)
    delta_interest_coverage = delta_interest_coverage.map('{:,.2f}'.format)
    fin_columns[2].metric("Interest Coverage", interest_coverage[-1],delta_interest_coverage[-1])

    # current ratio
    current_ratio = last_5_years_fundamentals.loc["Current Ratio",:]
    delta_current_ratio = current_ratio.diff()
    current_ratio = current_ratio.map('{:,.2f}'.format)
    delta_current_ratio = delta_current_ratio.map('{:,.2f}'.format)
    fin_columns[0].metric("Current Ratio", current_ratio[-1],delta_current_ratio[-1])

    # quick ratio
    quick_ratio = last_5_years_fundamentals.loc["Quick Ratio",:]
    delta_quick_ratio = quick_ratio.diff()
    quick_ratio = quick_ratio.map('{:,.2f}'.format)
    delta_quick_ratio = delta_quick_ratio.map('{:,.2f}'.format)
    fin_columns[1].metric("Quick Ratio", quick_ratio[-1],delta_quick_ratio[-1])

    # liabilities to assets
    liabilities_to_assets = last_5_years_fundamentals.loc["Liabilities to Assets",:]
    delta_liabilities_to_assets = liabilities_to_assets.diff()
    liabilities_to_assets = liabilities_to_assets.map('{:,.2f}'.format)
    delta_liabilities_to_assets = delta_liabilities_to_assets.map('{:,.2f}'.format)
    fin_columns[2].metric("Liabilities to Assets", liabilities_to_assets[-1],delta_liabilities_to_assets[-1], delta_color="inverse")


    # Chart
    financial_health_df = pd.DataFrame(columns=["Term", "Type", "Value"])
    financial_health_df = financial_health_df.append({"Term":"Long", "Type": "Assets",  "Value": last_5_years_fundamentals.at["Total Non-Current Assets", last_5_years_fundamentals.columns[-1]]},ignore_index=True)
    financial_health_df = financial_health_df.append({"Term":"Long", "Type": "Liabilities", "Value": last_5_years_fundamentals.at["Total Non-Current Liabilities", last_5_years_fundamentals.columns[-1]]},ignore_index=True)
    financial_health_df = financial_health_df.append({"Term":"Short", "Type": "Assets","Value":  last_5_years_fundamentals.at["Total Current Assets", last_5_years_fundamentals.columns[-1]]},ignore_index=True)
    financial_health_df = financial_health_df.append({"Term":"Short", "Type":  "Liabilities","Value":  last_5_years_fundamentals.at["Total Current Liabilities", last_5_years_fundamentals.columns[-1]]},ignore_index=True)



    fig = px.bar(financial_health_df, x="Term", y="Value", color="Type",barmode="group", width=800)
    fin_columns[3].plotly_chart(fig)

with st.expander("Valuation", expanded=True):
    last_year_fundamentals = (fudamentals_df.iloc[:,-1].T).copy()

    last_year_fundamentals["Price to Sales"] = last_quote / last_year_fundamentals["Revenue per Share"]

    last_year_fundamentals["Price to Book"] = last_quote / last_year_fundamentals["Book value per share"]

    last_year_fundamentals["Price to Earnings"] = last_quote / last_year_fundamentals["EPS"]

    last_year_fundamentals["Price to FCF"] = last_quote / last_year_fundamentals["FCF per share"]

    last_year_fundamentals["EV to EBITDA"] = (enterprise_value * 1000) / last_year_fundamentals["EBITDA"]

    last_year_fundamentals["EV to FCF"] = (enterprise_value * 1000) / last_year_fundamentals["Free Cash Flow"]

    last_year_fundamentals["EV to Revenue"] = (enterprise_value * 1000) / last_year_fundamentals["Revenue"]

    
    last_year_fundamentals["PS to growth"] = last_year_fundamentals["Price to Sales"] / (last_year_fundamentals["Revenue growth 3y. av."] * 100)
    last_year_fundamentals["PE to growth"] = last_year_fundamentals["Price to Earnings"] / (last_year_fundamentals["EPS growth 3y. av."] * 100)
    last_year_fundamentals["PB to growth"] = last_year_fundamentals["Price to Book"] / (last_year_fundamentals["Book value growth 3y. av."] * 100)
    last_year_fundamentals["PFCF to growth"] = last_year_fundamentals["Price to FCF"] / (last_year_fundamentals["FCF per share growth 3y. av."] * 100)
    last_year_fundamentals["EVEBITDA to growth"] = last_year_fundamentals["EV to EBITDA"] / (last_year_fundamentals["EBITDA growth 3y. av."] * 100)
    last_year_fundamentals["EVFCF to growth"] = last_year_fundamentals["EV to FCF"] / (last_year_fundamentals["Free Cash Flow growth 3y. av."] * 100)
    last_year_fundamentals["EVRevenue to growth"] = last_year_fundamentals["EV to Revenue"] / (last_year_fundamentals["Revenue growth 3y. av."] * 100)

    last_year_fundamentals = last_year_fundamentals.T

    print(last_year_fundamentals)

    st.markdown("Basic ratios:")

    val_columns = st.columns(7)

    val_columns[0].metric("Price to Earnings", round(last_year_fundamentals.loc["Price to Earnings"],1))
    val_columns[1].metric("Price to Sales", round(last_year_fundamentals.loc["Price to Sales"],1))
    val_columns[2].metric("Price to Book", round(last_year_fundamentals.loc["Price to Book"],1))
    val_columns[3].metric("Price to FCF", round(last_year_fundamentals.loc["Price to FCF"],1))
    val_columns[4].metric("EV to Revenue", round(last_year_fundamentals.loc["EV to Revenue"],1))
    val_columns[5].metric("EV to EBITDA", round(last_year_fundamentals.loc["EV to EBITDA"],1))
    val_columns[6].metric("EV to FCF", round(last_year_fundamentals.loc["EV to FCF"],1))

    # st.markdown("With growth (3 year average):")
    val_columns2 = st.columns(7)
    val_columns2[0].metric("Price to Earnings", round(last_year_fundamentals.loc["PE to growth"],1), str(round(last_year_fundamentals["EPS growth 3y. av."] * 100,2)) + "%")
    val_columns2[1].metric("Price to Sales", round(last_year_fundamentals.loc["PS to growth"],1), str(round(last_year_fundamentals["Revenue growth 3y. av."] * 100,2)) + "%")
    val_columns2[2].metric("Price to Book", round(last_year_fundamentals.loc["PB to growth"],1), str(round(last_year_fundamentals["Book value growth 3y. av."] * 100,2)) + "%")
    val_columns2[3].metric("Price to FCF", round(last_year_fundamentals.loc["PFCF to growth"],1), str(round(last_year_fundamentals["FCF per share growth 3y. av."] * 100,2)) + "%")
    val_columns2[4].metric("EV to Revenue", round(last_year_fundamentals.loc["EVRevenue to growth"],1), str(round(last_year_fundamentals["Revenue growth 3y. av."] * 100,2)) + "%")
    val_columns2[5].metric("EV to EBITDA", round(last_year_fundamentals.loc["EVEBITDA to growth"],1), str(round(last_year_fundamentals["EBITDA growth 3y. av."] * 100,2)) + "%")
    val_columns2[6].metric("EV to FCF", round(last_year_fundamentals.loc["EVFCF to growth"],1), str(round(last_year_fundamentals["Free Cash Flow growth 3y. av."] * 100,2)) + "%")

    st.write("*Seconds row is divided by growth (3 year average)")

    st.markdown("### Discounted Cash Flow Model")

    dcf_columns = st.columns([1,1,2])
    growth_1 = dcf_columns[0].number_input("Growth years 1-5 (%)", value=round(last_year_fundamentals["EPS growth 3y. av."] * 100,2)*0.8)
    growth_2 = dcf_columns[0].number_input("Growth years 6-10 (%)", value=round(last_year_fundamentals["EPS growth 3y. av."]*100,2)/2)
    expected_multiple = dcf_columns[0].number_input("Expected multiple", value=15)
    discount_rate = dcf_columns[0].number_input("Discount rate (%)", value=14)
    current_earnings = dcf_columns[0].number_input("Current earnings (mm)", value=last_year_fundamentals["Net Income"])

    dcf_columns2 = st.columns(4)
    add_cash = dcf_columns2[0].checkbox("Add cash & short term investments")
    add_long_term_investments = dcf_columns2[0].checkbox("Add long term investments")
    substract_debt = dcf_columns2[0].checkbox("Substract debt")



    # Discounted Cash Flow

    year1 = (current_earnings * (1 + growth_1/100))
    year2 = (year1 * (1 + growth_1/100))
    year3 = (year2 * (1 + growth_1/100))
    year4 = (year3 * (1 + growth_1/100))
    year5 = (year4 * (1 + growth_1/100))
    year6 = (year5 * (1 + growth_2/100))
    year7 = (year6 * (1 + growth_2/100))
    year8 = (year7 * (1 + growth_2/100))
    year9 = (year8 * (1 + growth_2/100))
    year10 = (year9 * (1 + growth_2/100))

    discounted_year1 = year1 / (1 + discount_rate/100)
    discounted_year2 = year2 / (1 + discount_rate/100)**2
    discounted_year3 = year3 / (1 + discount_rate/100)**3
    discounted_year4 = year4 / (1 + discount_rate/100)**4
    discounted_year5 = year5 / (1 + discount_rate/100)**5
    discounted_year6 = year6 / (1 + discount_rate/100)**6
    discounted_year7 = year7 / (1 + discount_rate/100)**7
    discounted_year8 = year8 / (1 + discount_rate/100)**8
    discounted_year9 = year9 / (1 + discount_rate/100)**9
    discounted_year10 = year10 / (1 + discount_rate/100)**10

    discounted_values = [discounted_year1, discounted_year2, discounted_year3, discounted_year4, discounted_year5, discounted_year6, discounted_year7, discounted_year8, discounted_year9, discounted_year10]

    exit_value = (year10 * expected_multiple) / (1 + discount_rate/100)**10

    dcf = pd.DataFrame({"Discounted Value": discounted_values}, index=["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6", "Year 7", "Year 8", "Year 9", "Year 10"])
    dcf["Cumulative Value"] = dcf["Discounted Value"].cumsum()

    present_value = dcf.at["Year 9","Cumulative Value"] + exit_value
    present_value_with_cash = present_value

    if add_cash:
        present_value_with_cash += last_year_fundamentals.at["Cash & Short-Term Investments"]
    if add_long_term_investments:
        present_value_with_cash += last_year_fundamentals.at["Investments"]
    if substract_debt:
        present_value_with_cash -= last_year_fundamentals.at["Total Debt"]

    dcf_columns[1].markdown("#")
    dcf_columns[1].markdown("#")
    dcf_columns[1].table(dcf)

    # Chart
    fig = go.Figure(data=go.Scatter(x=dcf.index, y=dcf["Cumulative Value"]))
    fig.update_layout(title='Proyected Value of Future Cash Flows', width=800, height=500)
    dcf_columns[2].plotly_chart(fig)


    dcf_columns2[1].metric("Present Value of Future Cash Flows:","{:,.0f}".format(present_value))
    if add_cash:
        dcf_columns2[2].metric("Cash & Short-Term Investments::","{:,.0f}".format(last_year_fundamentals.at["Cash & Short-Term Investments"]))
        
    if add_long_term_investments:
        dcf_columns2[2].metric("Long Term Investments:","{:,.0f}".format(last_year_fundamentals.at["Investments"]))
    if substract_debt:
        dcf_columns2[3].metric("Debt:","{:,.0f}".format(last_year_fundamentals.at["Total Debt"]))
    
    dcf_columns2[1].metric("Number of shares:","{:,.0f}".format(ticker_yahoo.info['sharesOutstanding']/1000000))

    fair_value = int(present_value_with_cash) / (int(ticker_yahoo.info['sharesOutstanding'] / 1000000))
    dcf_columns2[3].metric("Fair Value per share", round(fair_value,2))
    dcf_columns2[0].write("*All in millions except per shares amounts.")
    st.markdown("#")


