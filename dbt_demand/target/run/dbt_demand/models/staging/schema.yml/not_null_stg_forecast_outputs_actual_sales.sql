
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select actual_sales
from CAUSAL_DEMAND_DB.ANALYTICS_STAGING.stg_forecast_outputs
where actual_sales is null



  
  
      
    ) dbt_internal_test