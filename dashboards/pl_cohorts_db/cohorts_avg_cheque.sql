--SQL-запрос предназначен для анализа среднего чека пользователей в разрезе когорт и месяцев 
--(различных периодов времени после первой покупки)

--Этот запрос подходит для оценки среднего чека в разрезе когорт (групп пользователей, присоединившихся в одинаковый период) 
--и месяцев с целью выявления тенденций изменения среднего чека во времени.

--Входные данные:
--Таблица dwh.chequeitems_retro, содержащая информацию о чеках и суммах покупок.

--Выходные данные:
--Рассчитывается значение среднего чека в разрезе когорт и месяцев.

--Алгоритм:
--1. Создание виртуальной таблицы: для каждой транзакции вычисляется когорта (cohort) 
--и месяц визита (visit_month), а также рассчитывается средний чек (avg_cheque).
--2. Группировка результатов по когортам и месяцам, с расчетом среднего чека.
--3. Выбор минимального значения среднего чека в разрезе когорт и месяцев.
--4. Сортировка результатов по убыванию среднего чека.

--Ожидаемый результат:
--Результатом выполнения данного запроса будет таблица с колонками visit_month (месяц визита), 
--cohort (когорта), и значением среднего чека. 
--Полученные данные позволят оценить изменение среднего чека у пользователей в различные 
--периоды времени после первой покупки, а также выявить наиболее успешные когорты по этому показателю.

-------------------------

SELECT visit_month AS visit_month,
       cohort AS cohort,
       min(avg_cheque) AS "Средний чек, руб."
FROM
  (select toString(toStartOfMonth(toDate(dictGet('dwh.d_contact', 'first_shop_d', cityHash64(contact_id, instance_id))))) as cohort,
          toString(toStartOfMonth(toDate(dt))) as visit_month,
          round(sum(summ/100) / count (distinct ch_number),2) as avg_cheque
   from dwh.chequeitems_retro
   where toStartOfMonth(toDate(dictGet('dwh.d_contact', 'first_shop_d', cityHash64(contact_id, instance_id))))<>'1970-01-01'
   group by cohort,
            visit_month
   order by cohort,
            visit_month) AS virtual_table
GROUP BY visit_month,
         cohort
ORDER BY "Средний чек, руб." DESC