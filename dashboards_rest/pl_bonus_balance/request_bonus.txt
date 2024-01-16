SELECT shop_credit_name AS shop_credit_name,
       0 AS "Сальдо начальное",
       sum(value_debet) AS "Всего бонусов начислено", -sum(value_credit) AS "Всего бонусов списано", -sumIf(value_credit, shop_credit_name=shop_debet_name) AS "Своих бонусов списано", -sumIf(value_credit, shop_credit_name<>shop_debet_name) AS "Чужих бонусов списано",
                                                                                                                                                                                         (sum(value_debet)) - (-sum(value_credit)) AS "Всего начислено - Всего списано",
                                                                                                                                                                                         sum(value_debet) + sum(value_credit) AS "Сальдо конечное"
FROM
  (select bonus_id,
          toString(campaign_instance_hash) as campaign_instance_hash,
          if((value)>0, value, 0) as value_debet,
          if(shop_debet.2 = '', dictGet('dwh.d_shop', 'name', shop_debet.1), shop_debet.2) as shop_debet_name,
          if(arrayJoin(shops_values).4 = '', dictGet('dwh.d_shop', 'name', arrayJoin(shops_values).1), arrayJoin(shops_values).4) as shop_credit_name,
          if(value<0, arrayJoin(shops_values).2 as value, 0) as value_credit,
          arrayJoin(shops_values).3 as d_created
   from
     (SELECT bonus_id,
             campaign_instance_hash,
             dictGet('dwh.d_campaign', 'campaign_name', campaign_instance_hash) as campaign_name,
             (groupArrayIf(shop_instance_hash, (value/100)>0)[1], if(campaign_name in
                                                                       (SELECT name
                                                                        FROM dwh.shop)
                                                                     and groupArrayIf(parent_type_id, (value/100)>0)[1] = 3, campaign_name, '')) as shop_debet,
             groupArray((shop_instance_hash, value/100, d_created, if(campaign_name in
                                                                        (SELECT name
                                                                         FROM dwh.shop)
                                                                      and parent_type_id = 3, campaign_name, ''))) as shops_values
      from bonus_slim_retro
      where is_delete = 0
      group by bonus_id,
               campaign_instance_hash)) AS virtual_table
GROUP BY shop_credit_name
ORDER BY count(*) DESC