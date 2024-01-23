SELECT 
    cohort, 
    ROUND(SUM(qty_of_users/zero_day_users), 4) AS avg_lifetime_days
FROM 
    (
        SELECT 
            toStartOfMonth(first_shop_d) AS cohort,
            (last_shop_d - first_shop_d)::int AS days_diff, 
            COUNT(DISTINCT contact_id) AS qty_of_users
        FROM 
            dwh.contacts_info 
        WHERE 
            first_shop_d <> '1970-01-01'
        GROUP BY 
            cohort, days_diff
    ) AS cohort_table
LEFT JOIN
    (
        SELECT 
            toStartOfMonth(first_shop_d) AS cohort, 
            COUNT(DISTINCT contact_id) AS zero_day_users 
        FROM 
            dwh.contacts_info 
        WHERE 
            last_shop_d = first_shop_d AND first_shop_d <> '1970-01-01'
        GROUP BY 
            cohort
    ) AS zero_day_table
USING cohort
GROUP BY 
    cohort;