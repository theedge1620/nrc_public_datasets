#! python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 15:40:54 2017

@author: JBC4

This program scrapes the NRC public webpage for Generic Communications

"""

import requests, bs4, re
import pandas as pd

NRCproxies = { 
        'http': 'http://148.184.186.50:80',
        'https': 'http://148.184.186.50:80',
}


# find all the IN references in a page
regwebAddress = 'https://www.nrc.gov/reading-rm/doc-collections/gen-comm/info-notices/'
mlWebString = 'https://www.nrc.gov/docs/'

df = pd.DataFrame()

years = list(range(1979,2020))

for i in range(0, len(years)):
    
    # read html table from site:
    df_list=pd.read_html(regwebAddress+str(years[i])+'/')
    dfToAppend = df_list[1]
    
    # remove junk columns and top row and synch column names:
    del dfToAppend[2]
    del dfToAppend[4]
    dfToAppend = dfToAppend.drop(dfToAppend.index[0]) # Drop titles row
    dfToAppend = dfToAppend.reset_index(drop=True)  # reset row indices
    dfToAppend['Link']=""
    dfToAppend.rename(columns = {0:'Number', 1:'Title', 
                              3:'Date'}, inplace = True)
    
    # Get ML numbers and hyperlinks:
    res = requests.get(regwebAddress+str(years[i])+'/',proxies=NRCproxies)
    res.raise_for_status()
    gcSoup = bs4.BeautifulSoup(res.text, "lxml")
    
    if years[i] == 2002:
        table = gcSoup.find('table',{'summary':'NRC Information Notices: xxxx Index'})
    else:
        table = gcSoup.find('table',{'summary':'NRC Information Notices: ' +str(years[i])+' Index'})
    
    tableRows = table.find_all('tr')
    inRegex = re.compile(r'IN-\d\d-\d+\s\w+.*\s--\s.*')

    for j in range(1,len(tableRows)):  # for each table row (except title row)
        tableRowString=str(tableRows[j])  
        
        for k in range(0,len(dfToAppend['Number'])):  # for each IN number
            testString = dfToAppend['Number'][k]
            if testString in tableRowString:  #if you find it
                linkSoup = bs4.BeautifulSoup(tableRowString,"lxml")
                inLink = linkSoup.find_all('a',href=True)
                if inLink:  # if there's a link, use it
                    if years[i]==1990:  #1990 links are different than others
                        dfToAppend['Link'][k]='https://www.nrc.gov/reading-rm/doc-collections/gen-comm/info-notices/1990/'+inLink[0].attrs['href']
                    elif testString =='IN-85-11':  # IN 85-11 is linked wrong on site
                        dfToAppend['Link'][k]='https://www.nrc.gov/reading-rm/doc-collections/gen-comm/info-notices/1985/'+inLink[0].attrs['href']
          
                    else:
                        dfToAppend['Link'][k]='https://www.nrc.gov'+inLink[0].attrs['href']
                else:    # if not, use the general table link
                    dfToAppend['Link'][k]=regwebAddress+str(years[i])+'/'
                
    #  append dataframes
    if i ==0:
        df = dfToAppend
    else:
        df = df.append(dfToAppend,ignore_index=True)


# drop rows with junk titles "--"
df = df[~df['Number'].str.contains('--')]        
df.to_excel("Information Notices - Scraped from Public Site.xlsx")  
