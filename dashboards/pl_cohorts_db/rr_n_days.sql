-- SQL-запрос предназначен для анализа поведения пользователей в различные временные интервалы после их первой 
-- покупки - последующих заказов  (Retention Rate)
-- Анализируется количество активных контактов в различные временные интервалы после первой покупки.

-- Входные данные:
-- Таблица dwh.chequeitems_retro, содержащая информацию о покупках 

-- Выходные данные:
-- Результатом выполнения запроса является таблица с колонками visit_day_order (порядковый номер дня после первой покупки)
-- "Активных контактов, шт." (количество активных контактов)
-- "visit_day_order" (порядковый номер дня после первой покупки)

-- Алгоритм:
-- 1. Создание виртуальной таблицы: для каждого контакта вычисляется когорта (cohort), размер когорты (cohort_size), 
-- максимальный интервал времени после первой покупки (max_diff), а также количество активных контактов (contacts_qty) 
-- в различные временные интервалы после первой покупки
-- 2. Группировка результатов по порядковому номеру дня после первой покупки
-- 3. Фильтрация результатов для учета только определенного интервала времени после первой покупки
-- 4. Сортировка результатов по порядковому номеру дня после первой покупки

-- Результатом выполнения запроса является таблица, содержащая данные о количестве активных контактов в различные 
-- временные интервалы после первой покупки.

------------------------------------------------

SELECT visit_day_order AS visit_day_order,
       sum(contacts_qty) AS "Активных контактов, шт.",
       min(visit_day_order) AS "MIN(visit_day_order)"
FROM
  (SELECT toStartOfMonth(dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) AS cohort,
          case
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) = 0 then 0
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 1
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 30 then 30
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 30
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 60 then 60
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 60
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 90 then 90
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 90
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 120 then 120
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 120
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 150 then 150
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 150
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 180 then 180
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 180
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 210 then 210
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 210
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 240 then 240
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 240
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 270 then 270
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 271
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 300 then 300
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 300
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 330 then 330
              when (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) >= 330
                   and (toDate(dt) - dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)) < 360 then 360
              else 720
          end as visit_day_order,
          uniqExact(contact_id) as contacts_qty
   FROM dwh.chequeitems_retro
   WHERE oper_type = 1
     AND is_del = 0
     AND 1
     and dictGet('dwh.d_contact', 'first_shop_d', contact_instance_hash_calc)<>'1970-01-01'
   group by cohort,
            visit_day_order
   order by cohort asc, visit_day_order asc) AS virtual_table
WHERE cohort >= toDate('2023-01-23')
  AND cohort < toDate('2024-01-23')
GROUP BY visit_day_order
ORDER BY "MIN(visit_day_order)" ASC
LIMIT 1000;
