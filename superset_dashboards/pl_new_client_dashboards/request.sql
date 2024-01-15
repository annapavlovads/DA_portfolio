SELECT "Ресторан первой покупки" AS "Ресторан первой покупки",
       count(DISTINCT contact_id) AS "Кол-во гостей"
FROM
  (SELECT contact_id,
          registration_d,
          first_shop_id,
          dictGet('dwh.d_shop', 'name', cityHash64(first_shop_id, instance_id)) as "Ресторан первой покупки"
   FROM dwh.contacts_info) AS virtual_table
WHERE (first_shop_id <> 0)
GROUP BY "Ресторан первой покупки"
ORDER BY "Кол-во гостей" DESC