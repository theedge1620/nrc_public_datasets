#! python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  5 15:40:54 2017

@author: JBC4

This program scrapes the NRC public webpage for Regulatory Issue Summaries
Note:  Currently, only the initial revision is contained until code to capture
revisions from tables are developed (last updated - 02/12/2017)

"""

import requests, bs4, re
import pandas as pd

NRCproxies = { 
        'http': 'http://148.184.186.50:80',
        'https': 'http://148.184.186.50:80',
}


# find all the IN references in a page
regwebAddress = 'https://www.nrc.gov/reading-rm/doc-collections/gen-comm/reg-issues/'
mlWebString = 'https://www.nrc.gov/docs/'

df = pd.DataFrame()

years = list(range(1999,2020))

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
    
    if years[i] == 1900:  # if loop for exceptions
        table = gcSoup.find('table',{'summary':'Regulatory Issue Summaries - xxxx Index'})
    else:
        table = gcSoup.find('table',{'summary':'Regulatory Issue Summaries - ' +str(years[i])})
    
    tableRows = table.find_all('tr')
    inRegex = re.compile(r'RIS-\d\d-\d+\s\w+.*\s--\s.*')

    for j in range(1,len(tableRows)):  # for each table row (except title row)
        tableRowString=str(tableRows[j])  
        
        for k in range(0,len(dfToAppend['Number'])):  # for each IN number
            testString = dfToAppend['Number'][k]
            if pd.isna(testString):
                testString = 'xxxxNoRECORDINTABLE'
            if testString in tableRowString:  #if you find it
                linkSoup = bs4.BeautifulSoup(tableRowString,"lxml")
                inLink = linkSoup.find_all('a',href=True)
                if inLink:  # if there's a link, use it
                    if years[i]==1900:  #exception year links are different than others
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
#df = df[~df['Number'].str.contains("")]        
        
df = df.dropna()        
df.to_excel("Regulatory Issue Summaries - Scraped from Public Site.xlsx")  
