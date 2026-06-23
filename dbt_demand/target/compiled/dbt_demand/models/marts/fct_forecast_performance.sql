with forecasts as (
    select * from CAUSAL_DEMAND_DB.ANALYTICS_STAGING.stg_forecast_outputs
),

performance as (
    select
        store_nbr,
        family,
        model,
        count(*) as num_weeks,
        avg(abs_pct_error) as avg_wape,
        sqrt(avg(power(forecast_error, 2))) as rmse,
        avg(abs(forecast_error)) as mae,
        sum(actual_sales) as total_actual_sales,
        sum(forecasted_sales) as total_forecasted_sales
    from forecasts
    group by store_nbr, family, model
)

select * from performance