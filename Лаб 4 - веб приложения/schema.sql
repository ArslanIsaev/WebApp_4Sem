CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    last_name VARCHAR(100),
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    role_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

INSERT INTO roles (name, description) VALUES
    ('Администратор', 'Полный доступ к системе'),
    ('Пользователь', 'Обычный пользователь');

INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id)
VALUES ('admin', 'pbkdf2:sha256:600000$placeholder', 'Иванов', 'Иван', 'Иванович', 1);
