
CREATE TABLE exp_assignment (
    user_id INT PRIMARY KEY,
    exp_group CHAR(1) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 使用 CRC32 哈希分组，完全独立于业务数据，且同一数据下可复现
INSERT INTO exp_assignment (user_id, exp_group)
SELECT 
    user_id,
    CASE WHEN MOD(CRC32(CONCAT('exp_v1_', user_id)), 100) < 60 THEN 'A' ELSE 'B' END
FROM users
WHERE first_login_date BETWEEN '2025-06-15' AND '2025-06-21';