-- SQL-запрос используется для вычисления среднего "времени жизни" пользователей (в днях) из различных когорт

-- Используемые поля:
-- cohort - когорта пользователей, определяемая как первый месяц их совершения покупки
-- qty_of_users - количество уникальных пользователей в каждой когорте
-- zero_day_users - количество пользователей в день их первой покупки 
-- avg_lifetime_days - среднее "время жизни" пользователей в днях в каждой когорте

--Логика запроса:
-- В первом подзапросе (cohort_table) расчитывается количество дней между первой и последней 
-- покупкой (days_diff) для каждой когорты пользователей. 
-- Также подсчитывается количество уникальных пользователей (qty_of_users) в каждой когорте.
-- Во второй подзапросе (zero_day_table) подсчитывается количество пользователей, совершивших 
-- свою первую покупку в каждом месяце.
-- Оба подзапроса объединяются с помощью LEFT JOIN по полю cohort.
-- Затем выполняется группировка по когортам, и для каждой когорты вычисляется среднее время 
-- жизни пользователей (avg_lifetime_days), что представляет собой среднее количество дней 
-- между первой и последней покупкой в каждой когорте.

----------------------------------------------------------------------

SELECT 
    cohort, 
    ROUND(SUM(qty_of_users/zero_day_users), 4) AS avg_lifetime_days
FROM 

--для каждой когорты пользователей получаем количество дней между первым чеком и 
--чеком покупки и находим разницу между ними в днях 
    (
        SELECT 
            toStartOfMonth(first_shop_d) AS cohort,
            (last_shop_d - first_shop_d)::int AS days_diff, 
            COUNT(DISTINCT contact_id) AS qty_of_users
        FROM 
            dwh.contacts_info 
        WHERE 
            first_shop_d <> '1970-01-01'
        GROUP BY 
            cohort, days_diff
    ) AS cohort_table

LEFT JOIN

--для каждого месяца получаем количество новых пользователей 
    (
        SELECT 
            toStartOfMonth(first_shop_d) AS cohort, 
            COUNT(DISTINCT contact_id) AS zero_day_users 
        FROM 
            dwh.contacts_info 
        WHERE 
            last_shop_d = first_shop_d AND first_shop_d <> '1970-01-01'
        GROUP BY 
            cohort
    ) AS zero_day_table
USING cohort
GROUP BY 
    cohort;
