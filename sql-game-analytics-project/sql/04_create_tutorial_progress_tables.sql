--用来做漏斗分析，同样嵌入异常：让第 3 步的完成率突然变低。

CREATE TABLE tutorial_progress (
    progress_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    step_id INT NOT NULL,   -- 1~5 步
    complete_date DATE
);

--

INSERT INTO tutorial_progress (user_id, step_id, complete_date)
SELECT 
    u.user_id,
    s.step_id,
    u.first_login_date  -- 都记录在注册当天完成步骤
FROM users u
CROSS JOIN (
    SELECT 1 AS step_id UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5
) s
WHERE
    -- 模拟漏斗：步骤1 90%完成，步骤2 80%，步骤3 故意降低到40%，步骤4 60%，步骤5 50%
    (s.step_id = 1 AND RAND() < 0.90) OR
    (s.step_id = 2 AND RAND() < 0.80) OR
    (s.step_id = 3 AND RAND() < 0.40) OR  -- 问题步骤
    (s.step_id = 4 AND RAND() < 0.60) OR
    (s.step_id = 5 AND RAND() < 0.50);
