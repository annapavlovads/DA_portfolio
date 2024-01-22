SELECT this_month,
       previous_month,
       -1 * uniq(contact_id) as num_users,
       status
FROM

     (SELECT contact_id,
             groupUniqArray(toStartOfMonth(toDate(dt))) as months_visited,
             addMonths(arrayJoin(months_visited), +1) this_month,
             if(has(months_visited, this_month) = 1, 'retained', 'gone') as status,
             addWeeks(this_month, -1) as previous_month
      FROM dwh.chequeitems_retro
      group by contact_id) as table_1

   WHERE status = 'gone'
   GROUP BY this_month,
            previous_month,
            status
   HAVING this_month != addMonths(toStartOfMonth(today()), +1)

   UNION ALL 

   SELECT this_month,
          previous_month,
          toInt64(uniq(contact_id)) as num_users,
          status
   FROM

     (SELECT contact_id,
             groupUniqArray(toStartOfMonth(toDate(dt))) as months_visited,
             arrayJoin(months_visited) this_month,
             if(has(months_visited, addMonths(this_month, -1)) = 1, 'retained', 'new') as status,
             addWeeks(this_month, -1) as previous_month
      FROM dwh.chequeitems_retro
      group by contact_id) as table_2

   GROUP BY this_month,
            previous_month,
            status