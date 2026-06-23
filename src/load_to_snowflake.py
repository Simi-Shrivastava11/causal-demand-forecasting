import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd

SNOWFLAKE_CONFIG = {
    'account': 'OPLYBSH-CS76807',
    'user': 'SimiShrivastava',
    'password': 'Chibataba@2026',
    'warehouse': 'COMPUTE_WH',
    'database': 'CAUSAL_DEMAND_DB',
    'schema': 'STAGING'
}

files = {
    'RAW_WEEKLY_SALES': 'data/processed/weekly_sales_clean.csv',
    'RAW_FEATURE_MATRIX': 'data/processed/feature_matrix.csv',
    'RAW_FORECAST_OUTPUTS': 'data/outputs/forecast_outputs.csv',
    'RAW_MODEL_COMPARISON': 'reports/model_comparison.csv',
    'RAW_CAUSAL_IMPACT': 'reports/causal_impact_results.csv',
}

conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
cursor = conn.cursor()

for table_name, file_path in files.items():
    df = pd.read_csv(file_path)
    df.columns = [c.upper().replace(' ', '_') for c in df.columns]
    
    cursor.execute(f'DROP TABLE IF EXISTS CAUSAL_DEMAND_DB.STAGING.{table_name}')
    
    success, nchunks, nrows, _ = write_pandas(
        conn, df, table_name,
        database='CAUSAL_DEMAND_DB',
        schema='STAGING',
        auto_create_table=True
    )
    print(f'Loaded {table_name}: {nrows} rows, success={success}')

conn.close()
print('All tables loaded successfully')