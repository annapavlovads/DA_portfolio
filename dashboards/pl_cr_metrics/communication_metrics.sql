with restaurant_table as 
  (select contact_id,
  arrayElement(groupArray(tuple(shop_id, shop_qty)), 1).1 as most_freq_shop
  from
    (SELECT distinct contact_id,
    dictGet('dwh.d_contact', 'freq_shop', contact_hash_calc) as shop_id,
    length(groupArray(shop_id)) as shop_qty
    from dwh.chequeitems_retro
    group by contact_id,shop_id
    order by contact_id, shop_qty DESC) as t1
    group by contact_id), 
sent_table as 
  (SELECT toDate(send_dt) as send_date, action_name, contact_id, message_state_name, message_type_name
  FROM dwh.communication
  group by send_date, action_name, contact_id, message_state_name, message_type_name), 
order_table as 
  (SELECT toDate(dt) as cheq_date, contact_id, sum(summ)/100 AS cheq_sum
  FROM dwh.chequeitems_retro
  WHERE oper_type = 1 AND is_del = 0
  group by contact_id, cheq_date)
select st.contact_id as user_id, 
case when rt.most_freq_shop='' then 'Неизвестно' else rt.most_freq_shop end as restaurant, 
st.send_date as date, 
st.action_name as action, 
st.message_state_name as message_state, 
st.message_type_name as message_type, 
case when (ot.cheq_date>=st.send_date and ot.cheq_date<=st.send_date+7) then ot.contact_id end as day_7_visit,
sumIf(ot.cheq_sum, ot.cheq_date>=st.send_date and ot.cheq_date<st.send_date+7) as day_7_cheq
from 
sent_table as st left join order_table as ot on st.contact_id=ot.contact_id
left join restaurant_table as rt on ot.contact_id=rt.contact_id
group by user_id, restaurant, date, action, message_state, message_type, day_7_visit