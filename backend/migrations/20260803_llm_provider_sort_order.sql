ALTER TABLE llm_provider
    ADD COLUMN sort_order INT NOT NULL DEFAULT 0 COMMENT '用户自定义排序，值越小越靠前';

UPDATE llm_provider
SET sort_order = id;
