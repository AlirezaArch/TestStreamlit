import datetime
import sys
import json
import time
import os
import numpy as numpy
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

st.title("Cooling System Condition Monitoring")

#left_column, middle_column, right_column = st.columns(3)
#tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])

#inf_url="http://192.168.100.16:8086"
inf_url="http://10.58.17.31:8086"
bucket="analytics-poc"
inf_org="ABB"
inf_token="l6isxGFafI9UmH0VCCgrnV6N6-H_--R7ivFzGVigbrmv2fimDVTsfI63iJTnwc8R1tlUTpnHjKnFxqqXwQsD1Q=="
measurement="ml_test2"

Text1 = st.empty()
Text2 = st.empty()
Text3 = st.empty()
Text4 = st.empty()
Text5 = st.empty()

plot1=st.empty()
plot2=st.empty()


# with left_column:
#     plot1=st.empty()

# with right_column:
#     plot2=st.empty()


CONFIG_INFLUXDB = "config_influxdb.json"


CONF_FILE_DIRECTORY = "init/"

query_SPE = 'from(bucket: "analytics-poc")\
  |> range(start:-200s )\
  |> filter(fn: (r) => r["_measurement"] == "ml_test2")\
  |> filter(fn: (r) => r["_field"] == "SPE_test" or r["_field"]=="Threshold_quantile")'




clientDB = influxdb_client.InfluxDBClient(
    url=inf_url,
    token=inf_token,
    org=inf_org
    )

query_api = clientDB.query_api()



while True:

        #LOAD YOUR MODEL HERE

        try:
            while True:


                result_AD = query_api.query(org=inf_org, query=query_SPE)
                DF_SPE_DB=pd.DataFrame(result_AD[0].records)
                DF_Thresh_DB=pd.DataFrame(result_AD[1].records)

                DF_SPE_DB['time']=DF_SPE_DB[0].apply(lambda x:pd.to_datetime(x.get_time()))
                DF_SPE_DB['value']=DF_SPE_DB[0].apply(lambda x:x.get_value())
                DF_Thresh_DB['time']=DF_Thresh_DB[0].apply(lambda x:pd.to_datetime(x.get_time()))
                DF_Thresh_DB['value']=DF_Thresh_DB[0].apply(lambda x:x.get_value())
                st.write(DF_Thresh_DB['value'])

                figure = go.Figure()
                figure.add_trace(go.Scatter(x = DF_SPE_DB['time'], y = DF_SPE_DB['value'], mode='lines'))
                figure.add_trace(go.Scatter(x = DF_Thresh_DB['time'], y = DF_Thresh_DB['value'], mode='lines'))
                figure.update_yaxes(type='log')
                figure.update_layout(
                    title="Autoencoder SPE_test",
                    autosize=False,
                    width=800,
                    height=600,
                    )


                fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = DF_SPE_DB['value'].iloc[-20:].mean(),
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Anomaly score"}))


                plot1.plotly_chart(figure, theme="streamlit", use_conatiner_width=True)
                plot2.plotly_chart(fig_gauge, theme="streamlit", use_conatiner_width=True)


                    


        except Exception as e:
            print(str(e))
            print(" exception: " + str(time.strftime("%Y%m%d_%H%M%S")),  file=sys.stderr)
            time.sleep(2)
            sys.exit()