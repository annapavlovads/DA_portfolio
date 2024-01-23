SELECT toStartOfDay(toDateTime(cohort)) AS __timestamp,
       min("RR") AS "Средний LifeTime, дней (по когортам)"
FROM
  (select cohort,
          round(sum(qty_of_users/zero_day_users), 4) as RR
   from
     (SELECT toStartOfMonth(first_shop_d) as cohort,
             (last_shop_d - first_shop_d)::int AS days_diff,
             COUNT(DISTINCT contact_id) as qty_of_users
      FROM dwh.contacts_info
      WHERE first_shop_d <> '1970-01-01'
      group by cohort,
               days_diff) as cohort_table
   left join
     (SELECT toStartOfMonth(first_shop_d) as cohort,
             COUNT(DISTINCT contact_id) AS zero_day_users
      FROM dwh.contacts_info
      WHERE last_shop_d = first_shop_d
        AND first_shop_d <> '1970-01-01'
      group by cohort) as zero_day_table using cohort
   group by cohort) AS virtual_table
GROUP BY toStartOfDay(toDateTime(cohort))
ORDER BY "Средний LifeTime, дней (по когортам)" DESC
LIMIT 1000;