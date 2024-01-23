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