import quandl as q
import pandas as pd
import numpy as np
import os

#
# Still WIP
#
# Completed Sheets
#
#           Raw Data dump by two periods
#           Pivot example by sector
#           Top 50 holdings on current period
#
# To-do
#
#           New securities purchase for current period 
#           What has been sold - based on Value differences in both and just in in previous
#           Eventually pass in a Investor name and period dates - so can hook up to a UI

# GET and SET Key using EXPORT on Shell
q.ApiConfig.api_key=os.environ.get("quandl_key")

# for full list see getInstitutionalDetails.py
ins_dim = 'DIMENSIONAL FUND ADVISORS LP'
ins_bw = 'BRIDGEWATER ASSOCIATES LP, DIMENSIONAL FUND ADVISORS LP'
ins_aqr = 'AQR CAPITAL MANAGEMENT LLC'

# Set Institution
institution = ins_aqr

current_dataset = '2018-09-30'
current_file = institution + '#' + current_dataset + '.csv'
previous_dataset = '2018-06-30'
previous_file = institution + '#' + previous_dataset + '.csv'

current_data  = q.get_table('SHARADAR/SF3',  calendardate= current_dataset, investorname= institution)
previous_data = q.get_table('SHARADAR/SF3',  calendardate= previous_dataset, investorname= institution)

current_data.to_csv(current_file)
previous_data.to_csv(previous_file)

# Now we are going to merge the two dataframes

merged_file = institution + '#' + previous_dataset + 'MERGED WITH' + current_dataset + '.xlsx'
merged_data = current_data.merge(previous_data.drop_duplicates(), on=['ticker'], how='outer', indicator=True)

# We will also need to add a couple of fields based on left/right nulls so we have a consolidated value and issue details (some of the securities cannot be located)
merged_data['consolidated_value'] = np.where(merged_data['value_x'].isnull(), merged_data['value_y'], merged_data['value_x'])
merged_data['activity_flag'] = np.where(merged_data['value_x'] >  merged_data['value_y'], 'Purchase','Sell')

# TO-DO - Fix LEFT = Current Period, Right = Previous Period.  Make easier to read.

# Now merge with security details if they exist
ticker_data  = q.get_table('SHARADAR/TICKERS')
complete_data = merged_data.merge(ticker_data, on=['ticker'], how='left')

Pivot_ByMergeSector = pd.pivot_table(complete_data,index=["sector"],columns=["_merge"],values=["consolidated_value"],aggfunc=[np.sum])

top50_data = complete_data.nlargest(50, 'consolidated_value')

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(merged_file, engine='xlsxwriter')

# Write each dataframe to a different worksheet.
complete_data.to_excel(writer, sheet_name='Raw')
Pivot_ByMergeSector.to_excel(writer, sheet_name='Periods_By_Sector')
top50_data.to_excel(writer, sheet_name='Top50')

writer.save()
