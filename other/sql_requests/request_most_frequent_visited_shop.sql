--Этот запрос предназначен для подсчета количества коммуникаций, которые относятся к клиентским базам ресторанов в С-Петербурге (смс, емейл, пуш)

--Первый подзапрос извлекает данные о контактах (contact_id) и наиболее часто посещаемом магазине (most_freq_shop) из таблицы dwh.chequeitems_retro. 
--Для этого используется функция dictGet и функция arrayElement для обработки массивов. Группировка происходит по contact_id.

--Второй подзапрос извлекает данные о сообщениях (mess_type, send_date, message_qty) из таблицы dwh.communication, с учетом некоторых условий фильтрации 
--(исключение определенных действий). Для группировки используются поля send_date, mess_type и contact_id.


select 
    contact_id, 
    case when most_freq_shop='' then 'Неизвестно' else most_freq_shop end as most_freq_shop, 
    mess_type, 
    send_date, 
    message_qty 
from
(
    select 
        contact_id, 
        arrayElement(groupArray(tuple(shop_id, shop_qty)),1).1 as most_freq_shop
    from
    (
        select
            distinct contact_id, 
            dictGet('dwh.d_contact', 'freq_shop', cityHash64(contact_id, instance_id)) as shop_id,
            length(groupArray(shop_id)) as shop_qty
        from 
            dwh.chequeitems_retro 
        group by 
            contact_id, shop_id
        order by 
            contact_id, shop_qty DESC
    ) as t1
    group by 
        contact_id
) as t1
right join 
(
    select
        message_type_name as mess_type, 
        toDate(send_d) as send_date,
        contact_id as contact_id,
        count(distinct key_id) as message_qty
    from 
        dwh.communication  
    where 
        is_del=0 
        and not position(lower(action_name), 'test')>0 
        and not position(lower(action_name), 'тест')>0 
        and not position(lower(action_name), 'новая')>0
        and not position(lower(action_name), 'vn_')>0 
        and not position(lower(action_name), 'gatchina')>0 
        and not position(lower(action_name), 'pskov')>0 
        and not position(lower(action_name), 'sb_')>0 
        and not position(lower(action_name), 'vs_')>0 
    group by 
        send_date, mess_type, contact_id
) as t2 
using 
    contact_id
