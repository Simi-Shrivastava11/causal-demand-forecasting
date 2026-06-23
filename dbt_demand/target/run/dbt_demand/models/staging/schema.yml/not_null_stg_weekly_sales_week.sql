
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select week
from CAUSAL_DEMAND_DB.ANALYTICS_STAGING.stg_weekly_sales
where week is null



  
  
      
    ) dbt_internal_test