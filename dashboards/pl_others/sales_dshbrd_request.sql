--SQL-запрос предназначен для извлечения данных о контактах пользователей, чеках покупок и связанных с ними атрибутах из таблицы dwh.chequeitems_retro. 
--Данные выводятся в форме, удобной для последующего анализа и обработки. Результаты можно использовать для получения инсайтов относительно 
--времени совершения покупок, места покупки, суммы чека и других аспектов пользовательской активности.

--Входные данные:
--Таблица dwh.chequeitems_retro, содержащая информацию о чеках и контактах пользователей.

--Выходные данные:
--Результатом выполнения запроса является таблица со следующими колонками: date_time (дата и время), week_day (день недели), 
--hour (час), restaurant_name (название ресторана), ea_ch (атрибуты чека, раскрытые из словаря), contact_id (идентификатор контакта), 
--cheq_id (идентификатор чека), cheq_sum (сумма чека), cheq_summdisc (сумма с учетом скидок), paid_by_bonus (сумма оплаты бонусами).

--Алгоритм:
--1. Выбор данных из таблицы dwh.chequeitems_retro и преобразование временных данных с использованием вспомогательных функций 
--(toDateTime, toDayOfWeek, toHour).
--2. Использование словаря dwh.d_shop для получения названия ресторана с помощью функции dictGet.
--3. Обработка массивов массивов (arrayJoin) для атрибутов чека.
--4. Фильтрация данных с помощью предиката оператора WHERE.
--5. Группировка данных по указанным колонкам с помощью GROUP BY.

--Ожидаемый результат:
--Результатом выполнения запроса будет таблица, содержащая информацию о чеках и контактах пользователей, 
--сгруппированную по определенным атрибутам.

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