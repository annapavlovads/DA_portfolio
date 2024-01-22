SELECT toStartOfDay(toDateTime(bonus_date)) AS __timestamp,
       (SUM("Списано баллов") + sum("Баллов сгорело")) / sum("Начислено баллов") AS "Коэффициент использования баллов"
FROM
  (SELECT toStartOfMonth(toDateTime(d_created)) AS bonus_date,
          sumIf((value)/100, is_delete = 0
                and source_table = 1
                and oper_type = 'D') AS "Начислено баллов",
          ABS(sumIf((value)/100, is_delete = 0
                    and source_table = 2
                    and parent_type_id <> 6
                    and oper_type = 'C')) AS "Списано баллов",
          ABS(sumIf(value, is_delete = 0
                    and parent_type_id = 6)/100) AS "Баллов сгорело",
          sumIf((value)/100, is_delete = 0
                and source_table = 1
                and oper_type = 'D') - (ABS(sumIf((value)/100, is_delete = 0
                                                  and source_table = 2
                                                  and parent_type_id <> 6
                                                  and oper_type = 'C')) + ABS(sumIf(value, is_delete = 0
                                                                                    and parent_type_id = 6)/100)) as saldo
   FROM dwh.bonus_slim_retro
   WHERE is_delete = '0'
   GROUP BY toStartOfMonth(toDateTime(d_created))) AS virtual_table

GROUP BY toStartOfDay(toDateTime(bonus_date))
ORDER BY "Коэффициент использования баллов" DESC
