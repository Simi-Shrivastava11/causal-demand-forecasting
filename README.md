# Causal Demand Forecasting & Promotion ROI Analytics

I built this project during my job search after finishing my MS in Data Science at UMD. I wanted to work on something that combined time series forecasting with causal inference, two things I found really interesting but rarely saw done together in portfolio projects.

The core question: when sales go up during a promotion, did the promotion actually cause that, or would people have bought anyway? And more broadly, how well can we predict grocery demand, and what happens when something unexpected hits like an earthquake?

For the promotion analysis I used counterfactual modeling to estimate true incremental lift. For the earthquake I took a different approach and quantified the demand shock by comparing actual sales against model forecasts. A clean causal setup was not possible for the earthquake because it hit all stores simultaneously, so I was careful not to overclaim.

The dataset is real grocery sales data from a large Ecuadorian retailer (Favorita), available on Kaggle. It covers 2013 to 2017 across 54 stores and 33 product families.

---

## What I built

Two things working together.

A forecasting layer that predicts 4 weeks of demand using sales history, promotions, holidays, and oil prices. I built four models: a seasonal naive baseline, moving average, LightGBM, and Prophet. I evaluated them using walk-forward validation to simulate how they would actually perform in production.

A causal layer that estimates what sales would have looked like without a promotion or external event. OLS counterfactual modeling for the promotion, forecast vs actual comparison for the earthquake.

---

## The data

Downloaded from [Kaggle](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/data). Five files: daily sales, store metadata, holidays, oil prices, and transactions.

I narrowed the scope to 5 store-family combinations selected based on data quality: high volume, low zero-sales rate, no long gaps in the series. A lot of product families like PRODUCE had huge stretches of zero sales which makes them basically unmodelable with standard time series methods.

| Store | Family |
|-------|--------|
| 44 | GROCERY I |
| 45 | BEVERAGES |
| 47 | CLEANING |
| 3 | DAIRY |
| 46 | MEATS |

---

## What I learned about feature engineering

This was the part that surprised me most. There are so many ways to accidentally leak future information into your features, things like computing a rolling average without shifting first, or fitting an encoder on the full dataset before splitting. I was careful about this throughout. Every lag and rolling feature uses shift(1) before any calculation so the model only ever sees past data.

I also found that too many features can hurt more than help if they are correlated or noisy. Feature selection matters a lot more than I expected.

---

## Forecasting results

I used expanding window walk-forward validation with a 104 week minimum training window, 4 week forecast horizon, and 4 week step size. 21 folds per series.

| Model | Avg WAPE |
|-------|----------|
| LightGBM | 8.2% |
| Moving Average | 8.7% |
| Prophet | 11.3% |
| Seasonal Naive | 13.5% |

LightGBM wins but the moving average is surprisingly close. That tells you recent demand trend is the strongest signal for these categories. Prophet underperformed and I think it struggled with the relatively short series length per combination.

**By series (LightGBM):**

| Store | Family | WAPE |
|-------|--------|------|
| 3 | DAIRY | 4.7% |
| 46 | MEATS | 7.8% |
| 47 | CLEANING | 8.5% |
| 45 | BEVERAGES | 9.0% |
| 44 | GROCERY I | 9.9% |

DAIRY is the easiest to forecast, clean upward trend and consistent seasonality. GROCERY I is the hardest, high volume with more volatility and sensitivity to external events.

---

## Causal impact analysis

### Promotion, November 2015, Store 44 GROCERY I

I picked a promotion period away from major holidays and the earthquake so I could isolate the effect. I used three control series (CLEANING, DAIRY, BEVERAGES) that were correlated with GROCERY I in the pre-period but not promoted at the same time. MEATS was excluded because its pre-period correlation was near zero.

| | Value |
|-|-------|
| Actual sales | 368,070 |
| Counterfactual | 350,703 |
| Incremental units | 17,367 |
| Lift | 5.0% |

The promotion worked but the lift was modest. A 5% increase means a lot of those sales would have happened anyway.

### Earthquake shock quantification, April 2016

I trained the model on pre-earthquake data, forecasted the shock window, and compared actual vs expected. This is not causal inference. The earthquake hit all stores at the same time so there is no valid control group. I am calling it demand shock quantification.

| Family | Impact | Story |
|--------|--------|-------|
| GROCERY I | +21.4% | Panic buying |
| BEVERAGES | +5.5% | Water and drinks stockpiling |
| CLEANING | -5.0% | Deprioritized during crisis |
| DAIRY | -0.7% | Unaffected, cannot stockpile perishables |
| MEATS | -10.9% | Supply chain disruption |

The pattern across categories tells a coherent story which makes me more confident the numbers are real.

---

## Snowflake and dbt

I loaded all outputs into Snowflake and built a dbt analytics layer on top.

Staging views: `stg_weekly_sales` and `stg_forecast_outputs`

Mart tables: `fct_weekly_sales` and `fct_forecast_performance`

9 data quality tests passing.

---

## Dashboard

Built with Streamlit, pulling live data from Snowflake.

**Live:** https://causal-demand-forecasting-lcadpikgbtacbjt2tnu3br.streamlit.app

---

## How to run it

```bash
git clone https://github.com/Simi-Shrivastava11/causal-demand-forecasting.git
cd causal-demand-forecasting
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Download data from Kaggle
kaggle competitions download -c store-sales-time-series-forecasting -p data/raw/
cd data/raw && unzip store-sales-time-series-forecasting.zip

# Run notebooks in order 01 through 05
jupyter notebook

# Run dashboard
streamlit run dashboard/app.py
```

---

## Limitations

Scoped to 5 combinations so results may not hold for sparse or intermittent demand series.

The OLS counterfactual assumes the relationship between treated and control series stays linear during the event.

Earthquake analysis is shock quantification not causal inference.

Prophet would likely perform better with more data per series.
