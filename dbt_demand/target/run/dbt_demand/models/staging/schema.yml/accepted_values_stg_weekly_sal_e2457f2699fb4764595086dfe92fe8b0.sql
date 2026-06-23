
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        family as value_field,
        count(*) as n_records

    from CAUSAL_DEMAND_DB.ANALYTICS_STAGING.stg_weekly_sales
    group by family

)

select *
from all_values
where value_field not in (
    'GROCERY I','BEVERAGES','MEATS','CLEANING','DAIRY'
)



  
  
      
    ) dbt_internal_test