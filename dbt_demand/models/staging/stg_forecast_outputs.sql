with source as (
    select * from {{ source('staging', 'RAW_FORECAST_OUTPUTS') }}
),

renamed as (
    select
        store_nbr::integer as store_nbr,
        family,
        week::date as week,
        actual::float as actual_sales,
        forecast::float as forecasted_sales,
        model,
        (actual::float - forecast::float) as forecast_error,
        abs(actual::float - forecast::float) / nullif(actual::float, 0) as abs_pct_error
    from source
)

select * from renamed