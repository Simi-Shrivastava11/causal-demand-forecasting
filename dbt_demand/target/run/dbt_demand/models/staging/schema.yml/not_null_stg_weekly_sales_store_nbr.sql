
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select store_nbr
from CAUSAL_DEMAND_DB.ANALYTICS_STAGING.stg_weekly_sales
where store_nbr is null



  
  
      
    ) dbt_internal_test