#!/usr/bin/env python
# coding: utf-8

# This application is for the solution of the test which is about analyzing lse ftse50 dataset. I have put all the comments starting with "#" on those expression, which can be uncommented to see the results. Please run to code to execute each cell. The interactive charts are saved as html and will be sent along. They will not work on static python html file. The code to download the dataset creating in this application is provided in the last cells.
# 
# Answer to question 3b. If I will have a more time, I would like to do some general prediction on this data to know how future index will. Moreover, I would like to create a javascript application based on that. Using dc.js, I would like to create an interactive application and visual summary of this data as also shown on this site. https://dc-js.github.io/dc.js/.

# First step is to import all packages to be used

# In[71]:


import datetime
import pandas_datareader.data as wb
import pandas as pd
import numpy as np
import seaborn as sns #visualisation
import holoviews as hv
from holoviews import opts, dim
hv.extension('bokeh')
import panel as pn
import panel.widgets as pnw
import hvplot.pandas #noqa
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import matplotlib


# Then get ticker data spredsheet

# In[2]:


ticker_data = "ftse50lse.csv"
df_ticker = pd.read_csv(ticker_data)
tick = df_ticker.Ticker


# Read data from yahoo finance and converting to pandas dataframe

# In[3]:


p = wb.DataReader(tick, 'yahoo','2017-9-19','2021-9-01')


# See overview of the downloaded data

# In[92]:


p.axes


# We are only interested in closing prices

# In[5]:


df_close =p['Adj Close']


# In[93]:


#len(p["Adj Close"]) #check the length of the data. returns number of rows


# Functions to see the null values

# In[94]:


print(df_close.isnull().values.any()) # returns true if there are null values in the dataframe
print(df_close.isnull().values.sum()) # returns total count of null values
#print(df_close.isnull().sum()) # returns count of null values with column numbers


# Uncomment it and it will remove all the rows with the null values. Then I put it into a new dataframe.
# 
# Solution of 2(b)
# In this step, I have preserved columns (tickers) because the ratio of null value per column is very less.
# if column has more null values then in that case rows need to be preserved and columns need to be deleted.
# !A best practice normall all data scientists use. :)!

# In[8]:


df_clean=df_close.dropna()


# In[109]:


print(df_close.shape) # size of dataframe with null values
print(df_clean.shape) # size of dataframe without null values
print(df_clean.isnull().values.sum()) ## see no null values :)


# In[10]:


df_clean.head() # a sneek peek into the dataset


# This dataset do all big calculations. It returns FTSE50 Index and partial values for other indexes.

# In[11]:


#Function that gets values from ticker spreadsheet and returns them to following code
def get_shares(label):
    for index, row in df_ticker.iterrows():
          if label == row["Ticker"]:
            no_shares = row["Shares"]
            sector = row["Sector"]
            weight = row["Weight"]
    return(sector, weight, no_shares)

value = []
ind =[]
sector_indx = [] # storage of partially calculated stock indexes
weight_val = []
weight_indx=[]# “true” FTSE 50 Index level
ffa =[]
ffa_lst=[] # storage of partially calculated free float adjustment factor
for index, row in df_clean.iterrows():
    for i,j in row.items():
        sector, weight, no_shares = get_shares(i) 
        no_shares = int(no_shares.replace(",",""))
        val = j*no_shares*1
        value.append(val)
        weight = float(weight.replace("%",""))
        weight_val = j*weight
        ffa = weight_val/len(df_clean)
        ffa_lst.append([weight_val, index, i])
        sector_indx.append([sector, index, val])
    ind.append(sum(value)/len(df_clean))    
    weight_indx.append(sum(value))
    


# This is the FTSE50 Index that was asked at 1(c). In the last cell of this application, there is a code to download all these datasets.

# In[124]:


df_index = pd.DataFrame()
df_index = pd.DataFrame(zip(df_clean.index, ind), columns = ["date","index"])
print(df_index[0:10])


# This is sub indices for each sector as asked in 1d. The result is a multi index dataframe.

# In[125]:


df_sectorindx = pd.DataFrame(sector_indx,columns = ["sector","date","value"])
df_sectorindx=df_sectorindx[['date','sector',"value"]].groupby(['date', "sector","value"]).sum()/len(df_clean)
df_sectorindx.head()


# In[110]:


#print(len(weight_indx))


# In the following first there is the true FTSE50 Index that was asked in 3(a) then the free floating adjustment factor.

# In[126]:


df_wgt_index = pd.DataFrame(zip(df_clean.index, weight_indx), columns = ["date","index"])
print(df_wgt_index[0:10])
#This is free floating adjustment factor
df_ffa= pd.DataFrame(ffa_lst, columns = ["ffa","date","stock"])
df_ffa_gp=df_ffa.pivot_table(index ='date', columns =['stock'], values =['ffa']).reset_index()
#df_ffa_gp.head()


# Time series of main index as asked in 2a. It shows positive correlation. Over time indices has progressed.
# 

# In[127]:


df_index.hvplot.line(x="date", y="index") 


# Time series of sector index as asked in 2a. Suddenly finance sector dropped down after 3/2020. Consumer sector is growing up mid 2019.
# Health sector has progressed a lot from 2020 and is still high. It could be due to Corona.
# 

# In[128]:


df_sectorindx.hvplot.line(x = "date", y = "value", by ='sector')


# The same Time series of sector index as above but with more fine view and controls. The following code will save the chart as html for sharing or offline use.
# 
# 

# In[129]:


df_sectorindx.hvplot.line(x = "date", y = "value", groupby ='sector')
plt_sectorindx = df_sectorindx.hvplot.line(x = "date", y = "value", groupby ='sector')
hv.save(plt_sectorindx, 'plt_sectorindx.html', backend='bokeh')


# Convert multiindex dataframe to single index for ease of use and visualise in next questions
# 

# In[130]:


df_sector = df_sectorindx.reset_index()
print(df_sector)


# Which sector performed better in the last 18 months? Question from 2b. 
# 
# The health sector is best performing with some exception to consumer. 
# The worst is Finance as it was higher before and now it is down. Retail on the other hand was always low.
# 

# In[131]:


end_date=df_sector["date"].max()
#print(end_date)
eighteen_m_ago = end_date - relativedelta(months=18) # date 18 months ago
#print(eighteen_m_ago)

#create a dataframe from this condition
df_eighteen_sector = df_sector[(df_sector["date"] >= eighteen_m_ago) & (df_sector["date"] <= end_date)]
#df_eighteen_sector.head()

#visualize it
df_eighteen_sector.hvplot.line(x = "date", y = "value", by ='sector')


# The same Time series of sector index as above but with more fine view and controls. Also in the following code will save the chart as html.
# 

# In[132]:


df_eighteen_sector.hvplot.line(x = "date", y = "value", groupby ='sector')
# The following code will save the chart as html
plt_eighteen_sector = df_eighteen_sector.hvplot.line(x = "date", y = "value", groupby ='sector')
hv.save(plt_eighteen_sector, 'plt_eighteen_sector.html', backend='bokeh')


# An interactive chart showing values for different years and sector. The code to save chart as html is also included in the following.

# In[133]:


df_eighteen_sector.hvplot.bar(x = "date.month" , y = "value", groupby=['date.year', 'sector'] )


# Solution of 2c, calculation of rolling average and sd. Then creating a dataframe from them.
# 

# In[134]:


# The following code will save the chart as html
plt_eighteen_sector_bar = df_eighteen_sector.hvplot.bar(x = "date.month" , y = "value", groupby=['date.year', 'sector'] )
hv.save(plt_eighteen_sector_bar, 'plt_eighteen_sector_bar.html', backend='bokeh')


# In[135]:


#Rolling average for both indices
avg_indx_1 = df_index["index"].rolling(window=30).mean()
avg_indx_3 = df_index["index"].rolling(window=90).mean()
avg_indx_6 = df_index["index"].rolling(window=120).mean()
avg_sec_1 = df_sector["value"].rolling(window=30).mean()
avg_sec_3 = df_sector["value"].rolling(window=90).mean()
avg_sec_6 = df_sector["value"].rolling(window=120).mean()


# In[136]:


#standard deviation for both indices
sd_indx_1 = df_index["index"].rolling(window=30).std()
sd_indx_3 = df_index["index"].rolling(window=90).std()
sd_indx_6 = df_index["index"].rolling(window=120).std()
sd_sec_1 = df_sector["value"].rolling(window=30).std()
sd_sec_3 = df_sector["value"].rolling(window=90).std()
sd_sec_6 = df_sector["value"].rolling(window=120).std()


# In[137]:


#putting the above values in dataframe
df_avg=pd.DataFrame(zip(avg_sec_1,avg_sec_3,avg_sec_6), columns=["roll_avg_1","roll_avg_3","roll_avg_6"])
df_avg.head()
df_sd=pd.DataFrame(zip(sd_sec_1,sd_sec_3,sd_sec_6), columns=["sd_1","sd_3","sd_6"])
df_sd.head()
# remove na values
df_avg= df_avg.dropna()
df_sd= df_sd.dropna()


# To change the date format for creating visualizations.

# In[142]:


df_eighteen_sector['date'] = df_eighteen_sector["date"].dt.strftime("%m/%y")
print(df_eighteen_sector['date'])


# Overview chart of performance of different sectors from last 18 months.

# In[139]:


plt.figure(figsize=[20,7])
sns.barplot(x='date', y='value',  hue = "sector", data=df_eighteen_sector)


# Solution to answer 2c for rolling average. Overlay chart is shown below.
# 

# In[140]:


bar = plt.figure(figsize=[30,5])
bar=sns.barplot(x='date', y='value',  hue = "sector", data=df_eighteen_sector)
bar.tick_params(axis='y')
line=bar.twiny()
line=sns.lineplot( data=df_avg, sort=False, linewidth = 0.3)
line.tick_params(axis='y')
plt.show()


# Solution to answer 2c for standard deviation. Overlay chart is shown below.

# In[141]:


# solution to answer 2c for sd
bar = plt.figure(figsize=[30,5])
bar=sns.barplot(x='date', y='value',  hue = "sector", data=df_eighteen_sector)
bar.tick_params(axis='y')
line=bar.twiny()
line=sns.lineplot( data=df_sd, sort=False, linewidth = 0.3)
line.tick_params(axis='y')
plt.show()


# In[ ]:


# download files from all the above created datasets
df_index.to_csv("ftseindex.csv")
df_sectorindx.to_csv("sectorindex.csv")
df_wgt_indx.to_csv("wgt_indx.csv")
df_ffa_gp.to_csv("ffa.csv")

