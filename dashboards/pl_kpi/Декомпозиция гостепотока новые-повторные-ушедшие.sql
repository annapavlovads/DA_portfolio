--SQL-запрос предназначен для анализа посещаемости пользователей и рассчитывает среднее количество уникальных пользователей 
--в указанном месяце. Запрос извлекает данные из таблицы dwh.chequeitems_retro, вычисляет статус пользователей 
--(удержание, ушедшие, новые), а также выполняет агрегацию и фильтрацию данных для получения среднего количества 
--пользователей в месяц для анализа поведения пользователей, определения эффективности удержания клиентов и оценки 
--эффективности маркетинговых кампаний.

--Входные данные:
--Таблица dwh.chequeitems_retro, содержащая информацию о посещении пользователей (contact_id), а также даты их посещения.

--Выходные данные:
--Результатом выполнения запроса является таблица со следующими колонками: __timestamp (дата начала месяца), 
--status (статус пользователя), "AVG(num_users)" (среднее количество уникальных пользователей в месяц).

--Алгоритм:
--1. Извлечение данных из таблицы dwh.chequeitems_retro с помощью вспомогательного подзапроса и преобразование 
--дат с использованием функций toStartOfMonth, toDateTime, toDate.
--2. Вычисление количества уникальных пользователей за каждый месяц и их статуса (удержание, ушедшие, новые).
--3. Фильтрация полученных данных на основе статуса пользователей и отбор только ушедших пользователей.
--4. Группировка данных по месяцам, статусу и количеству пользователей.
--5. Объединение результатов двух подзапросов с использованием UNION ALL для получения общей таблицы с данными.
--6. Фильтрация и агрегация данных на основе даты и статуса пользователей.
--7. Сортировка результатов в порядке убывания среднего количества пользователей в месяц.

--Ожидаемый результат:
--Результатом выполнения запроса будет таблица, содержащая информацию о среднем количестве уникальных пользователей по месяцам и их статусе.

----------------------------------------------------------------------------------------------

SELECT toStartOfMonth(toDateTime(this_month)) AS __timestamp,
       status AS status,
       AVG(num_users) AS "AVG(num_users)"
FROM
  (SELECT this_month,
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
   UNION ALL SELECT this_month,
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
            status) AS virtual_table
WHERE this_month >= toDate('2020-05-01')
  AND this_month < toDate('2020-12-01')
GROUP BY status,
         toStartOfMonth(toDateTime(this_month))
ORDER BY "AVG(num_users)" DESC