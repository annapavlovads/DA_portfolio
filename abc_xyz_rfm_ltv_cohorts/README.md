## RFM-анализ
`SQL` `Clickhouse` `Superset` `Python` `Pandas` `Seaborn` `Matplotlib` `Numpy` <br><br>
`RFM-анализ` был проведен для сегментации клиентов на основе их поведения. Такой анализ позволяет построить более персонализированное взаимодействие с клиентами, увидеть структуру клиентской базы и, предпринимая усилия по повышению "статуса" клиента в сегментах, увеличить прибыльность бизнеса. <br>
 
[RFM.ipynb](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/clients_rest/RFM_pandas/RFM_pandas.ipynb)<br><br>
[RFM SQL](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/clients_rest/RFM_sql/RFM_request.sql) | 
[Чарт Superset](https://drive.google.com/file/d/19gN3bHp19ePkfJJ2K1sd7dergSzEQlQO/view?usp=drive_link) | 
[Пример выгрузки RFM.xlsx](https://github.com/annapavlovads/DA_portfolio/raw/main/abc_xyz_rfm_ltv_cohorts/clients_rest/RFM_sql/sample_rfm_request.xlsx)<br><br>
[Стратегия и рекомендации по работе с сегментами](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/clients_rest/RFM_sql/RFM_advice.md)

## ABC- и XYZ-анализ
`Python` `Pandas` `Matplotlib` `Seaborn` <br><br>
[ABC.ipynb](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/goods_rest/ABC_pandas.ipynb) | 
[XYZ.ipynb](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/goods_rest/XYZ_pandas.ipynb) <br><br>
[Рекомендации по работе с группами](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/goods_rest/abc_xyz_advice.md)<br><br>

## Когортный анализ
`SQL` `Clickhouse` `Superset` <br><br>
[Дашборд "Когортный анализ"](https://drive.google.com/file/d/1dRhG_0Fvu3KK26tUaAO3wwXrvdwB_pNO/view?usp=drive_link)<br><br>
Когортный анализ отлично показывает окупаемость маркетинговых инвестиций, а также насколько маркетинговая стратегия вообще работает. И то, и другое очень важно для бизнеса. <br>

Примеры вопросов, на которые отвечает чарт активности пользователей и `RR`:
- Через сколько времени пользователи полностью перестают пользоваться продуктом?
- Какая доля клентов перестает осуществлять заказы через месяц? два? три?
- Кто пользуется продуктом дольше - пользователи, которые зарегистрировались в марте или в июне?

## Retention Rate
`SQL` `Clickhouse` `Superset` <br><br>
[Retention SQL](https://github.com/annapavlovads/DA_portfolio/blob/main/dashboards/pl_kpi/%D0%A1%D1%80%D0%B5%D0%B4%D0%BD%D0%B8%D0%B9%20RR-N-days.sql) 
| [Чарт Superset](https://drive.google.com/file/d/1ZIJYwojLrJBau7F94nrOYqO_GILulwRO/view?usp=drive_link)<br>
 
Расчет `Retention Rate` пользователей покогортно в днях был сделан для того, чтобы:
- оценить эффективность удержания клиентов (высокий `RR` свидетельствует о том, что клиенты возвращаются для повторных покупок, что может быть основой для увеличения прибыли)
- мониторинга эффективности рекламных кампаний (если `RR` оказывается низким в определенных когортах, это может указывать на проблемы с качеством лидов в этой когорте) 
- оценить долгосрочные тенденции в удержании клиентов, что может помочь в планировании будущих доходов и управлении рисками, связанными с оттоком клиентов <br>

## LTV
`SQL` `Clickhouse` `Superset` <br><br>
[LTV SQL](https://github.com/annapavlovads/DA_portfolio/blob/main/dashboards/pl_cohorts_db/ltv.sql) 
| [LTV-чарт](https://drive.google.com/file/d/1yGfa4xbtTKpSCLWajFtiSvCfnuH3j71q/view?usp=drive_link)<br>
 
Когортный анализ (чарт `LTV`) позволяет ответить на вопросы:
- сколько денег за все время принесли пользователи, совершившие первый заказ в феврале?
- сколько денег за первые полгода принесли пользователи, совершившие первый заказ в марте?
- какая группа клиентов принесла нам больше денег за полгода - те, что пришли по рекламной кампании от июня или другой рекламы от июля?

## Lifetime
`SQL` `Clickhouse` `Superset` <br><br>
[Lifetime.sql](https://github.com/annapavlovads/DA_portfolio/blob/main/abc_xyz_rfm_ltv_cohorts/clients_rest/cohorts_lifetime_sql/lifetime_days.sql) |
[Чарт Superset](https://drive.google.com/file/d/1yIfqzxUtB88kXQVqtG85gJ8tGoULVbNR/view?usp=drive_link)<br>
 
Расчет `lifetime` пользователей покогортно был проведен для: 
- оценки эффективности маркетинговых кампаний, как показатель того, насколько успешно и устойчиво новые клиенты удерживаются в продукте (если `lifetime` увеличивается с течением времени, это может свидетельствовать о том, что маркетинговые усилия компании направлены на более качественных клиентов, что может привести к увеличению доходов).
- планирования бюджета маркетинга: используя `lifetime` можно прогнозировать доход от каждой когорты и определить, сколько нужно инвестировать в удержание клиентов и привлечение новых
- выявления факторов, влияющих на удержание клиентов (например, если `lifetime` внезапно сокращается в какой-то когорте, необходимо провести дополнительный анализ, чтобы выявить причины и приступить к их устранению) <br>

## Sticky Factor
`SQL` `Clickhouse` `Superset` <br><br>
[Sticky Factor - SQL](https://github.com/annapavlovads/DA_portfolio/blob/main/dashboards/pl_kpi/%D0%94%D0%B8%D0%BD%D0%B0%D0%BC%D0%B8%D0%BA%D0%B0%20Sticky%20Factor.sql) | [StickyFactor - чарт](https://drive.google.com/file/d/1P4sWCA-KW-7XKQ_kl5599zgt4IWrsD0V/view?usp=drive_link) <br>

Расчет `Sticky Factor` для пользователей покогортно проводился для построения чарта на дашборде об активности клиентской базы, он помогает понять:
- уровень вовлеченности пользователей в продукт: насколько активно и регулярно клиенты используют продукт (совершают заказы). Высокий (в отношении "принятого" исторически или по отрасли) `Sticky Factor` указывает высокую лояльность и удовлетворенность продуктом. Низкий `Sticky Factor`, напротив, может указывать на проблемы с удержанием клиентов и потенциальные возможности для улучшения уровня вовлеченности.
- оценки качества пользователей покогортно / оценки качества маркетинговых кампаний <br>
