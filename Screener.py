### Libraries
import statistics
import requests
from bs4 import BeautifulSoup
import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

def calculate_intrinsic_value_PE(cost_of_capital, RoCE, growth_high, high_growth_period, fade_period, terminal_growth_rate, tax_rate):
    # Initialize variables
    
    cost_of_capital = cost_of_capital/100
    RoCE = RoCE/100
    growth_high = growth_high/100
    terminal_growth_rate = terminal_growth_rate/100

    
    intrinsic_value = 0
    EPS = RoCE * (1 - tax_rate)

    # Calculate present value of high growth period earnings
    for year in range(1, high_growth_period + 1):
        EPS *= (1 + growth_high)
        present_value = EPS / ((1 + cost_of_capital) ** year)
        intrinsic_value += present_value

    # Calculate present value of fade period earnings
    EPS *= (1 + growth_high) ** fade_period
    for year in range(high_growth_period + 1, high_growth_period + fade_period + 1):
        EPS *= (1 + terminal_growth_rate)
        present_value = EPS / ((1 + cost_of_capital) ** year)
        intrinsic_value += present_value

    # Calculate terminal value
    terminal_value = EPS * (1 + terminal_growth_rate) / (cost_of_capital - terminal_growth_rate)
    terminal_value_discounted = terminal_value / ((1 + cost_of_capital) ** (high_growth_period + fade_period))

    # Add terminal value to intrinsic value
    intrinsic_value += terminal_value_discounted
    
    print("Intrinsic val: ",intrinsic_value)

    return intrinsic_value


def scraper(token):
  url = f"https://www.screener.in/company/{token}/consolidated" 

  r = requests.get(url)

  htmlContent = r.content
  soup = BeautifulSoup(htmlContent, 'html.parser')
  
  price = soup.find_all('span')
  l = len(price[5].text.strip())

  if l == 1:
      url = f"https://www.screener.in/company/{token}/"

  else:
      url = f"https://www.screener.in/company/{token}/consolidated" 

  r = requests.get(url)

  htmlContent = r.content
  soup = BeautifulSoup(htmlContent, 'html.parser')
  title = soup.title

  

  #Find FY23 PE
  pe_ratio_element = soup.find("li", class_="flex flex-space-between", attrs={"data-source": "default"})

  mcap = pe_ratio_element.find("span", class_="number")
  #print(mcap)
  mcap = float(mcap.text.replace(',',''))
  fy23_net_profit = soup.find_all('tr', class_="strong")
  Np = fy23_net_profit[5]

  #print(len(Np))
  #Np = float(Np.find_all('td', class_='')[11].text.replace(',',''))
  Np = Np.find_all('td',class_='') 
  Np = float(Np[len(Np) - 2].text.replace(',',''))

  #print("Np length:",len(Np))
  fy23_PE = round(mcap/Np,2)
  #fy23_P_E

  anchors = soup.find_all('a')
  stocks = soup.find_all('li', class_="flex flex-space-between")
  #print(stocks)

  stock_data = {}

  for stock in stocks:
      pe_ratio = stock.find('span', class_="name").text
      if 'Stock P/E' in pe_ratio:
          P_E = float(stock.find('span', class_ ="nowrap value").text.strip())
          stock_data['Stock_PE'] = P_E
      
  
  soc = soup.find_all('tr', class_='')
  ROCE = []
  for s in soc[38].find_all('td', class_= ''):
      if s.text == '':
          s.text.replace('', '0%')
      else:
          ROCE.append(int(s.text.replace('%','')))
  del ROCE[-1]

  if len(ROCE)<5:
      ROCE = ROCE[-1]
  else:
      ROCE = statistics.median(ROCE[-5:]) 


  stock_data['ROCE'] = ROCE

  stock_data['FY23_PE'] = fy23_PE

  #print('Stocks P/E', P_E, '\n', 'ROCE', ROCE)

  growth = soup.find_all('table', class_="ranges-table")
  #growth_tables_headers = growth.

  keyList = ["10yrs", "5yrs", "3yrs","TTM"]
  sales_dict = {}
  profit_dict = {}

  for i in keyList:
    sales_dict[i] = None
    profit_dict[i] = None

  for table in growth:
    table_header = table.find("th").text
    if table_header == "Compounded Profit Growth":
      cells = table.find_all("td")
      for i in range(1,len(cells),2):

        #print("Cell val: ",cells[i].text.strip().replace("%", ""))

        if cells[i].text.strip().replace("%", ""):
          if i == 1:
            profit_dict['10yrs'] = float(cells[i].text.strip().replace("%", ""))
          if i == 3:
            profit_dict['5yrs'] = float(cells[i].text.strip().replace("%", ""))
          if i == 5:
            profit_dict['3yrs'] = float(cells[i].text.strip().replace("%", ""))
          if i == 7:
            profit_dict['TTM'] = float(cells[i].text.strip().replace("%", ""))
            
        else:
          if i == 1:
            profit_dict['10yrs'] = 0
          if i == 3:
            profit_dict['5yrs'] = 0
          if i == 5:
            profit_dict['3yrs'] = 0
          if i == 7:
            profit_dict['TTM'] = 0

    if table_header == "Compounded Sales Growth":
      cells = table.find_all("td")
      for i in range(1,len(cells),2):

        #print("Cell val: ",cells[i].text.strip().replace("%", ""))

        if cells[i].text.strip().replace("%", ""):
          if i == 1:
            sales_dict['10yrs'] = float(cells[i].text.strip().replace("%", ""))
          if i == 3:
            sales_dict['5yrs'] = float(cells[i].text.strip().replace("%", ""))
          if i == 5:
            sales_dict['3yrs'] = float(cells[i].text.strip().replace("%", ""))
          if i == 7:
            sales_dict['TTM'] = float(cells[i].text.strip().replace("%", ""))
            
        else:
          if i == 1:
            sales_dict['10yrs'] = 0
          if i == 3:
            sales_dict['5yrs'] = 0
          if i == 5:
            sales_dict['3yrs'] = 0
          if i == 7:
            sales_dict['TTM'] = 0


    #print(sales_dict)
  return stock_data, sales_dict, profit_dict 

#a = scraper("MARUTI")

#for key in set(list(res[1].keys()) + list(res[2].keys())):
# print("Combined Table: ",combinedTable)
# print("Combined Table keys: ",list(combinedTable.keys()))
# print("Combined Table values: ",list(combinedTable.values()))




container_intro = st.container(border=True)
with container_intro:
  st.title("VALUING CONSISTENT COMPOUNDERS")
  #st.write(combinedTable)
  st.write("Hi there!")
  st.write("This page will help you calculate intrinsic PE of consistent compounders through growth-RoCE DCF model.")
  st.write("We then compare this with current PE of the stock to calculate degree of overvaluation.")
  #st.write("NSE/BSE symbol")
  token = st.text_input("NSE/BSE symbol", value = "NESTLEIND")

res = scraper(token)

# keyList = set(list(res[1].keys()) + list(res[2].keys()))
# print("KEYLIST: ",keyList)

combinedTable = {}

for key in list(res[1].keys()):

    print("KEY: ",key)
    
    try:
        combinedTable.setdefault(key,[]).append(res[1][key])        
    except KeyError:
        pass

    try:
        combinedTable.setdefault(key,[]).append(res[2][key])          
    except KeyError:
        pass
  #st.write(res)

tableCol1 = {"":["Sales Growth","Profit Growth"]}
tableCol1.update(combinedTable)

tab = go.Figure(data=[go.Table(
  columnwidth = [50,50],
  header=dict(
    values=list(tableCol1.keys()),
    align = "right"),
  cells=dict(
    values=list(tableCol1.values()),
    align = "right"))
    ])
tab.update_layout(height=80, margin=dict(r=100, l=5, t=5, b=5), width= 725)


container_sliders = st.container(border = True)
with container_sliders:
  coc = st.slider('Cost of Capital (CoC): %', 8,16, step=1)
  roce = st.slider('Return on Capital Employed (RoCE): %', 10,100,10)
  growth_high = st.slider('Growth during high growth period: $',8,20,2)
  high_growth_period = st.slider("High growth period(years)", 10,25,2)
  fade_period = st.slider('Fade Period (years)',5,20,5)
  terminal_growth_rate = st.slider("Terminal Growth Rate (%)",0,8,1)

intrinsicPE = calculate_intrinsic_value_PE(coc,roce,growth_high,high_growth_period,fade_period,terminal_growth_rate,0.25)

degOvereval = 0

if  res[0]['Stock_PE'] <= res[0]['FY23_PE']:
  degOvereval = (res[0]['Stock_PE']/intrinsicPE) - 1
else:
  degOvereval = (res[0]['FY23_PE']/intrinsicPE) - 1


container_info = st.container(border = True)
with container_info:
  st.write(f"Stock Symbol: {token}")
  st.write(f"Current PE: {res[0]['Stock_PE']}")
  st.write(f"FY23 PE: {res[0]['FY23_PE']}")
  st.write(f"5-Yr Median pre-tax RoCE: {res[0]['ROCE']}")

container_tab = st.container(border = True)
with container_tab:
  st.write(tab)


fig_Sales = go.Figure(go.Bar(
            x=list(res[1].values()),
            y=list(res[1].keys()),
            orientation='h',
            dx=5))

fig_Sales.update_layout(
  xaxis_title = "Percentage",
  yaxis_title = "Time Period",
  width=300,
  height=500
)

#fig_Sales = px.bar(res[1],x = list(res[1].values()), y = list(res[1].keys()),width = 10)  

#st.write(fig_Sales)            

#col1, col2 = st.columns(2, gap = "large")

fig_Profits = go.Figure(go.Bar(
            x=list(res[2].values()),
            y=list(res[2].keys()),
            orientation='h'))
fig_Profits.update_layout(
  xaxis_title = "Percentage",
  yaxis_title = "Time Period",
  width=300,
  height=500
)

# fig_Profits.update_xaxes(
#   autorange = 
# )

#fig_Profits = st.bar_chart(x = list(res[2].values()), y = list(res[2].keys()),width = 10)



#st.write(fig)                     

container_charts = st.container(border = True)
with container_charts:
  container_charts_col1, container_charts_col2 = container_charts.columns(2, gap = "large")
  container_charts_col1.write(fig_Sales)
  container_charts_col2.write(fig_Profits)

container_final = st.container(border = True)
with container_final:
  st.write("Play with inputs to see changes in intrinsic PE and overvaluation:")
  st.write(f"The calculated intrinsic PE is: {round(intrinsicPE,2)}")
  st.write(f"Degree of overevaluation: {round(degOvereval*100,2)} %")
#col1, col3 = st.columns([10, 10], gap = "large")

