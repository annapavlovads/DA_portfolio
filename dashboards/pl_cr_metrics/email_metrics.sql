-- SQL-запрос предназначен для извлечения информации о E-mail-коммуникациях с клиентом. 
-- Результатом запроса является результирующая таблица с данными о затратах, количестве 
пользователей, отношении конверсии, показателях успешности отправки сообщений и других метриках
-- Запрос служит основой для построения чарта-таблицы для дашборда с метриками коммуникаций

------------------------------------------------------

SELECT action_name AS action_name,
       sum(message_price_rub) AS "Затраты, руб.",
       count(DISTINCT contact_id) AS "Users (Контакты, шт.)",
       COUNT(DISTINCT day_7_visit)/count(distinct contact_id) AS "CR-7,%",
       sum(day_7_cheq) AS "CR-7, руб.",
       COUNT(DISTINCT sent)/count(distinct contact_id) AS "SendRate,%",
       COUNT(DISTINCT not_sent)/count(distinct contact_id) AS "BounceRate,%",
       COUNT(DISTINCT error)/count(distinct contact_id) AS "ErrorRate,%",
       COUNT(DISTINCT delivered)/count(distinct contact_id) AS "DeliveryRate,%",
       COUNT(DISTINCT opened)/count(distinct contact_id) AS "OpenRate,%",
       COUNT(DISTINCT link_visit)/count(distinct contact_id) AS "Click ThroughRate,%",
       count(distinct link_visit)/count(distinct opened) AS "Click ToOpen Rate,%",
       sum(day_7_cheq)/count(distinct sent) AS "Revenue PerEmail, руб.",
       SUM(day_7_cheq)/sum(message_price_rub) AS "ReturnOn Marketing Investment, %"
FROM
  (SELECT contact_id,
          first_name,
          last_name,
          mobile_phone,
          email,
          favourite_restaurant,
          action_name,
          send_date,
          16800/1000000 as message_price_rub,
          case
              when (cheq_date>=send_date
                    and cheq_date<send_date+7) then contact_id
              else null
          end as day_7_visit,
          sumIf(cheq_sum, cheq_date>=send_date
                and cheq_date<send_date+7) as day_7_cheq,
          message_state_name,
          case
              when message_state_name = 'Отправлено'
                   and cheq_date<send_date+7 then contact_id
              else null
          end as sent,
          case
              when message_state_name = 'Не отправлено'
                   and cheq_date<send_date+7 then contact_id
              else null
          end as not_sent,
          case
              when message_state_name = 'Ошибка'
                   and cheq_date<send_date+7 then contact_id
              else null
          end as error,
          case
              when message_state_name = 'Доставлено'
                   and cheq_date<send_date+7 then contact_id
              else null
          end as delivered,
          case
              when message_state_name = 'Переход по ссылке'
                   and cheq_date<send_date+7 then contact_id
              else null
          end as link_visit,
          case
              when message_state_name = 'Открыто'
                   and cheq_date<send_date+7 then contact_id
              else null
          end as opened
   FROM
     (SELECT toDate(send_dt) as send_date,
             action_name,
             contact_id,
             dictGet('dwh.d_contact', 'first_name', contact_instance_hash) AS first_name,
             dictGet('dwh.d_contact', 'last_name', contact_instance_hash) AS last_name,
             dictGet('dwh.d_contact', 'sms', contact_instance_hash) AS mobile_phone,
             dictGet('dwh.d_contact', 'email', contact_instance_hash) AS email,
             dictGet('dwh.d_contact', 'freq_shop', contact_instance_hash) AS favourite_restaurant,
             message_state_name
      from dwh.communication
      where message_type_name='Email'
      group by send_date,
               action_name,
               contact_id,
               first_name,
               last_name,
               mobile_phone,
               email,
               favourite_restaurant,
               message_state_name) as sent_table
   left join
     (SELECT toDate(dt) as cheq_date,
             contact_id,
             sum(summ)/100 AS cheq_sum
      FROM dwh.chequeitems_retro
      WHERE oper_type = 1
        AND is_del = 0
      group by contact_id,
               cheq_date) as visit_table on sent_table.contact_id = visit_table.contact_id
   group by contact_id,
            action_name,
            send_date,
            message_state_name,
            message_price_rub,
            day_7_visit,
            sent,
            link_visit,
            delivered,
            error,
            not_sent,
            opened,
            first_name,
            last_name,
            mobile_phone,
            email,
            favourite_restaurant
   order by send_date DESC) AS virtual_table
WHERE send_date >= toDate('2023-10-26')
  AND send_date < toDate('2024-01-26')
GROUP BY action_name
ORDER BY max(send_date) DESC