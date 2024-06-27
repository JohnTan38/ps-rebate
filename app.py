import streamlit as st
import pandas as pd
import numpy as np
import math,re
from datetime import datetime

st.set_page_config('PSA Rebates', page_icon="🏛️", layout='wide')
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

title_main('PSA Rebates')

dataUpload = st.file_uploader("Upload your xlsx file", type="xlsx")
if dataUpload is None:
        st.text("Please upload a file")
elif dataUpload is not None:
        data_0 = pd.read_excel(dataUpload, sheet_name='week_25_volume', engine='openpyxl')
        data_0 = data_0.dropna(axis=1, how='all')
        data_0 = data_0.transpose().reset_index().rename(columns={'index':'peak/offpeak', 0:'24h', 1:'48h', 2:'_48h'})
        data_new = data_0.tail(-1)

        psa_rebate = pd.read_excel(r'https://raw.githubusercontent.com/JohnTan38/Best-README/master/PSA_rebate_github.xlsx', 
                                   sheet_name='psa_rebate_total', engine='openpyxl')
        if st.button('Lets get rebates'):
            #st.dataframe(data_new)
            st.divider()
            rebate = data_new.copy()
            
            #offpeak rebate
            offpeak_20_24 = psa_rebate.iloc[0, psa_rebate.columns.get_loc('offpeak_24')] #35
            offpeak_20_48 = psa_rebate.iloc[0, psa_rebate.columns.get_loc('offpeak_48')] #15
            offpeak_40_24 = psa_rebate.iloc[1, psa_rebate.columns.get_loc('offpeak_24')] #52.5
            offpeak_40_48 = psa_rebate.iloc[1, psa_rebate.columns.get_loc('offpeak_48')] #22.5

            offpeak_rebate_20 = offpeak_20_24*(rebate.iloc[3, rebate.columns.get_loc('24h')]) + offpeak_20_48*(rebate.iloc[3, rebate.columns.get_loc('48h')])
            offpeak_rebate_40 = offpeak_40_24*(rebate.iloc[4, rebate.columns.get_loc('24h')]) + offpeak_40_48*(rebate.iloc[4, rebate.columns.get_loc('48h')])
            offpeak_rebate_total = math.ceil(offpeak_rebate_20 + offpeak_rebate_40)

            #peak rebate
            peak_20_24 = psa_rebate.iloc[0, psa_rebate.columns.get_loc('peak_24')] #25
            peak_20_48 = psa_rebate.iloc[0, psa_rebate.columns.get_loc('peak_48')] #10
            peak_40_24 = psa_rebate.iloc[1, psa_rebate.columns.get_loc('peak_24')] #37.5
            peak_40_48 = psa_rebate.iloc[1, psa_rebate.columns.get_loc('peak_48')] #15

            peak_rebate_20 = peak_20_24*(rebate.iloc[0, rebate.columns.get_loc('24h')]) + peak_20_48*(rebate.iloc[0, rebate.columns.get_loc('48h')])
            peak_rebate_40 = peak_40_24*(rebate.iloc[1, rebate.columns.get_loc('24h')]) + peak_40_48*(rebate.iloc[1, rebate.columns.get_loc('48h')])
            peak_rebate_total = math.ceil(peak_rebate_20 + peak_rebate_40)

            #total rebate    
            rebate_total = pd.DataFrame(columns=['peak_24', 'peak_48', 'peak_total', 'offpeak_24', 'offpeak_48', 'offpeak_total'], 
                                        index=['20_ft', '40_ft'])

            rebate_total.loc['20_ft', 'peak_24'] = peak_20_24*(rebate.iloc[0, rebate.columns.get_loc('24h')])
            rebate_total.loc['20_ft', 'peak_48'] = peak_20_48*(rebate.iloc[0, rebate.columns.get_loc('48h')])
            rebate_total.loc['20_ft', 'peak_total'] = peak_rebate_20
            rebate_total.loc['20_ft', 'offpeak_24'] = offpeak_20_24*(rebate.iloc[3, rebate.columns.get_loc('24h')])
            rebate_total.loc['20_ft', 'offpeak_48'] = offpeak_20_48*(rebate.iloc[3, rebate.columns.get_loc('48h')])
            rebate_total.loc['20_ft', 'offpeak_total'] = offpeak_rebate_20

            rebate_total.loc['40_ft', 'peak_24'] = peak_40_24*(rebate.iloc[1, rebate.columns.get_loc('24h')])
            rebate_total.loc['40_ft', 'peak_48'] = peak_40_48*(rebate.iloc[1, rebate.columns.get_loc('48h')])
            rebate_total.loc['40_ft', 'peak_total'] = peak_rebate_40
            rebate_total.loc['40_ft', 'offpeak_24'] = offpeak_40_24*(rebate.iloc[4, rebate.columns.get_loc('24h')])
            rebate_total.loc['40_ft', 'offpeak_48'] = offpeak_40_48*(rebate.iloc[4, rebate.columns.get_loc('48h')])
            rebate_total.loc['40_ft', 'offpeak_total'] = offpeak_rebate_40

            html_str_offpeak_rebate = f"""
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
                {offpeak_rebate_total}</style>
                <br></p>"""
            st.markdown('''
                **OFFPEAK REBATES** '''+html_str_offpeak_rebate, unsafe_allow_html=True)

            success_df('Data generated successfully!')


st.markdown('''
            **REBATES** :orange[rebates] :blue-background[blue highlight] :cherry_blossom:''')
