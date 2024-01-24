--SQL-запрос используется для анализа данных чеков покупателей в приложении/ресторане по времени и определения новых 
--и повторных покупателей. Запрос извлекает данные из таблицы dwh.chequeitems_retro, объединяет информацию о чеках и 
--ассоциирует их с новыми или повторными покупателями на основе их первой покупки. Результатом запроса является 
--агрегированная информация о сумме чека, новом/повторном покупателе и временной метке начала месяца для каждого чека.
--Запрос полезен для анализа поведения новых и повторных покупателей, выявления изменений в покупательском поведении 
--с течением времени и принятия соответствующих маркетинговых или операционных решений.

--Входные данные:
--Запрос использует данные из таблицы dwh.chequeitems_retro, которая содержит информацию о чеках, покупателях, суммах чеков 
--и других связанных данных.

--Выходные данные:
--Результатом выполнения запроса является таблица с колонками: __timestamp (месяц и год начала периода), is_new (признак нового 
--или повторного покупателя) и "SUM(cheq_sum)" (общая сумма чеков). Это позволяет проанализировать и сравнить сумму чеков новых 
--и повторных покупателей по месяцам.

--Алгоритм:
--1. Используются два подзапроса для получения информации о чеках (t1) и о дате первой покупки для каждого покупателя (t2).
--2. Данные объединяются для определения новых и повторных покупателей, а также суммирования определенных связанных данных, 
--таких как сумма чека и оплачено бонусами.
--3. Результаты фильтруются по указанному временному диапазону для анализа и группируются по новым/повторным покупателям и 
--временной метке начала месяца.

--Ожидаемый результат:
--Результатом работы запроса будет таблица с обобщенными данными о сумме чеков, отнесенной к новым и повторным покупателям, 
--по месяцам в указанном временном диапазоне. Это позволит проанализировать динамику покупок и поведение новых и повторных покупателей.


--------------------------------------------------------------------------

SELECT toStartOfMonth(toDateTime(date_time)) AS __timestamp,
       is_new AS is_new,
       sum(cheq_sum) AS "SUM(cheq_sum)"
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
              when toMonth(date_time)=toMonth(first_shop_date) then 'Новый'
              else 'Повторный'
          end as is_new
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
WHERE date_time >= toDateTime('2020-05-01 00:00:00')
  AND date_time < toDateTime('2020-12-01 00:00:00')
GROUP BY is_new,
         toStartOfMonth(toDateTime(date_time))
ORDER BY "SUM(cheq_sum)" DESC