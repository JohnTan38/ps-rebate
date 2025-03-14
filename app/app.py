import streamlit as st
import pandas as pd
import numpy as np
import math,re
from datetime import datetime
#import win32com.client
import glob, os, openpyxl, re
#import pythoncom
import seaborn as sns
import matplotlib.pyplot as plt 
import warnings
warnings.filterwarnings("ignore")

import datetime as datetime

#import smtplib, email, ssl
#from email import encoders
#from email.mime.base import MIMEBase
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText

st.set_page_config('PS Rebates', page_icon="🏛️", layout='wide')
def title(url):
     st.markdown(f'<p style="color:#2f0d86;font-size:22px;border-radius:2%;"><br><br><br>{url}</p>', unsafe_allow_html=True)
def title_main(url):
     st.markdown(f'<h1 style="color:#230c6e;font-size:42px;border-radius:2%;"><br>{url}</h1>', unsafe_allow_html=True)

def success_df(html_str):
    html_str = f"""
        <p style='background-color:#baffc9;
        color: #313131;
        font-size: 15px;
        border-radius:5px;
        padding-left: 12px;
        padding-top: 10px;
        padding-bottom: 12px;
        line-height: 18px;
        border-color: #03396c;
        text-align: left;'>
        {html_str}</style>
        <br></p>"""
    st.markdown(html_str, unsafe_allow_html=True)


def process_dataframe(df_data):
    # Function to extract number after last whitespace
    def extract_number(s):
        # Check if the input is string
        if isinstance(s, str):
            try:
                
                return np.float64(re.findall(r'\b\d+\b', s)[-1])
            except (IndexError, ValueError):
                return np.float64(0)
        else:
            return np.float64(0)

    df_data['USED'] = 0

    # Check each column
    for col in df_data.columns:
        try:
            # If the column header is a datetime
            datetime.strptime(str(col), '%Y-%m-%d %H:%M:%S')
            # Apply the function to each element in the column
            df_data['USED'] += df_data[col].apply(extract_number)
        except ValueError:
            continue
            
        df_data['BAL'] = df_data['INITIAL QTY'] - df_data['USED']
        df_data['COST'] = df_data['UNIT $']* df_data['USED']
        df_data['STATUS'] = df_data['BAL'].apply(lambda x: 'REORDER' if x < 5 else 'HEALTHY')

    return df_data

def select_reorder(df):
    return df[df['STATUS'] == 'REORDER']

title_main('PS Rebates')
#pythoncom.CoInitialize() 

st.sidebar.header("Line graph")
lst_num_week = st.sidebar.multiselect('Select number of weeks to plot', [5,6,7,8,9,10], placeholder='Choose 1', 
                          max_selections=2)
if st.sidebar.button('Confirm weeks'):
    if lst_num_week is not None:
        st.sidebar.write(f'Selected weeks: {lst_num_week[0]}')
        num_week = lst_num_week[0]
    else:
        st.sidebar.write('please select number of weeks')
#if usr_name is not None:
    #if st.sidebar.button('Confirm Username'):
            #usr_email = usr_name[0]+ '@sh-cogent.com.sg' #your outlook email address
            #st.sidebar.write(f'User email: {usr_email}')
            #outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI") 
def user_email(usr_name):
    usr_email = usr_name[0] + '@sh-cogent.com.sg'
    return usr_email

dataUpload = st.file_uploader("Upload your DCON and Week xlsx files", type="xlsx", accept_multiple_files=True)
if dataUpload is None:
        st.text("Please upload a file")
elif dataUpload is not None:
        for i in range(len(dataUpload)):
            if dataUpload[i].name in 'Week.xlsx':
                haulier_original_0 = pd.read_excel(dataUpload[i], sheet_name='Week', engine='openpyxl')
                haulier_00 = haulier_original_0[['Container Number', 'Size, Type', 'Carrier Name', 'Carrier Voyage', 'Event Type','Event Time']]

                haulier_00.rename(columns = {'Container Number': 'Container_Number', 'Carrier Name': 'Carrier_Name', 'Carrier Voyage': 'Carrier_Voyage', 
                            'Size, Type': 'Size', 'Event Type': 'Event_Type', 'Event Time': 'Event_Time'}, inplace = True)
                haulier_00.sort_values(['Event_Time', 'Carrier_Name'], ascending=[True, False], inplace=True)
                haulier_0 = haulier_00.copy()
            elif dataUpload[i].name in 'DCON.xlsx':
                dcon_original = pd.read_excel(dataUpload[i], sheet_name='DCON', engine='openpyxl')
                dcon_0 = dcon_original[['Container', 'Discharger Abbreviated Vessel', 'Discharger Abbreviated Voyage', 'Discharger Berthing Time', 'Discharge Time', 
                        'Loader Abbreviated Vessel', 'Loader Abbreviated Voyage', 'Loader Berthing Time', 'Load Time']]
                def rename_specific_cols(df, col_to_rename, new_col):
    
                    column_mapping = {col: new_col for col in col_to_rename}
                    df_rename_col = df.rename(columns=column_mapping)
                    return df_rename_col
                dcon_1 = rename_specific_cols(dcon_0.copy(), ['Discharger Abbreviated Vessel', 'Loader Abbreviated Vessel'], 'Carrier_Name')
                dcon_2 = rename_specific_cols(dcon_1, ['Discharger Abbreviated Voyage', 'Loader Abbreviated Voyage'], 'Carrier_Voyage')

                dcon_2.rename(columns={'Container': 'Container_Number', 'Discharger Berthing Time': 'Berth_Time', 'Discharge Time': 'Discharge_Time', 
                       'Loader Berthing Time': 'Berth_Time', 'Load Time': 'Load_Time'}, inplace=True)
                def format_time(df, col1,col2):
                    df[col1] = df[col1].astype(str).str.replace('-','')
                    df[col2] = df[col2].astype(str).str.replace('-','')
                    return df
                dcon_3=format_time(dcon_2, 'Discharge_Time', 'Load_Time')

                def rename_duplicate_columns(df):
                    cols = pd.Series(df.columns)
                    for dup in cols[cols.duplicated()].unique(): 
                        cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
                    df.columns = cols
                    return df

                dcon = rename_duplicate_columns(dcon_3)

        #append 'Discharge_Time', 'Load_Time' to haulier dataframe 20240706 works great!
        def append_columns_2(df_dcon, df_haulier):
            # First, merge based on 'Carrier_Name' & 'Carrier_Voyage'
            df_merged = pd.merge(df_haulier, df_dcon[['Carrier_Name', 'Carrier_Voyage', 'Discharge_Time', 'Load_Time']], 
                            on=['Carrier_Name', 'Carrier_Voyage'], how='left')

            # Then, merge based on 'Carrier_Name_1' & 'Carrier_Voyage_1'
            df_merged = pd.merge(df_merged, df_dcon[['Carrier_Name_1', 'Carrier_Voyage_1', 'Discharge_Time', 'Load_Time']], 
                            left_on=['Carrier_Name', 'Carrier_Voyage'], right_on=['Carrier_Name_1', 'Carrier_Voyage_1'], 
                            how='left', suffixes=('', '_1'))

            # If 'Discharge_Time' and 'Load_Time' are NaN, fill them with the values from the second merge
            df_merged['Discharge_Time'].fillna(df_merged['Discharge_Time_1'], inplace=True)
            df_merged['Load_Time'].fillna(df_merged['Load_Time_1'], inplace=True)
            # Drop the unnecessary columns
            df_merged.drop(columns=['Carrier_Name_1', 'Carrier_Voyage_1', 'Discharge_Time_1', 'Load_Time_1'], inplace=True)
            return df_merged
        
        def calculate_time_difference(df):
            df['Event_Time'] = pd.to_datetime(df['Event_Time']) # Convert the time columns to datetime
            df['Discharge_Time'] = pd.to_datetime(df['Discharge_Time'])
            df['Load_Time'] = pd.to_datetime(df['Load_Time'])

            df['Time_Difference'] = np.nan # Initialize a new column 'Time_Difference' with NaN values

            # Calculate 'Time_Difference' for rows where 'Event_Type' is 'EXIT'
            df.loc[df['Event_Type'] == 'EXIT', 'Time_Difference'] = (df['Event_Time'] - df['Discharge_Time']).dt.total_seconds() / 60

            # Calculate 'Time_Difference' for rows where 'Event_Type' is 'ENTRY'
            df.loc[df['Event_Type'] == 'ENTRY', 'Time_Difference'] = (df['Load_Time'] - df['Event_Time']).dt.total_seconds() / 60
    
            df['PSA_Rebate'] = np.nan # Initialize a new column 'PSA_Rebate' with NaN values

            # Assign 'PSA_Rebate' based on 'Time_Difference'
            df.loc[df['Time_Difference'] < 24*60, 'PSA_Rebate'] = 1
            df.loc[(df['Time_Difference'] >= 24*60) & (df['Time_Difference'] < 48*60), 'PSA_Rebate'] = 2

            return df

        #def send_email_psa_reabte(df,usr_email):
            #usr_email = user_email(usr_name)
            #email_receiver = usr_email
            #email_receiver = st.multiselect('Select one email', ['john.tan@sh-cogent.com.sg', 'vieming@yahoo.com'])
            #email_sender = "john.tan@sh-cogent.com.sg"
            #email_password = "" #st.secrets["password"]

            #body = """
                #<html>
                #<head>
                #<title>Dear User</title>
                #</head>
                #<body>
                #<p style="color: blue;font-size:25px;">PSA Rebate ($) offpeak/peak.</strong><br></p>

                #</body>
                #</html>

                #"""+ df.to_html() +"""
        
                #<br>This message is computer generated. """+ datetime.now().strftime("%Y%m%d %H:%M:%S")

            #mailserver = smtplib.SMTP('smtp.office365.com',587)
            #mailserver.ehlo()
            #mailserver.starttls()
            #mailserver.login(email_sender, email_password)
       
            #try:
                #if email_receiver is not None:
                    #try:
                        #rgx = r'^([^@]+)@[^@]+$'
                        #matchObj = re.search(rgx, email_receiver)
                        #if not matchObj is None:
                            #usr = matchObj.group(1)
                    
                    #except:
                        #pass

                #msg = MIMEMultipart()
                #msg['From'] = email_sender
                #msg['To'] = email_receiver
                #msg['Subject'] = 'PSA Rebate Summary '+ datetime.today().strftime("%Y%m%d %H:%M")
                #msg['Cc'] = 'john.tan@sh-cogent.com.sg'
        
                #msg.attach(MIMEText(body, 'html'))
                #text = msg.as_string()

                #with smtplib.SMTP("smtp.office365.com", 587) as server:
                    #server.ehlo()
                    #server.starttls()
                    #server.login(email_sender, email_password)
                    #server.sendmail(email_sender, email_receiver, text)
                    #server.quit()
                #st.success(f"Email sent to {email_receiver} 💌 🚀")
                #success_df(f"Email sent to {email_receiver} 💌 🚀")
            #except Exception as e:
                #st.error(f"Email not sent: {e}")


        if st.button('Lets get rebates'):
            #st.dataframe(data_new)
            st.divider()
            psa_rebate_indicator = calculate_time_difference(append_columns_2(dcon,haulier_0).dropna(subset=['Container_Number']))
            #rebate = data_new.copy()
            from datetime import datetime

            #public_holidays = ['2024-01-01', '2024-02-10', '2024-02-11', '2024-05-01', '2024-05-23', '2024-05-24', '2024-08-09', 
                   #'2024-10-25', '2024-12-25'] 
            df_public_holidays = pd.read_excel("https://raw.githubusercontent.com/JohnTan38/Project-Income/main/public_holidays.xlsx", sheet_name='public_holidays', 
                                                engine='openpyxl')
            public_holidays = df_public_holidays['public_holidays'].tolist() # Define the public holidays in Singapore

            def extract_numeric(df):
                df['Size'] = df['Size'].str.extract('(\\d+)', expand=False)  # Use regular expression to extract numeric part of 'Size' column
                return df

            def add_offpeak_columns(df_rebate):
                df_rebate['Event_Time'] = pd.to_datetime(df_rebate['Event_Time'], format='%Y-%m-%d %H:%M:%S') # Convert the 'Event_Time' column to datetime

                # Initialize the 'Offpeak_24' and 'Offpeak_48' columns with 0
                df_rebate['Offpeak_24'] = 0
                df_rebate['Offpeak_48'] = 0

                # Iterate over the rows of the DataFrame
                for i, row in df_rebate.iterrows():
                    # Check if the event time is a Sunday, a public holiday, or between 21:00 and 04:59
                    if row['Event_Time'].weekday() == 6 or row['Event_Time'].strftime('%Y-%m-%d') in public_holidays or (row['Event_Time'].hour >= 21 or row['Event_Time'].hour < 5):
                        # If 'PSA_Rebate' is 1, set 'Offpeak_24' to 1
                        if row['PSA_Rebate'] == 1:
                            df_rebate.at[i, 'Offpeak_24'] = 1
                        # If 'PSA_Rebate' is 2, set 'Offpeak_48' to 1
                        elif row['PSA_Rebate'] == 2:
                            df_rebate.at[i, 'Offpeak_48'] = 1
    
                extract_numeric(df_rebate)
                return df_rebate

            psa_offpeak_peak_rates = pd.read_csv(r"https://raw.githubusercontent.com/JohnTan38/Project-Income/main/psa_rebate.csv", index_col=0)

            #offpeak rebate
            offpeak_20_24 = psa_offpeak_peak_rates.iloc[0, psa_offpeak_peak_rates.columns.get_loc('offpeak_24')] #35
            offpeak_20_48 = psa_offpeak_peak_rates.iloc[0, psa_offpeak_peak_rates.columns.get_loc('offpeak_48')] #15
            offpeak_40_24 = psa_offpeak_peak_rates.iloc[1, psa_offpeak_peak_rates.columns.get_loc('offpeak_24')] #52.5
            offpeak_40_48 = psa_offpeak_peak_rates.iloc[1, psa_offpeak_peak_rates.columns.get_loc('offpeak_48')] #22.5
            
            #peak rebate
            peak_20_24 = psa_offpeak_peak_rates.iloc[0, psa_offpeak_peak_rates.columns.get_loc('peak_24')] #25
            peak_20_48 = psa_offpeak_peak_rates.iloc[0, psa_offpeak_peak_rates.columns.get_loc('peak_48')] #10
            peak_40_24 = psa_offpeak_peak_rates.iloc[1, psa_offpeak_peak_rates.columns.get_loc('peak_24')] #37.5
            peak_40_48 = psa_offpeak_peak_rates.iloc[1, psa_offpeak_peak_rates.columns.get_loc('peak_48')] #15
            
            #total rebate    
            def calculate_rebate(df):
                # Define a function to calculate rebate based on the conditions
                def rebate(row):
                    #if row['Offpeak_24'] == 1:
                        if row['Size'] == '20':
                            return offpeak_20_24 if row['Offpeak_24'] == 1 else offpeak_20_48 if row['Offpeak_48'] == 1 else 0
                        elif row['Size'] == '40':
                            return offpeak_40_24 if row['Offpeak_24'] == 1 else offpeak_40_48 if row['Offpeak_48'] == 1 else 0
            
                    #elif row['Nonpeak'] == 'No':
                        if row['Size'] == '20':
                            return peak_20_24 if row['Peak_24'] == 1 else peak_20_48 if row['Peak_48'] == 1 else 0
                        elif row['Size'] == '40':
                            return peak_40_24 if row['Peak_24'] == 1 else peak_40_48 if row['Peak_48'] == 1 else 0
                        else:
                            return 0

                # Apply the function to each row in the DataFrame to calculate the rebate
                df['Rebate'] = df.apply(rebate, axis=1)
                return df
            st.dataframe(calculate_rebate(add_offpeak_columns(psa_rebate_indicator)))
            st.divider()

            def count_occurrences(df_rebate):
                # Initialize a new DataFrame with the desired index and columns
                df_count = pd.DataFrame(index=['20', '40'], columns=['Offpeak_24', 'Offpeak_48'])

                # Count the occurrences and fill the new DataFrame
                for size in ['20', '40']:
                    for offpeak in ['Offpeak_24', 'Offpeak_48']:
                        df_count.at[size, offpeak] = df_rebate[(df_rebate['Size'] == size) & (df_rebate[offpeak] == 1)].shape[0]

                return df_count
            st.write("20 ft/40 ft offpeak count")
            st.table(count_occurrences(calculate_rebate(add_offpeak_columns(psa_rebate_indicator))))
            psa_offpeak_count = count_occurrences(calculate_rebate(add_offpeak_columns(psa_rebate_indicator)))

            def offpeak_rebate_sums(df_rebate):
                # Filter rows based on conditions
                offpeak_20_24 = df_rebate[(df_rebate['Size'] == '20') & (df_rebate['Offpeak_24'] == 1)]['Rebate'].sum()
                offpeak_40_24 = df_rebate[(df_rebate['Size'] == '40') & (df_rebate['Offpeak_24'] == 1)]['Rebate'].sum()
                offpeak_20_48 = df_rebate[(df_rebate['Size'] == '20') & (df_rebate['Offpeak_48'] == 1)]['Rebate'].sum()
                offpeak_40_48 = df_rebate[(df_rebate['Size'] == '40') & (df_rebate['Offpeak_48'] == 1)]['Rebate'].sum()

                # Create a new DataFrame with the calculated sums
                offpeak_df = pd.DataFrame({
                    'offpeak_24hr': [offpeak_20_24, offpeak_40_24],
                    'offpeak_48hr': [offpeak_20_48, offpeak_40_48]
                    }, index=['20', '40'])

                return offpeak_df
            st.write("Offpeak Rebates ($)")
            st.dataframe(offpeak_rebate_sums(calculate_rebate(add_offpeak_columns(psa_rebate_indicator))))

            def sum_and_round(df):
                column_sums = df.sum() #sum all cols
                rounded_sums = column_sums.round(1)
                return rounded_sums

            sums = sum_and_round(offpeak_rebate_sums(calculate_rebate(add_offpeak_columns(psa_rebate_indicator))))
            #st.write(f"total_offpeak_rebate_24hr: {sums['offpeak_24hr']}") #st.write(f"total_offpeak_rebate_48hr: {sums['offpeak_48hr']}")
            df_offpeak_rebate_sums = offpeak_rebate_sums(calculate_rebate(add_offpeak_columns(psa_rebate_indicator)))

            #20240801
            df_overall_rebate_efficiency = pd.read_excel(r'https://raw.githubusercontent.com/JohnTan38/Project-Income/main/Overall_Rebate_Efficiency.xlsx', sheet_name='OverallRebateEfficiency', 
                                 engine='openpyxl')
            df_psa_lolo = pd.read_excel(r'https://raw.githubusercontent.com/JohnTan38/Project-Income/main/Overall_Rebate_Efficiency.xlsx', sheet_name='PSA_LOLO',
                             engine='openpyxl')
            psa_lolo_20 = df_psa_lolo['psa_lolo_20']
            psa_lolo_40 = df_psa_lolo['psa_lolo_40']
            #sum across cols
            def sum_cols(df, col_sum):
                df[col_sum] = df.sum(axis=1)
                return df

            df_rebate_total=sum_cols(df_offpeak_rebate_sums, 'sum_offpeak_rebate')

            rebate_efficiency_20 = (df_rebate_total['sum_offpeak_rebate']['20'] /psa_lolo_20) /0.5932
            rebate_efficiency_40 = (df_rebate_total['sum_offpeak_rebate']['40'] /psa_lolo_40) /0.5932
            overall_rebate_efficiency = math.ceil(((rebate_efficiency_20+rebate_efficiency_40)/2)*100) /100 #round 2 decimals

            def add_column(df,new_week):
                last_column = df.columns[-1]
                last_week_number = int(last_column.split('_')[-1]) #get week number of last col
                new_column = 'Week_'+ str(last_week_number+1)
                df[new_column] = new_week
                return df
                        
            df_overall_rebate_efficiency_new = add_column(df_overall_rebate_efficiency, overall_rebate_efficiency)
            # Transpose the DataFrame to have weeks as rows
            df_overall_rebate_efficiency_new = df_overall_rebate_efficiency_new.T
            df_overall_rebate_efficiency_new.columns = ['Efficiency']
            df_overall_rebate_efficiency_new.index.name = 'Week'

            # Function to plot the line chart
            def plot_efficiency(df_efficiency,num_weeks):
    
                df_to_plot = df_efficiency.tail(num_weeks) # Select the number of weeks to plot
        
                fig=plt.figure(figsize=(10, 5)) # Plot the line chart
                plt.plot(df_to_plot.index, (df_to_plot['Efficiency']*100).round(2), marker='o')
                for x,y in zip(df_to_plot.index, (df_to_plot['Efficiency']*100).round(2)):
                    plt.text(x,y, f'{y:.2f}%', ha='center', va='bottom')
    
                plt.ylim(0,100)
                plt.xlabel('Week Number')
                plt.ylabel('Efficiency (%)')
                plt.title('PSA Loaded Rebates Efficiency') # Set the labels and title    
                #plt.show() # Show the plot
                st.pyplot(fig) #streamlit

            #num_week = int(input("Enter the number of weeks to plot: ")) # User input for the number of weeks to plot
            plot_efficiency(df_overall_rebate_efficiency_new,lst_num_week[0]) # Call the function with the user input

            def append_dollar(df):
                # Iterate over each col in df
                for col in df.columns:
                    # Convert the col to string, Add '$' to the beginning of each col
                    df[col] = '$' + df[col].astype(str) 
                    return df

            #20240802
            def plot_clustered_bar(df, df_rebate):
                # Set the color palette as gradient from light blue to dark blue
                sns.set_palette(sns.color_palette("Blues", len(df.columns)))
    
                fig, ax = plt.subplots() # Create a figure and a set of subplots
                # Plot the DataFrame as a bar plot with the specified parameters
                df.plot(kind='bar', ax=ax)

                # Append column values of df_rebate to the respective bar charts
                for i, p in enumerate(ax.patches):
                    ax.annotate(str(df_rebate.iloc[i//len(df.columns), i%len(df.columns)]), 
                               (p.get_x() * 1.005, p.get_height() * 1.005))
    
                plt.ylim(0, 100) # Set the y-axis limit    
                plt.title('Nonpeak - container volume and $rebate', fontsize=9) # Set the title of the plot
                plt.ylabel('Container volume and $rebate', fontsize=8)
                plt.xlabel('Container size', fontsize=8)   
                #plt.show() # Show the plot
                st.pyplot(fig,ax)

            df_offpeak_rebate_sums_dollar = append_dollar(df_offpeak_rebate_sums)
            plot_clustered_bar(psa_offpeak_count, (df_offpeak_rebate_sums_dollar.iloc[:, :-1]).T) #call the function


            html_str_offpeak_rebate24 = f"""
                <p style='background-color:#F0FFFF;
                color: #483D8B;
                font-size: 18px;
                font: bold;
                border-radius:5px;
                padding-left: 12px;
                padding-top: 10px;
                padding-bottom: 12px;
                line-height: 18px;
                border-color: #03396c;
                text-align: left;'>
                {sums['offpeak_24hr']}</style>
                <br></p>"""
            st.markdown('''
                **TOTAL OFFPEAK REBATES ($) < 24hr** '''+html_str_offpeak_rebate24, unsafe_allow_html=True)
            
            html_str_offpeak_rebate48 = f"""
                <p style='background-color:#F0FFFF;
                color: #483D8B;
                font-size: 18px;
                font: bold;
                border-radius:5px;
                padding-left: 12px;
                padding-top: 10px;
                padding-bottom: 12px;
                line-height: 18px;
                border-color: #03396c;
                text-align: left;'>
                {sums['offpeak_48hr']}</style>
                <br></p>"""
            st.markdown('''
                **24hr < TOTAL OFFPEAK REBATES ($) < 48hr** '''+html_str_offpeak_rebate48, unsafe_allow_html=True)
            


            success_df('Data generated successfully!')
#st.markdown('''
            #**REBATES** :orange[rebates] :blue-background[blue highlight] :cherry_blossom:''')

            #sheetName = 'psa_rebate_'+ datetime.now().strftime("%Y%m%d %H%M")
            #try:
                    #calculate_rebate(add_offpeak_columns(psa_rebate_indicator)).to_csv("C:/Users/"+usr_name[0]+ "/Downloads/"+ 'psa_rebate.csv', mode='x')
            #except FileExistsError:
                    #calculate_rebate(add_offpeak_columns(psa_rebate_indicator)).to_csv("C:/Users/"+usr_name[0]+ "/Downloads/"+ 'psa_rebate_1.csv')
            
            #usr_email = user_email(usr_name)
            #send_email_psa_reabte(offpeak_rebate_sums(calculate_rebate(add_offpeak_columns(psa_rebate_indicator))),usr_email)


footer_html = """
    <div class="footer">
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #f0f2f6;
            padding: 10px 20px;
            text-align: center;
        }
        .footer a {
            color: #4a4a4a;
            text-decoration: none;
        }
        .footer a:hover {
            color: #3d3d3d;
            text-decoration: underline;
        }
    </style>
        All rights reserved @2025.      
    </div>
"""
st.markdown(footer_html,unsafe_allow_html=True)
