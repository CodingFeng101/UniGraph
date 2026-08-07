-- MySQL 8.4 does not provide a portable ADD COLUMN IF NOT EXISTS form.
-- Use INFORMATION_SCHEMA so this migration is safe to run more than once.
SET @add_is_favorite = (
    SELECT IF(
        COUNT(*) = 0,
        'ALTER TABLE chat_library ADD COLUMN is_favorite BOOLEAN NOT NULL DEFAULT FALSE',
        'SELECT 1'
    )
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'chat_library'
      AND COLUMN_NAME = 'is_favorite'
);
PREPARE add_is_favorite_stmt FROM @add_is_favorite;
EXECUTE add_is_favorite_stmt;
DEALLOCATE PREPARE add_is_favorite_stmt;

CREATE TABLE IF NOT EXISTS chat_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(50) NOT NULL UNIQUE,
    chat_library_uuid VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sequence INT NOT NULL DEFAULT 0,
    knowledge_graph_uuid VARCHAR(50) NULL,
    model_name VARCHAR(100) NULL,
    effort VARCHAR(20) NULL,
    created_time DATETIME NOT NULL,
    updated_time DATETIME NULL,
    INDEX ix_chat_message_chat_library_uuid (chat_library_uuid),
    CONSTRAINT fk_chat_message_library
        FOREIGN KEY (chat_library_uuid) REFERENCES chat_library(uuid) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chat_message_source (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(50) NOT NULL UNIQUE,
    message_uuid VARCHAR(50) NOT NULL,
    source_type VARCHAR(32) NOT NULL,
    content JSON NOT NULL,
    position INT NOT NULL DEFAULT 0,
    created_time DATETIME NOT NULL,
    updated_time DATETIME NULL,
    INDEX ix_chat_message_source_message_uuid (message_uuid),
    CONSTRAINT fk_chat_message_source_message
        FOREIGN KEY (message_uuid) REFERENCES chat_message(uuid) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
