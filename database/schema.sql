USE defaultdb;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SHOW TABLES;

SELECT * FROM users;

SELECT * FROM chat_messages;

INSERT INTO chat_messages (user_message, ai_response)
VALUES (
    'Tell me about Thilitshi',
    'Thilitshi is a BSc Computer Science graduate from the University of the Western Cape.'
);

SELECT *FROM chat_messages;

DELETE FROM chat_messages
WHERE id in(1,2,3,4);



SELECT * FROM chat_messages;

DELETE FROM chat_messages
WHERE id  =25;

ALTER TABLE chat_messages AUTO_INCREMENT = 1;
/*esay way to del everything*/
TRUNCATE TABLE chat_messages;
