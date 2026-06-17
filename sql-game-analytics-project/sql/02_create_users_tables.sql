CREATE TABLE users (
    user_id INT PRIMARY KEY,
    first_login_date DATE NOT NULL,
    channel VARCHAR(20) NOT NULL
);

--

INSERT INTO users (user_id, first_login_date, channel)
SELECT 
    n AS user_id,
    -- 随机生成 2025-06-01 ~ 2025-06-30 的日期
    DATE_ADD('2025-06-01', INTERVAL FLOOR(RAND() * 30) DAY) AS first_login_date,
    -- 用 CASE WHEN 将随机数映射为渠道
    CASE 
        WHEN (RAND() * 100) < 40 THEN '应用商店'   -- 40%
        WHEN (RAND() * 100) < 70 THEN '信息流广告'  -- 30%
        WHEN (RAND() * 100) < 90 THEN '抖音'        -- 20%
        ELSE '其他'                                 -- 10%
    END AS channel
FROM numbers
WHERE n <= 5000;  -- 只取 5000 个用户

