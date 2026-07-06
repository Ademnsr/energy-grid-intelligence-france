select
    extract(hour from start_date) as hour_of_day,
    avg(consumption_mw) as avg_consumption_mw,
    min(consumption_mw) as min_consumption_mw,
    max(consumption_mw) as max_consumption_mw,
    count(*) as nb_observations
from {{ ref('stg_energy_observations') }}
where period_type = 'REALISED'
group by extract(hour from start_date)
order by hour_of_day