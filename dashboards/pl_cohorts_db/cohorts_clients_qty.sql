-- SQL-запрос предназначен для расчета количества активных пользователей в разрезе месяцев их первого заказа (покогортно)
-- Полученные данные позволят оценить активность пользователей в различные периоды времени после их первого заказа и 
-- служат основой для построения чарта дашборда когортного анализа

-- Входные данные:
-- 1. Таблица dwh.contacts_info, содержащая информацию о контактах, включая их идентификаторы и даты первого заказа
-- 2. Таблица dwh.chequeitems_retro, содержащая информацию о визитах пользователей.

-- Выходные данные:
-- Расчитывается среднее количество активных пользователей по месяцам, учитывая их когорту.

-- Алгоритм построения запроса:
-- 1. выгрузка информации о дате первого взаимодействия (start_date) для каждого контакта
-- 2. выгрузка информации о дате визита (visit_date) для каждого контакта
-- 3. объединение данных
-- 4. расчет количества активных пользователей для каждой пары месяцев (первого заказа-когорты и следующего заказа) 
-- с учетом условий, таких как start_month < visit_month и start_month<>'1970-01-01' (в контексте хранения данных 
-- у нас - означает наличие хотя бы одного заказа) 
-- 5. группировка результатов по месяцам начала и визита.
-- 6. расчет среднего значения по количеству активных пользователей для каждой пары месяцев (первого заказа-когорты 
-- и следующего заказа) 

-- Результатом выполнения данного запроса будет таблица с колонками 
-- visit_month - месяц заказа
-- start_month - месяц первого заказа - когорта
-- active_users -  количество активных пользователей

--------------------------

SELECT visit_month AS visit_month,
       start_month AS start_month,
       AVG(active_users) AS "AVG(active_users)"
FROM
  (select toString(toStartOfMonth(start_date)) as start_month,
          toString(toStartOfMonth(visit_date)) as visit_month,
          count(distinct contact_id) as active_users
   from
     (select contact_id,
             toDate(dictGet('dwh.d_contact', 'first_shop_d', cityHash64(contact_id, instance_id))) as start_date
      from dwh.contacts_info
      group by contact_id,
               start_date) as t1
   join
     (select distinct (contact_id), toDate(dt) as visit_date
      from dwh.chequeitems_retro) as t2 using contact_id
   group by start_month,
            visit_month
   having start_month < visit_month
   and start_month<>'1970-01-01'
   order by start_month desc, visit_month desc) AS virtual_table
GROUP BY visit_month,
         start_month
