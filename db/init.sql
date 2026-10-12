CREATE TABLE IF NOT EXISTS projects (
 id SERIAL PRIMARY KEY,
 name VARCHAR(160) NOT NULL,
 client VARCHAR(160) NOT NULL,
 category VARCHAR(40) NOT NULL DEFAULT 'Брендинг',
 status VARCHAR(30) NOT NULL DEFAULT 'В работе',
 deadline DATE,
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO projects (name, client, category, status, deadline) VALUES
 ('Фирменный стиль кофейни','Mellow Coffee','Брендинг','В работе',CURRENT_DATE+14),
 ('Дизайн Instagram-постов','Forma Studio','Соцсети','На проверке',CURRENT_DATE+7),
 ('Лендинг для агентства','North Agency','Веб-дизайн','Завершён',CURRENT_DATE-2);
