-- SQL-запрос предназначен для извлечения информации о первых покупках пользователей из таблицы dwh.chequeitems_retro 
-- и выявления особенностей поведения клиентов в момент их первой покупки и построения чарта для дашборда, отвечающего 
-- на вопрос, какой канал продаж (алякарт, доставка или самовывоз) является каналом "входа" контакта в продукт 

-- Входные данные: 
-- Таблица dwh.chequeitems_retro, содержащая информацию о покупках 

-- Выходные данные: 
-- Результатом выполнения запроса является таблица со следующими колонками: 
-- дата первой покупки в формате ПН
-- атрибуты чека
-- количество уникальных чеков

-- Алгоритм:
-- 1. Выбор данных из таблицы dwh.chequeitems_retro и преобразование данных с использованием вспомогательных 
-- функций (toDateTime, toMonday)
-- 2. Выбор атрибутов чеков, контактной информации и других характеристик первых покупок пользователей
-- 3. Отбор только первых покупок каждого клиента
-- 4. Группировка данных по указанным колонкам с использованием оператора GROUP BY
-- 5. Сортировка результатов по количеству уникальных идентификаторов чеков в порядке убывания

-- Ожидаемый результат:
-- Результатом выполнения запроса будет таблица, содержащая информацию об атрибутах чеков, относящихся к
-- первым покупкам пользователей, и количество уникальных идентификаторов чеков для каждого из них в разбивке
-- по месяцам как база для построения чарта 

------------------------------------------------------------------------------------------

SELECT toMonday(toDateTime(date_time)) AS __timestamp,
       ea_ch AS ea_ch,
       count(DISTINCT cheq_id) AS "COUNT_DISTINCT(cheq_id)"

FROM
  (select date_time,
          restaurant_name,
          ea_ch,
          contact_id,
          cheq_id,
          cheq_sum,
          cheq_summdisc,
          paid_by_bonus,
          first_shop_date,
          case
              when toDate(date_time)=toDate(first_shop_date) then 1
              else 0
          end as is_first_order
   from
     (SELECT toDateTime(dt) as date_time,
             dictGet('dwh.d_shop', 'name', cityHash64(shop_id, instance_id)) as restaurant_name,
             arrayJoin(ea_ch.1) as ea_ch,
             contact_id as contact_id,
             cheque_id AS cheq_id,
             summ_ch/100 AS cheq_sum,
             summdisc_ch/100 AS cheq_summdisc,
             sum(paid_by_bonus/100) as paid_by_bonus
      FROM dwh.chequeitems_retro
      WHERE oper_type = 1
        AND is_del = 0
        AND 1
      group by date_time,
               cheq_id,
               cheq_sum,
               cheq_summdisc,
               ea_ch,
               contact_id,
               restaurant_name) as t1
   left join
     (SELECT min(toDateTime(dt)) as first_shop_date,
             contact_id as contact_id
      FROM dwh.chequeitems_retro
      WHERE is_del = 0
      group by contact_id) as t2 using contact_id) AS virtual_table
WHERE is_first_order = '1'
GROUP BY ea_ch,
         toMonday(toDateTime(date_time))
ORDER BY "COUNT_DISTINCT(cheq_id)" DESC
