--SQL-запрос для расчета показателя LTV (пожизненной ценности клиента) в разрезе различных временных интервалов для каждой 
--когорты клиентов. Основной целью запроса является выявление поведения клиентов по мере прошествия времени с момента первой 
--покупки и определение их ценности в различные периоды. Результаты запроса позволяют оценить, как меняется LTV клиентов в различные 
--интервалы времени после первой покупки, что может быть полезно при принятии решений о стимулировании продаж и удержании клиентов.
 
--Входные данные:
--Для выполнения запроса используются данные из таблицы dwh.chequeitems_retro, содержащей информацию о чеках, их датах, суммах, 
--а также связанных с этими чеками идентификаторах клиентов.
  
--Выходные данные:
--Результатом выполнения запроса является таблица с колонками: "Размер когорты, контактов", "Макс. кол-во дней для LTV" и 
--значениями LTV для различных временных интервалов (7, 14, 30, 60, 90, 180, 365, 730 дней).
  
--Алгоритм:
--1. Внутри запроса используются подзапросы для вычисления размера когорты (общего количества клиентов), максимального 
--количества дней, прошедших с момента первой покупки, и расчета LTV для различных временных интервалов после первой покупки.
--2. Подзапросы выполняют необходимые операции по фильтрации, группировке и условным расчетам для LTV в различные моменты времени.
  
--Ожидаемый результат:
--Результатом выполнения запроса является таблица с показателями LTV для различных временных интервалов для каждой когорты клиентов. 
--Это позволяет оценить зависимость стоимости клиента от времени после первой покупки, что полезно для принятия решений по маркетингу, 
--удержанию клиентов и оценки эффективности продаж.
  

-----------------------------------------------------------------------------------------

SELECT "Размер когорты, контактов" AS "Размер когорты, контактов",
       "Макс. кол-во дней для LTV" AS "Макс. кол-во дней для LTV",
       "Первая покупка" AS "Первая покупка",
       "LTV 7 дней" AS "LTV 7 дней",
       "LTV 14 дней" AS "LTV 14 дней",
       "LTV 30 дней" AS "LTV 30 дней",
       "LTV 60 дней" AS "LTV 60 дней",
       "LTV 90 дней" AS "LTV 90 дней",
       "LTV 180 дней" AS "LTV 180 дней",
       "LTV 365 дней" AS "LTV 365 дней",
       "LTV 730 дней" AS "LTV 730 дней"
FROM
  (select count(distinct contact_id) as "Размер когорты, контактов",
          max(diff) as "Макс. кол-во дней для LTV",
          round(sum(case
                        when diff = 0 then cheque_sum
                    end) / count(distinct contact_id), 0) as "Первая покупка",
          round(case
                    when max(diff)>0 then sum(case
                                                  when diff<=7 then cheque_sum
                                              end) / count(distinct contact_id)
                end, 0) as "LTV 7 дней",
          round(case
                    when max(diff)>7 then sum(case
                                                  when diff<=14 then cheque_sum
                                              end) / count(distinct contact_id)
                end, 0) as "LTV 14 дней",
          round(case
                    when max(diff)>14 then sum(case
                                                   when diff<=30 then cheque_sum
                                               end) / count(distinct contact_id)
                end, 0) as "LTV 30 дней",
          round(case
                    when max(diff)>30 then sum(case
                                                   when diff<=60 then cheque_sum
                                               end) / count(distinct contact_id)
                end, 0) as "LTV 60 дней",
          round(case
                    when max(diff)>60 then sum(case
                                                   when diff<=90 then cheque_sum
                                               end) / count(distinct contact_id)
                end, 0) as "LTV 90 дней",
          round(case
                    when max(diff)>90 then sum(case
                                                   when diff<=180 then cheque_sum
                                               end) / count(distinct contact_id)
                end, 0) as "LTV 180 дней",
          round(case
                    when max(diff)>180 then sum(case
                                                    when diff<=365 then cheque_sum
                                                end) / count(distinct contact_id)
                end, 0) as "LTV 365 дней",
          round(case
                    when max(diff)>365 then sum(case
                                                    when diff<=730 then cheque_sum
                                                end) / count(distinct contact_id)
                end, 0) as "LTV 730 дней"
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
   having cohort > '2020-01-01') AS virtual_table