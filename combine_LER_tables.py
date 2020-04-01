# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 21:04:47 2020

@author: Katy
"""

import pandas as pd

# Read first file:

current_df = pd.read_excel("./data/LERSearchResults1991.xlsx")
# Read and append the rest:
for i in range(1992,2020):
    update_df = pd.read_excel("./data/LERSearchResults"+str(i)+".xlsx")
    current_df = pd.concat([current_df, update_df])
    
# Write the appended dataframe to an excel file
# Add index=False parameter to not include row numbers
current_df.to_excel("/data/all_LERs.xlsx", index=False)