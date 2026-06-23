import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Causal Demand Forecasting", layout="wide")

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"]
    )

@st.cache_data
def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

weekly_sales = run_query("SELECT * FROM CAUSAL_DEMAND_DB.ANALYTICS_STAGING.STG_WEEKLY_SALES")
forecast = run_query("SELECT * FROM CAUSAL_DEMAND_DB.ANALYTICS_STAGING.STG_FORECAST_OUTPUTS")
performance = run_query("SELECT * FROM CAUSAL_DEMAND_DB.ANALYTICS_MARTS.FCT_FORECAST_PERFORMANCE")
causal = run_query("SELECT * FROM CAUSAL_DEMAND_DB.STAGING.RAW_CAUSAL_IMPACT")
model_comp = run_query("SELECT * FROM CAUSAL_DEMAND_DB.STAGING.RAW_MODEL_COMPARISON")

weekly_sales['WEEK'] = pd.to_datetime(weekly_sales['WEEK'])
forecast['WEEK'] = pd.to_datetime(forecast['WEEK'])

st.title("Causal Demand Forecasting & Promotion ROI Analytics")
st.markdown("Favorita Grocery Dataset — 5 store-family combinations, 4.5 years of weekly data")

tab1, tab2, tab3, tab4 = st.tabs([
    "Executive Summary",
    "Demand Forecast",
    "Causal Impact",
    "Model Performance"
])

with tab1:
    st.header("Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    best_model = model_comp.groupby('MODEL')['WAPE'].mean().idxmin()
    best_wape = model_comp.groupby('MODEL')['WAPE'].mean().min()
    promo_lift = causal[causal['EVENT'].str.contains('Promotion')]['RELATIVE_IMPACT'].values
    eq_impact = causal[causal['EVENT'].str.contains('Earthquake') & 
                       (causal['FAMILY'] == 'GROCERY I')]['RELATIVE_IMPACT'].values
    
    col1.metric("Best Model", best_model.title())
    col2.metric("Best WAPE", f"{float(best_wape):.1%}")
    col3.metric("Promotion Lift", f"{float(promo_lift[0]):.1%}" if len(promo_lift) > 0 else "N/A")
    col4.metric("Earthquake Impact (Grocery)", f"{float(eq_impact[0]):.1%}" if len(eq_impact) > 0 else "N/A")
    
    st.subheader("Model Comparison")
    summary = model_comp.groupby('MODEL')['WAPE'].mean().reset_index().sort_values('WAPE')
    fig = px.bar(summary, x='MODEL', y='WAPE', color='MODEL',
                 title='Average WAPE by Model (lower is better)')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Demand Forecast")
    
    col1, col2 = st.columns(2)
    store = col1.selectbox("Store", sorted(weekly_sales['STORE_NBR'].unique()))
    family = col2.selectbox("Family", sorted(weekly_sales[weekly_sales['STORE_NBR'] == store]['FAMILY'].unique()))
    
    actual = weekly_sales[(weekly_sales['STORE_NBR'] == store) & (weekly_sales['FAMILY'] == family)]
    fc = forecast[(forecast['STORE_NBR'] == store) & (forecast['FAMILY'] == family)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=actual['WEEK'], y=actual['SALES'], name='Actual', line=dict(color='steelblue')))
    fig.add_trace(go.Scatter(x=fc['WEEK'], y=fc['FORECASTED_SALES'], name='Forecast',
                             line=dict(color='orange', dash='dash')))
    fig.add_shape(type='line', x0='2016-04-16', x1='2016-04-16', y0=0, y1=1,
              yref='paper', line=dict(color='red', dash='dash'))
    fig.add_annotation(x='2016-04-16', y=1, yref='paper', text='Earthquake', showarrow=False)
    fig.update_layout(title=f'Store {store} - {family}', xaxis_title='Week', yaxis_title='Weekly Sales')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Forecast Error Over Time")
    fc['ABS_PCT_ERROR'] = fc['ABS_PCT_ERROR'].astype(float)
    fig2 = px.line(fc, x='WEEK', y='ABS_PCT_ERROR', title='Absolute Percentage Error by Week')
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.header("Causal Impact Analysis")
    
    st.subheader("Promotion Impact — Store 44 GROCERY I, November 2015")
    promo = causal[causal['EVENT'].str.contains('Promotion')]
    
    col1, col2, col3 = st.columns(3)
    if len(promo) > 0:
        col1.metric("Actual Sales", f"{float(promo['ACTUAL'].values[0]):,.0f}")
        col2.metric("Counterfactual Sales", f"{float(promo['COUNTERFACTUAL'].values[0]):,.0f}")
        col3.metric("Incremental Lift", f"{float(promo['RELATIVE_IMPACT'].values[0]):.1%}")
    
    st.subheader("Earthquake Shock Analysis — April 2016")
    eq = causal[causal['EVENT'].str.contains('Earthquake')].copy()
    eq['ABSOLUTE_IMPACT'] = eq['ABSOLUTE_IMPACT'].astype(float)
    eq['RELATIVE_IMPACT'] = eq['RELATIVE_IMPACT'].astype(float)
    
    fig = px.bar(eq, x='FAMILY', y='RELATIVE_IMPACT', color='RELATIVE_IMPACT',
                 color_continuous_scale='RdYlGn',
                 title='Earthquake Impact by Product Family (% vs Expected)')
    fig.add_hline(y=0, line_dash='dash', line_color='black')
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(eq[['FAMILY', 'ACTUAL', 'COUNTERFACTUAL', 'ABSOLUTE_IMPACT', 'RELATIVE_IMPACT']].round(2))

with tab4:
    st.header("Model Performance")
    
    summary = model_comp.groupby('MODEL').agg(
        avg_wape=('WAPE', 'mean'),
        avg_rmse=('RMSE', 'mean'),
        avg_mae=('MAE', 'mean')
    ).round(4).reset_index().sort_values('avg_wape')
    
    st.subheader("Overall Model Comparison")
    st.dataframe(summary)
    
    st.subheader("LightGBM Performance by Series")
    lgb = performance[performance['MODEL'] == 'lightgbm'].sort_values('AVG_WAPE')
    lgb['AVG_WAPE'] = lgb['AVG_WAPE'].astype(float)
    
    fig = px.bar(lgb, x='FAMILY', y='AVG_WAPE', color='FAMILY',
                 title='WAPE by Product Family (LightGBM)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(lgb[['STORE_NBR', 'FAMILY', 'AVG_WAPE', 'RMSE', 'MAE']].round(4))