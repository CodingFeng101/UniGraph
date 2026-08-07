-- Scope resource names to their owner so independent users can reuse names.
ALTER TABLE kg_base
    DROP INDEX ix_kg_base_name,
    ADD CONSTRAINT uq_kg_base_user_name UNIQUE (user_uuid, name);

ALTER TABLE llm_provider
    MODIFY COLUMN api_key TEXT NULL COMMENT '加密后的 API 密钥',
    DROP INDEX name,
    ADD CONSTRAINT uq_llm_provider_user_name UNIQUE (user_uuid, name);

ALTER TABLE sys_user
    MODIFY COLUMN api_key TEXT NULL COMMENT '加密后的旧版 API Key';
