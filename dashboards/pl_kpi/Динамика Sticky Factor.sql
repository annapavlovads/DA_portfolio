SELECT toStartOfDay(toDateTime(month)) AS __timestamp,
       min(sticky_factor) AS "Sticky factor"
FROM
  (select month,
          avg(DAU)/MAU as sticky_factor
   from
     (select month, date, DAU,
                          MAU
      from
        (SELECT toDate(dt) as date,
                toStartOfMonth(toDate(dt)) as month,
                count(distinct contact_id) as DAU
         FROM dwh.chequeitems_retro
         WHERE oper_type = 1
           AND is_del = 0
           AND 1
         group by date) as dau_dable
      left join
        (SELECT toStartOfMonth(toDate(dt)) as month,
                count(distinct contact_id) as MAU
         FROM dwh.chequeitems_retro
         WHERE oper_type = 1
           AND is_del = 0
           AND 1
         group by month) as mau_table using month) as basic_table
   group by month,
            MAU
   order by month) AS virtual_table
WHERE month >= toDate('2020-05-01')
  AND month < toDate('2020-12-01')
GROUP BY toStartOfDay(toDateTime(month))
ORDER BY "Sticky factor" DESC