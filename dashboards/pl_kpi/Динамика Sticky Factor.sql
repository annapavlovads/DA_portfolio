--SQL-запрос используется для расчета "Sticky factor" (коэффициент удержания пользователей) приложения на начало каждого дня 
--в указанном временном диапазоне. Запрос извлекает данные из таблицы dwh.chequeitems_retro, осуществляет агрегацию и расчет 
--"Sticky factor" на начало каждого месяца, а затем выводит информацию о "Sticky factor" на начало каждого дня в указанном 
--диапазоне времени. Результаты запроса помогают провести нализ удержания пользователей в приложении, позволяет определить, 
--насколько успешно удерживаются пользователи после привлечения, а также осуществляет мониторинг изменений "Sticky factor" 
--в определенный период времени.

--Входные данные:
--Таблица dwh.chequeitems_retro, содержащая информацию о количестве уникальных пользователей (contact_id), датах (dt) и 
--типах операций (oper_type) в приложении.

--Выходные данные:
--Результатом выполнения запроса является таблица с колонками: __timestamp (дата начала дня) и "Sticky factor", которая 
--отражает "Sticky factor" на начало каждого дня в указанном временном диапазоне.

--Алгоритм:
--1. Извлечение данных из таблицы dwh.chequeitems_retro с использованием вложенного подзапроса, расчетом "Sticky factor" 
--для каждого месяца.
--2. Фильтрация данных по указанному временному диапазону.
--3. Расчет "Sticky factor" на начало каждого дня в указанном диапазоне времени.
--4. Группировка данных по дням и сортировка результатов по "Sticky factor" в порядке убывания.

--Ожидаемый результат:
--Результатом работы запроса будет таблица, содержащая "Sticky factor" на начало каждого дня в указанном временном диапазоне, 
--что позволит проанализировать удержание пользователей в приложении.

--------------------------------------------------------------------------

SELECT toStartOfDay(toDateTime(month)) AS __timestamp,
       min(sticky_factor) AS "Sticky factor"
FROM
  (select month,
          avg(DAU)/MAU as sticky_factor
   from
     (select month, date, DAU,
                          MAU
      from
        (SELECT toDate(dt) as date,
                toStartOfMonth(toDate(dt)) as month,
                count(distinct contact_id) as DAU
         FROM dwh.chequeitems_retro
         WHERE oper_type = 1
           AND is_del = 0
           AND 1
         group by date) as dau_dable
      left join
        (SELECT toStartOfMonth(toDate(dt)) as month,
                count(distinct contact_id) as MAU
         FROM dwh.chequeitems_retro
         WHERE oper_type = 1
           AND is_del = 0
           AND 1
         group by month) as mau_table using month) as basic_table
   group by month,
            MAU
   order by month) AS virtual_table
WHERE month >= toDate('2020-05-01')
  AND month < toDate('2020-12-01')
GROUP BY toStartOfDay(toDateTime(month))
ORDER BY "Sticky factor" DESC