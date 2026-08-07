CREATE TABLE IF NOT EXISTS chat_share (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(50) NOT NULL UNIQUE,
    chat_library_uuid VARCHAR(50) NOT NULL UNIQUE,
    public_id VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    snapshot JSON NOT NULL,
    message_count INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_time DATETIME NOT NULL,
    updated_time DATETIME NULL,
    INDEX ix_chat_share_chat_library_uuid (chat_library_uuid),
    INDEX ix_chat_share_public_id (public_id),
    CONSTRAINT fk_chat_share_library
        FOREIGN KEY (chat_library_uuid) REFERENCES chat_library(uuid) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
