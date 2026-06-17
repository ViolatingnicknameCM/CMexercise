CREATE TABLE login_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    login_date DATE NOT NULL,
    session_duration INT  -- 在线时长(秒)
);

--

-- 为每个用户生成注册后 0~7 天的登录日志，概率有差异
INSERT INTO login_logs (user_id, login_date, session_duration)
SELECT 
    u.user_id,
    DATE_ADD(u.first_login_date, INTERVAL d.day_offset DAY) AS login_date,
    -- 随机时长：大部分 100~3600 秒，少数更短
    FLOOR(100 + RAND() * 3500) AS session_duration
FROM users u
CROSS JOIN (
    SELECT 0 AS day_offset UNION SELECT 1 UNION SELECT 2 UNION SELECT 3
    UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7
) d  -- 生成未来 0~7 天的日期候选
WHERE 
    -- 只保留“应该登录”的日期，通过概率控制
    (
        CASE 
            -- 注册当天（day=0）：90% 的人会登录
            WHEN d.day_offset = 0 THEN RAND() < 0.9
            -- 次日（day=1）：抖音渠道留存率低，故意设为 20%；其他渠道 45%
            WHEN d.day_offset = 1 THEN
                CASE WHEN u.channel = '抖音' THEN RAND() < 0.20
                     ELSE RAND() < 0.45
                END
            -- 第2~7天：抖音用户留存更低，其他渠道稍高
            ELSE
                CASE WHEN u.channel = '抖音' THEN RAND() < 0.10
                     ELSE RAND() < 0.25
                END
        END
    );
