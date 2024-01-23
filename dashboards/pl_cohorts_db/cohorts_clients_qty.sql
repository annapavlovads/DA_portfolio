SELECT visit_month AS visit_month,
       start_month AS start_month,
       AVG(active_users) AS "AVG(active_users)"
FROM
  (select toString(toStartOfMonth(start_date)) as start_month,
          toString(toStartOfMonth(visit_date)) as visit_month,
          count(distinct contact_id) as active_users
   from
     (select contact_id,
             toDate(dictGet('dwh.d_contact', 'first_shop_d', cityHash64(contact_id, instance_id))) as start_date
      from dwh.contacts_info
      group by contact_id,
               start_date) as t1
   join
     (select distinct (contact_id), toDate(dt) as visit_date
      from dwh.chequeitems_retro) as t2 using contact_id
   group by start_month,
            visit_month
   having start_month < visit_month
   and start_month<>'1970-01-01'
   order by start_month desc, visit_month desc) AS virtual_table
GROUP BY visit_month,
         start_month
LIMIT 1000;