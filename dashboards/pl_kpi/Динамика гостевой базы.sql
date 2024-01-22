SELECT y_m AS __timestamp,
       sum(cum_sum) AS "Количество клиентов (нарастающий итог)"
FROM
  (WITH contacts_cumsum AS
     (SELECT y_m,
             sumState(contact_qty) as contact
      FROM
        (SELECT toStartOfMonth(registration_d) as y_m,
                uniqExact(contact_id) as contact_qty
         FROM dwh.contacts_info
         WHERE state_contact = 0
           and (registration_d < '2100-01-01'
                or registration_d = '1970-01-01')
         GROUP BY toStartOfMonth(registration_d)
         ORDER  BY toStartOfMonth(registration_d) ASC)
      GROUP BY y_m
      ORDER BY y_m ASC) SELECT y_m,
                               runningAccumulate(contact) as cum_sum,
                               finalizeAggregation(contact) as contacts_monthly
   FROM contacts_cumsum
   ORDER BY y_m ASC) AS virtual_table
WHERE y_m >= toDate('2020-05-01')
  AND y_m < toDate('2020-12-01')
GROUP BY y_m
ORDER BY "Количество клиентов (нарастающий итог)" DESC