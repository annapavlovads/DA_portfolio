--Назначение запроса:
--Этот SQL-запрос используется для создания сегментации на основе RFM-анализа (recency, frequency, monetary) для контактов 
--в базе данных, в зависимости от их RFM-показателя присваивается макросегмент и сегмент.

--Используемые поля:
-- contact_id - идентификатор контакта
-- first_name - имя контакта
-- mobile_phone - мобильный телефон контакта
-- email - электронная почта контакта
-- favourite_restaurant - любимый ресторан контакта
-- R_, F_, M_ - пороговые значения для Recency, Frequency, Monetary
-- Recency, Frequency, Monetary - расчетные показатели на основе R_, F_, M_
-- RFM - объединенная строка, содержащая значения Recency, Frequency, Monetary
-- macrosegment - макросегмент контакта
-- segment - сегмент контакта

--Логика запроса:
-- Для каждого контакта выполняется расчет показателей Recency, Frequency и Monetary на основе пороговых значений R_, F_, M_.
-- Значения Recency, Frequency и Monetary объединяются в строку и сохраняются в поле RFM.
-- На основе значений Recency, Frequency и Monetary вычисляются макросегмент и сегмент для каждого контакта 
-- с использованием CASE выражений.

--------------------------

-- Присваиваем название для полученного кода сегмента, подтягиваем контактные данные для каждого контакта, получаем 
-- базовую таблицу для построения всех визуализаций в Superset
SELECT
      contact_id,
      first_name,
      mobile_phone, 
      email, 
      favourite_restaurant,
      R_, F_, M_, 
      arrayStringConcat(array(Recency, Frequency, Monetary), '') AS RFM,

       CASE
           WHEN (arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '51%' OR arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '41%') THEN 'Новые'
           WHEN (arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '52%' OR arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '53%' OR arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '54%' OR arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '55%' OR arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '42%' OR arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '43%' OR arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '44%' OR arrayStringConcat(array(Recency, Frequency, Monetary), '') LIKE '45%') THEN 'Активные'
           ELSE 'Отток'
           END AS macrosegment, 

       CASE
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('525', '524', '523', '515', '514', '513', '425', '424', '423', '415', '414', '413') THEN 'Новички'
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('522', '521', '512', '511', '422', '421', '412', '411', '323', '322', '321', '313', '312', '311', '225', '224', '223', '222', '221', '215', '214', '213', '212', '211', '125', '124', '123', '122', '121', '115', '114', '113', '112', '111') THEN 'Случайные'
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('555', '554', '545', '544', '455', '454', '445', '444') THEN 'ВИП'
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('553', '543', '535', '534', '533', '453', '443', '435', '434', '433') THEN 'Хорошие'
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('552', '551', '542', '541', '532', '531', '452', '451', '442', '441', '432', '431') THEN 'Хорошие экономные'
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('355', '354', '353', '345', '344', '343', '335', '334', '333') THEN 'Уходящие хорошие'
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('352', '351', '342', '341', '332', '331') THEN 'Уходящие экономные'
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('232', '231', '132', '131') THEN 'Отток экономные'
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('253', '252', '251', '243', '242', '241', '235', '234', '233', '153', '152', '151', '143', '142', '141', '135', '134', '133') then 'Отток обычные'
           WHEN arrayStringConcat(array(Recency, Frequency, Monetary), '') IN ('325', '324', '315', '314', '255', '254', '245', '244', '155', '154', '145', '144') THEN 'Потерянные ВИП'
           END AS segment

FROM
-- Присваиваем кодировку для каждого из показателей R, F, M       
       (SELECT contact_id, 
              first_name,
              mobile_phone, 
              email, 
              favourite_restaurant,
              R_, F_, M_,

              CASE
                  WHEN (R <= R_20) THEN 5
                  WHEN (R > R_20 and R <= R_40) THEN 4
                  WHEN (R > R_40 and R <= R_60) THEN 3
                  WHEN (R > R_60 and R <= R_80) THEN 2
                  WHEN (R > R_80) THEN 1
                  END AS Recency,

              CASE
                  WHEN F < F_20 THEN 1
                  WHEN F < F_40 THEN 2
                  WHEN F < F_60 THEN 3
                  WHEN F < F_80 THEN 4
                  ELSE 5
                  END AS Frequency,

              CASE
                  WHEN M < M_20 THEN 1
                  WHEN M < M_40 THEN 2
                  WHEN M < M_60 THEN 3
                  WHEN M < M_80 THEN 4
                  ELSE 5
                  END AS Monetary

              FROM

-- Получаем контактные данные для каждого контакта, их мы потом хотим видеть в выгрузке после фильтрации по сегментам 
-- и макросегментам
              (SELECT contact_id,
                      dictGet('dwh.d_contact', 'first_name', cityHash64(contact_id, instance_id)) AS first_name,
                      dictGet('dwh.d_contact', 'sms', cityHash64(contact_id, instance_id)) AS mobile_phone,
                      dictGet('dwh.d_contact', 'email', cityHash64(contact_id, instance_id)) AS email,
                      dictGet('dwh.d_contact', 'freq_shop', cityHash64(contact_id, instance_id)) AS favourite_restaurant,
                      today() - max(toDate(dt)) AS R,
                      uniqExact(cheque_id) AS F,
                      sum(summdisc/100) AS M, 
                      today() - max(toDate(dt)) AS R_,
                      uniqExact(cheque_id) AS F_,
                      sum(summdisc/100) AS M_
               FROM dwh.chequeitems_retro
               WHERE contact_id<>0 AND is_del = 0
               GROUP BY contact_id, first_name, mobile_phone, email, favourite_restaurant) AS b_table

                CROSS JOIN

-- Получаем квантили для каждого из показателей: R, F, M
              (SELECT
                      round(quantile(0.2)(R),0) AS R_20,
                      round(quantile(0.4)(R),0) AS R_40,
                      round(quantile(0.6)(R),0) AS R_60,
                      round(quantile(0.8)(R),0) AS R_80,

                      round(quantile(0.2)(F),0) AS F_20,
                      round(quantile(0.4)(F),0) AS F_40,
                      round(quantile(0.6)(F),0) AS F_60,
                      round(quantile(0.8)(F),0) AS F_80,

                      round(quantile(0.2)(M),0) AS M_20,
                      round(quantile(0.4)(M),0) AS M_40,
                      round(quantile(0.6)(M),0) AS M_60,
                      round(quantile(0.8)(M),0) AS M_80

               FROM

-- Получаем данные о днях, прошедших с последнего визита (R), о количестве (F) и сумме (M) чеков для каждого контакта 
               (SELECT contact_id,
                       today() - max(toDate(dt)) AS R,
                       count (distinct cheque_id) AS F,
                       sum(summdisc/100) AS M
               FROM dwh.chequeitems_retro
               WHERE contact_id<>0 AND is_del = 0
               GROUP BY contact_id) AS basic_table) AS quantile_table

              GROUP BY contact_id, first_name, mobile_phone, email, favourite_restaurant, Recency, Frequency, Monetary, R_, F_, M_
              ORDER BY contact_id) AS final_table
