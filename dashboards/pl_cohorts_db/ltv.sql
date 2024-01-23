SELECT cohort AS cohort,
       cohort_size AS cohort_size,
       max_diff AS max_diff,
       day_0 AS day_0,
       day_7 AS day_7,
       day_14 AS day_14,
       day_30 AS day_30,
       day_60 AS day_60,
       day_90 AS day_90,
       day_180 AS day_180,
       day_365 AS day_365,
       day_730 AS day_730
FROM
  (select cohort,
          count(distinct contact_id) as cohort_size,
          max(diff) as max_diff,
          round(sum(case
                        when diff = 0 then cheque_sum
                    end) / count(distinct contact_id), 2) as day_0,
          round(case
                    when max(diff)>0 then sum(case
                                                  when diff<=7 then cheque_sum
                                              end) / count(distinct contact_id)
                end, 0) as day_7 ,
          round(case
                    when max(diff)>7 then sum(case
                                                  when diff<=14 then cheque_sum
                                              end) / count(distinct contact_id)
                end, 0) as day_14 ,
          round(case
                    when max(diff)>14 then sum(case
                                                   when diff<=30 then cheque_sum
                                               end) / count(distinct contact_id)
                end, 0) as day_30,
          round(case
                    when max(diff)>30 then sum(case
                                                   when diff<=60 then cheque_sum
                                               end) / count(distinct contact_id)
                end, 0) as day_60,
          round(case
                    when max(diff)>60 then sum(case
                                                   when diff<=90 then cheque_sum
                                               end) / count(distinct contact_id)
                end, 0) as day_90,
          round(case
                    when max(diff)>90 then sum(case
                                                   when diff<=180 then cheque_sum
                                               end) / count(distinct contact_id)
                end, 0) as day_180,
          round(case
                    when max(diff)>180 then sum(case
                                                    when diff<=365 then cheque_sum
                                                end) / count(distinct contact_id)
                end, 0) as day_365,
          round(case
                    when max(diff)>365 then sum(case
                                                    when diff<=730 then cheque_sum
                                                end) / count(distinct contact_id)
                end, 0) as day_730
   from
     (select contact_id,
             toDate(dt) as cheq_date,
             toStartOfMonth(dictGet('dwh.d_contact', 'first_shop_d', cityHash64(contact_id, instance_id))) as cohort,
             toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', cityHash64(contact_id, instance_id)) as diff,
             summdisc/100 as cheque_sum
      from dwh.chequeitems_retro
      group by contact_id,
               cheq_date,
               cohort,
               diff,
               cheque_sum) as t1
   group by cohort
   having cohort > '2020-04-01'
   order by cohort) AS virtual_table