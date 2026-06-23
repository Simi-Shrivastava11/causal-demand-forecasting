
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select family
from CAUSAL_DEMAND_DB.ANALYTICS_STAGING.stg_weekly_sales
where family is null



  
  
      
    ) dbt_internal_test