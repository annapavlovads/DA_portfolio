-- SQL-запрос предназначен для анализа покупок клиентов после полученных ими пуш-уведомлений в приложении. 
-- Запрос готовит информацию для построения чарта-таблицы, содержащей общее количество отправленных 
-- пуш-уведомлений, уровень доставки уведомлений, конверсию визитов в покупки и 
-- общую выручку по различным периодам времени после отправки уведомлений.
-- Запрос применяется для анализа эффективности пуш-кампаний и их влияния на поведение клиентов. 
 
-- Входные данные:
-- Запрос использует данные из таблиц dwh.communication (содержит информацию о коммуникациях) и 
-- dwh.chequeitems_retro (содержит информацию о покупках)
  
-- Выходные данные:
-- Результатом запроса является таблица с названиями и значениями следующих показателей: 
-- общее количество отправленных пуш-уведомлений по кампаниями
-- уровень доставки уведомлений, 
-- конверсия визитов в покупки за 7 и 14 дней после отправки
-- общая выручка по 7 и 14 дням после отправки (полученная от клиентов, участвовавших в пуш-кампании)
  
-- Алгоритм:
-- 1. Запрос использует подзапросы для объединения информации о пуш-уведомлениях и покупках клиентов, 
-- а также для расчета показателей уровня доставки, конверсии и общей выручки
-- 2. Подзапросы выполняют группировку, фильтрацию и расчеты суммарных показателей на основе информации о 
-- пуш-уведомлениях и покупках
  
-- Результат:
-- Запрос предоставляет информацию о ключевых показателях эффективности пуш-уведомлений, общее количество 
-- пуш-уведомлений, уровень их доставки, конверсию в покупки и общую выручку по времени после отправки, 
-- служит базой для расчета метрик эффективности рекламных кампаний 
  
--------------------------------------------------------------------------------------------

SELECT count(DISTINCT contact_id) AS "Отправлено пуш, контактов",
       countIf(DISTINCT contact_id, message_state_name<>'Ошибка') / COUNT(DISTINCT contact_id) AS "Уровень доставки, %",
       COUNT(DISTINCT day_7_visit) / countIf(DISTINCT contact_id, message_state_name<>'Ошибка') AS "СR 7 дней, %",
       COUNT(DISTINCT day_14_visit) / countIf(DISTINCT contact_id, message_state_name<>'Ошибка') AS "СR 14 дней, %",
       sum(day_7_cheq) AS "Выручка СR 7 дней, руб.",
       sum(day_14_cheq) AS "Выручка СR 14 дней, руб."
FROM
  (select contact_id,
          send_date,
          message_state_name,
          case
              when cheq_date>=send_date
                   and cheq_date<send_date+7 then contact_id
              else null
          end as day_7_visit,
          case
              when cheq_date>=send_date
                   and cheq_date<send_date+14 then contact_id
              else null
          end as day_14_visit,
          sumIf(cheq_sum, cheq_date>=send_date
                and cheq_date<send_date+7) as day_7_cheq,
          sumIf(cheq_sum, cheq_date>=send_date
                and cheq_date<send_date+14) as day_14_cheq
   from
     (SELECT toDate(send_dt) as send_date,
             contact_id,
             message_state_name
      from dwh.communication
      where message_type_name='Push'
        and position(action_name, 'birthday')>0
        and not position(action_name, 'test')>0
      group by send_date,
               contact_id,
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
            send_date,
            message_state_name,
            day_7_visit,
            day_14_visit) AS virtual_table
WHERE send_date >= toDate('2023-10-22')
  AND send_date < toDate('2024-01-22')
ORDER BY "Отправлено пуш, контактов" DESC
