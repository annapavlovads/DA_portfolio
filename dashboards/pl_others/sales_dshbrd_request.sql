-- SQL-запрос предназначен для извлечения данных о контактах пользователей, чеках покупок и каналах продаж. атрибутах 
-- Данные выводятся в форме, удобной для построения чартов для дашборда. Результаты можно использовать для получения 
-- инсайтов относительно времени совершения покупок, места покупки, суммы чека и других аспектов пользовательской активности.

-- Входные данные:
-- Таблица dwh.chequeitems_retro, содержащая информацию о покупках 

-- Выходные данные:
-- Результатом выполнения запроса является таблица со следующими колонками: 
-- date_time (дата и время), 
-- week_day (день недели), 
-- hour (час), 
-- restaurant_name (название ресторана)
-- ea_ch (атрибуты чека - канал продаж)
-- contact_id (идентификатор контакта)
-- cheq_id (идентификатор чека)
-- cheq_sum (сумма чека, руб.)
-- cheq_summdisc (сумма с учетом скидок и бонусов, руб.)
-- paid_by_bonus (сумма оплаты бонусами)

-- Алгоритм:
-- 1. Выбор данных из таблицы dwh.chequeitems_retro и их преобразование 
-- (использование словарей с помощью функции dictGet, обработка массивов массивов для атрибутов чека)
-- 2. Фильтрация данных 
-- 3. Группировка данных 

-- Результатом выполнения запроса является таблица, содержащая информацию о чеках и контактах пользователей

---------------------------------------------------------------------------

SELECT 
	toDateTime(dt) as date_time,
	toDayOfWeek(toDateTime(dt)) as week_day, 
	toHour(toDateTime(dt)) as hour,
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

GROUP BY date_time, 
	heq_id, 
	cheq_sum, 
	cheq_summdisc, 
	ea_ch, 
	week_day, 
	hour, 
	contact_id, 
	restaurant_name
