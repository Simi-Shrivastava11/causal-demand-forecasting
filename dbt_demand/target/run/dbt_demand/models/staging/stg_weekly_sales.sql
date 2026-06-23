
  create or replace   view CAUSAL_DEMAND_DB.ANALYTICS_STAGING.stg_weekly_sales
  
  
  
  
  as (
    with source as (
    select * from CAUSAL_DEMAND_DB.STAGING.RAW_WEEKLY_SALES
),

renamed as (
    select
        store_nbr::integer as store_nbr,
        family,
        week::date as week,
        sales::float as sales,
        onpromotion::integer as onpromotion,
        oil_price::float as oil_price,
        city,
        state,
        type as store_type,
        cluster::integer as cluster,
        holiday_count::float as holiday_count,
        has_holiday::float as has_holiday
    from source
)

select * from renamed
  );

