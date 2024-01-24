## RFM-сегментация
`SQL` `Clickhouse` `Superset` `Python` `Pandas` `Seaborn` `Matplotlib` `Numpy` <br><br>
[RFM.ipynb](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm/clients_rest/RFM_pandas/RFM_pandas.ipynb) <br><br>
[RFM SQL](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/clients_rest/RFM_sql/RFM_request.sql) | 
[Чарт Superset](https://drive.google.com/file/d/19gN3bHp19ePkfJJ2K1sd7dergSzEQlQO/view?usp=drive_link) | 
[Пример выгрузки RFM.xlsx](https://github.com/annapavlovads/DA_portfolio/raw/main/abc_xyz_rfm/clients_rest/RFM_sql/sample_rfm_request.xlsx) <br><br>
[Стратегия и рекомендации по работе с сегментами](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/clients_rest/RFM_sql/RFM_advice.md)

## ABC-анализ
`Python` `Pandas` `Matplotlib` `Seaborn` <br><br>
[ABC.ipynb](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm/goods_rest/ABC_pandas.ipynb)<br><br>

## XYZ-анализ
`Python` `Pandas` `Matplotlib` `Seaborn` <br><br>
[XYZ.ipynb](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm/goods_rest/XYZ_pandas.ipynb)

## Когортный анализ
`SQL` `Clickhouse` `Superset` <br><br>
[Когорты - количество пользователей](https://github.com/annapavlovads/DA_portfolio/blob/main/dashboards/pl_cohorts_db/cohorts_clients_qty.sql) | [Когорты - средний чек](https://github.com/annapavlovads/DA_portfolio/blob/main/dashboards/pl_cohorts_db/cohorts_avg_cheque.sql)
| [Дашборд "Когортный анализ"](https://drive.google.com/file/d/1dRhG_0Fvu3KK26tUaAO3wwXrvdwB_pNO/view?usp=drive_link)

## Retention Rate
`SQL` `Clickhouse` `Superset` <br><br>
[Retention SQL](https://github.com/annapavlovads/DA_portfolio/blob/main/dashboards/pl_kpi/%D0%A1%D1%80%D0%B5%D0%B4%D0%BD%D0%B8%D0%B9%20RR-N-days.sql) 
| [Чарт Superset]()<br><br> 
Расчет `Retention Rate` пользователей покогортно в днях был сделан для того, чтобы:
- оценить эффективность удержания клиентов (высокий `RR` свидетельствует о том, что клиенты возвращаются для повторных покупок, что может быть основой для увеличения прибыли)
- мониторинга эффективности рекламных кампаний (если `RR` оказывается низким в определенных когортах, это может указывать на проблемы с качеством лидов в этой когорте) 
- оценить долгосрочные тенденции в удержании клиентов, что может помочь в планировании будущих доходов и управлении рисками, связанными с оттоком клиентов <br>

## LTV
`SQL` `Clickhouse` `Superset` <br><br>
[LTV SQL](https://github.com/annapavlovads/DA_portfolio/blob/main/dashboards/pl_cohorts_db/ltv.sql) 
| [LTV-чарт](https://drive.google.com/file/d/1yGfa4xbtTKpSCLWajFtiSvCfnuH3j71q/view?usp=drive_link)<br><br>

## Sticky Factor
`SQL` `Clickhouse` `Superset` <br><br>
[Sticky Factor SQL](https://github.com/annapavlovads/DA_portfolio/blob/main/dashboards/pl_kpi/%D0%94%D0%B8%D0%BD%D0%B0%D0%BC%D0%B8%D0%BA%D0%B0%20Sticky%20Factor.sql) 
| [StickyFactor-чарт](https://drive.google.com/file/d/1P4sWCA-KW-7XKQ_kl5599zgt4IWrsD0V/view?usp=drive_link) <br><br>

Расчет `Sticky Factor` для пользователей покогортно проводился для построения чарта на дашборде об активности клиентской базы, он помогает понять:
- уровень вовлеченности пользователей в продукт: насколько активно и регулярно клиенты используют продукт (совершают заказы). Высокий (в отношении "принятого" исторически или по отрасли) `Sticky Factor` указывает высокую лояльность и удовлетворенность продуктом. Низкий `Sticky Factor`, напротив, может указывать на проблемы с удержанием клиентов и потенциальные возможности для улучшения уровня вовлеченности.
- оценки качества пользователей покогортно / оценки качества маркетинговых кампаний <br>

## Метрики рассылок
`SQL` `Clickhouse` `Superset` <br><br>
[Метрики E-mail-рассылки]() | [Чарт Superset]() <br><br>

## Lifetime
`SQL` `Clickhouse` `Superset` <br><br>
[Lifetime.sql](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/clients_rest/cohorts_lifetime_sql/lifetime_days.sql) |
[Чарт Superset](https://drive.google.com/file/d/1yIfqzxUtB88kXQVqtG85gJ8tGoULVbNR/view?usp=drive_link)
<br><br>
Расчет `lifetime` пользователей покогортно был проведен для: 
- оценки эффективности маркетинговых кампаний, как показатель того, насколько успешно и устойчиво новые клиенты удерживаются в продукте (если `lifetime` увеличивается с течением времени, это может свидетельствовать о том, что маркетинговые усилия компании направлены на более качественных клиентов, что может привести к увеличению доходов).
- планирования бюджета маркетинга: используя `ifetime` можно прогнозировать доход от каждой когорты и определить, сколько нужно инвестировать в удержание клиентов и привлечение новых
- выявления факторов, влияющих на удержание клиентов (например, если `lifetime` внезапно сокращается в какой-то когорте, необходимо провести дополнительный анализ, чтобы выявить причины и приступить к их устранению) <br>
