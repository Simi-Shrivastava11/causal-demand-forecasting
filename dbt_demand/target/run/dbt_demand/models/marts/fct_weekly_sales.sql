
  
    

create or replace transient table CAUSAL_DEMAND_DB.ANALYTICS_MARTS.fct_weekly_sales
    
    
    
    as (with weekly_sales as (
    select * from CAUSAL_DEMAND_DB.ANALYTICS_STAGING.stg_weekly_sales
),

with_metrics as (
    select
        store_nbr,
        family,
        week,
        sales,
        onpromotion,
        oil_price,
        city,
        state,
        store_type,
        cluster,
        holiday_count,
        has_holiday,
        avg(sales) over (
            partition by store_nbr, family
            order by week
            rows between 3 preceding and 1 preceding
        ) as rolling_avg_4wk,
        sum(sales) over (
            partition by store_nbr, family
            order by week
            rows between 51 preceding and current row
        ) as rolling_52wk_sales,
        lag(sales, 52) over (
            partition by store_nbr, family
            order by week
        ) as sales_same_week_last_year,
        sales - lag(sales, 52) over (
            partition by store_nbr, family
            order by week
        ) as yoy_change
    from weekly_sales
)

select * from with_metrics
    )
;


  