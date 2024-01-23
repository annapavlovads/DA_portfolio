SELECT visit_month AS visit_month,
       cohort AS cohort,
       min(avg_cheque) AS "Средний чек, руб."
FROM
  (select toString(toStartOfMonth(toDate(dictGet('dwh.d_contact', 'first_shop_d', cityHash64(contact_id, instance_id))))) as cohort,
          toString(toStartOfMonth(toDate(dt))) as visit_month,
          round(sum(summ/100) / count (distinct ch_number),2) as avg_cheque
   from dwh.chequeitems_retro
   where toStartOfMonth(toDate(dictGet('dwh.d_contact', 'first_shop_d', cityHash64(contact_id, instance_id))))<>'1970-01-01'
   group by cohort,
            visit_month
   order by cohort,
            visit_month) AS virtual_table
GROUP BY visit_month,
         cohort
ORDER BY "Средний чек, руб." DESC