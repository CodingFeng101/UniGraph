-- MySQL dump 10.13  Distrib 8.4.2, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: dockerunigraph
-- ------------------------------------------------------
-- Server version	8.4.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `chat_library`
--

DROP TABLE IF EXISTS `chat_library`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_library` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `uuid` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL COMMENT 'Chat Message Name',
  `kg_base_uuid` varchar(50) NOT NULL,
  `messages` json DEFAULT NULL,
  `is_favorite` tinyint(1) NOT NULL DEFAULT '0',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `kg_base_uuid` (`kg_base_uuid`),
  KEY `ix_chat_library_id` (`id`),
  CONSTRAINT `chat_library_ibfk_1` FOREIGN KEY (`kg_base_uuid`) REFERENCES `kg_base` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chat_message`
--

DROP TABLE IF EXISTS `chat_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_message` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL,
  `chat_library_uuid` varchar(50) NOT NULL,
  `role` varchar(20) NOT NULL,
  `content` text NOT NULL,
  `sequence` int NOT NULL DEFAULT '0',
  `knowledge_graph_uuid` varchar(50) DEFAULT NULL,
  `model_name` varchar(100) DEFAULT NULL,
  `effort` varchar(20) DEFAULT NULL,
  `created_time` datetime NOT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `ix_chat_message_chat_library_uuid` (`chat_library_uuid`),
  CONSTRAINT `fk_chat_message_library` FOREIGN KEY (`chat_library_uuid`) REFERENCES `chat_library` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chat_message_source`
--

DROP TABLE IF EXISTS `chat_message_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_message_source` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL,
  `message_uuid` varchar(50) NOT NULL,
  `source_type` varchar(32) NOT NULL,
  `content` json NOT NULL,
  `position` int NOT NULL DEFAULT '0',
  `created_time` datetime NOT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `ix_chat_message_source_message_uuid` (`message_uuid`),
  CONSTRAINT `fk_chat_message_source_message` FOREIGN KEY (`message_uuid`) REFERENCES `chat_message` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `chat_share`
--

DROP TABLE IF EXISTS `chat_share`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_share` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL,
  `chat_library_uuid` varchar(50) NOT NULL,
  `public_id` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `snapshot` json NOT NULL,
  `message_count` int NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_time` datetime NOT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `chat_library_uuid` (`chat_library_uuid`),
  UNIQUE KEY `public_id` (`public_id`),
  CONSTRAINT `fk_chat_share_library` FOREIGN KEY (`chat_library_uuid`) REFERENCES `chat_library` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `community`
--

DROP TABLE IF EXISTS `community`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `community` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `knowledge_graph_uuid` varchar(50) NOT NULL,
  `uuid` varchar(50) NOT NULL,
  `title` text NOT NULL COMMENT '标题',
  `level` text NOT NULL COMMENT '等级',
  `content` text NOT NULL COMMENT '内容',
  `rating` text NOT NULL COMMENT '评分',
  `attributes` text,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `knowledge_graph_uuid` (`knowledge_graph_uuid`),
  KEY `ix_community_id` (`id`),
  CONSTRAINT `community_ibfk_1` FOREIGN KEY (`knowledge_graph_uuid`) REFERENCES `knowledge_graph` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=264 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `community_entity_map`
--

DROP TABLE IF EXISTS `community_entity_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `community_entity_map` (
  `community_id` int NOT NULL,
  `knowledge_entity_id` int NOT NULL,
  PRIMARY KEY (`community_id`,`knowledge_entity_id`),
  KEY `knowledge_entity_id` (`knowledge_entity_id`),
  CONSTRAINT `community_entity_map_ibfk_1` FOREIGN KEY (`community_id`) REFERENCES `community` (`id`) ON DELETE CASCADE,
  CONSTRAINT `community_entity_map_ibfk_2` FOREIGN KEY (`knowledge_entity_id`) REFERENCES `knowledge_entity` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kg_base`
--

DROP TABLE IF EXISTS `kg_base`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kg_base` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `user_uuid` varchar(50) NOT NULL,
  `uuid` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL COMMENT '名',
  `status` int NOT NULL COMMENT '状态(0停用 1正常)',
  `cover_image` varchar(255) DEFAULT NULL COMMENT '头像',
  `description` text COMMENT '描述',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `ix_kg_base_name` (`name`),
  KEY `user_uuid` (`user_uuid`),
  KEY `ix_kg_base_id` (`id`),
  CONSTRAINT `kg_base_ibfk_1` FOREIGN KEY (`user_uuid`) REFERENCES `sys_user` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_entity`
--

DROP TABLE IF EXISTS `knowledge_entity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_entity` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `knowledge_graph_uuid` varchar(50) NOT NULL,
  `uuid` varchar(50) NOT NULL,
  `name` text NOT NULL COMMENT '实体名称',
  `type` text NOT NULL COMMENT '实体类型',
  `attributes` text NOT NULL COMMENT '实体属性',
  `status` int NOT NULL COMMENT '状态(0停用 1正常)',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `knowledge_graph_uuid` (`knowledge_graph_uuid`),
  KEY `ix_knowledge_entity_id` (`id`),
  CONSTRAINT `knowledge_entity_ibfk_1` FOREIGN KEY (`knowledge_graph_uuid`) REFERENCES `knowledge_graph` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=149 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_graph`
--

DROP TABLE IF EXISTS `knowledge_graph`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_graph` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `uuid` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL COMMENT 'Knowledge Graph Name',
  `kg_base_uuid` varchar(50) NOT NULL,
  `schema_graph_uuid` varchar(50) NOT NULL,
  `index_status` varchar(50) NOT NULL DEFAULT '0' COMMENT 'Index Status',
  `depth` int NOT NULL COMMENT 'Depth',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `kg_base_uuid` (`kg_base_uuid`),
  KEY `schema_graph_uuid` (`schema_graph_uuid`),
  KEY `ix_knowledge_graph_id` (`id`),
  CONSTRAINT `knowledge_graph_ibfk_1` FOREIGN KEY (`kg_base_uuid`) REFERENCES `kg_base` (`uuid`) ON DELETE CASCADE,
  CONSTRAINT `knowledge_graph_ibfk_2` FOREIGN KEY (`schema_graph_uuid`) REFERENCES `schema_graph` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `knowledge_relationship`
--

DROP TABLE IF EXISTS `knowledge_relationship`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_relationship` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `source_entity_uuid` varchar(50) DEFAULT NULL,
  `target_entity_uuid` varchar(50) DEFAULT NULL,
  `knowledge_graph_uuid` varchar(50) NOT NULL,
  `uuid` varchar(50) NOT NULL,
  `name` text NOT NULL COMMENT '关系名称',
  `type` text NOT NULL COMMENT '关系类型',
  `attributes` text NOT NULL COMMENT '关系属性',
  `source` text NOT NULL COMMENT '三元组的源信息',
  `status` int NOT NULL COMMENT '状态(0停用 1正常)',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `source_entity_uuid` (`source_entity_uuid`),
  KEY `target_entity_uuid` (`target_entity_uuid`),
  KEY `knowledge_graph_uuid` (`knowledge_graph_uuid`),
  KEY `ix_knowledge_relationship_id` (`id`),
  CONSTRAINT `knowledge_relationship_ibfk_1` FOREIGN KEY (`source_entity_uuid`) REFERENCES `knowledge_entity` (`uuid`) ON DELETE CASCADE,
  CONSTRAINT `knowledge_relationship_ibfk_2` FOREIGN KEY (`target_entity_uuid`) REFERENCES `knowledge_entity` (`uuid`) ON DELETE CASCADE,
  CONSTRAINT `knowledge_relationship_ibfk_3` FOREIGN KEY (`knowledge_graph_uuid`) REFERENCES `knowledge_graph` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `llm_model`
--

DROP TABLE IF EXISTS `llm_model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `llm_model` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `type` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `group_name` varchar(100) DEFAULT NULL,
  `status` int DEFAULT '1',
  `provider_uuid` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `provider_uuid` (`provider_uuid`),
  CONSTRAINT `llm_model_ibfk_1` FOREIGN KEY (`provider_uuid`) REFERENCES `llm_provider` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=420 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `llm_provider`
--

DROP TABLE IF EXISTS `llm_provider`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `llm_provider` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `user_uuid` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `api_key` varchar(255) DEFAULT NULL,
  `api_url` varchar(512) DEFAULT NULL,
  `document_url` varchar(512) DEFAULT NULL,
  `status` int DEFAULT '1',
  `llm_model_url` varchar(512) DEFAULT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `user_uuid` (`user_uuid`),
  CONSTRAINT `llm_provider_ibfk_1` FOREIGN KEY (`user_uuid`) REFERENCES `sys_user` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=141 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schema_entity`
--

DROP TABLE IF EXISTS `schema_entity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schema_entity` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `schema_graph_uuid` varchar(50) NOT NULL,
  `uuid` varchar(50) NOT NULL,
  `name` text NOT NULL COMMENT '实体名',
  `type` varchar(255) DEFAULT NULL,
  `definition` varchar(255) DEFAULT NULL,
  `attributes` text NOT NULL COMMENT '实体属性',
  `source` text NOT NULL COMMENT '实体类型来源',
  `status` int NOT NULL COMMENT '状态(0停用 1正常)',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `schema_graph_uuid` (`schema_graph_uuid`),
  KEY `ix_schema_entity_id` (`id`),
  CONSTRAINT `schema_entity_ibfk_1` FOREIGN KEY (`schema_graph_uuid`) REFERENCES `schema_graph` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schema_graph`
--

DROP TABLE IF EXISTS `schema_graph`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schema_graph` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `uuid` varchar(50) NOT NULL,
  `kg_base_uuid` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL COMMENT 'Schema Graph Name',
  `aim` text COMMENT '目标描述',
  `modify_info` text COMMENT '修改信息',
  `modify_suggestion` text COMMENT '修改建议',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `kg_base_uuid` (`kg_base_uuid`),
  KEY `ix_schema_graph_id` (`id`),
  CONSTRAINT `schema_graph_ibfk_1` FOREIGN KEY (`kg_base_uuid`) REFERENCES `kg_base` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schema_relationship`
--

DROP TABLE IF EXISTS `schema_relationship`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schema_relationship` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `source_entity_uuid` varchar(50) NOT NULL,
  `target_entity_uuid` varchar(50) NOT NULL,
  `schema_graph_uuid` varchar(50) NOT NULL,
  `uuid` varchar(50) NOT NULL,
  `name` text NOT NULL COMMENT '关系名称',
  `type` text NOT NULL COMMENT '关系类型',
  `attributes` text NOT NULL COMMENT '关系属性',
  `definition` varchar(255) DEFAULT NULL,
  `source` text NOT NULL COMMENT '关系类型来源',
  `status` int NOT NULL COMMENT '状态(0停用 1正常)',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `source_entity_uuid` (`source_entity_uuid`),
  KEY `target_entity_uuid` (`target_entity_uuid`),
  KEY `schema_graph_uuid` (`schema_graph_uuid`),
  KEY `ix_schema_relationship_id` (`id`),
  CONSTRAINT `schema_relationship_ibfk_1` FOREIGN KEY (`source_entity_uuid`) REFERENCES `schema_entity` (`uuid`) ON DELETE CASCADE,
  CONSTRAINT `schema_relationship_ibfk_2` FOREIGN KEY (`target_entity_uuid`) REFERENCES `schema_entity` (`uuid`) ON DELETE CASCADE,
  CONSTRAINT `schema_relationship_ibfk_3` FOREIGN KEY (`schema_graph_uuid`) REFERENCES `schema_graph` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_api`
--

DROP TABLE IF EXISTS `sys_api`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_api` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `name` varchar(50) NOT NULL COMMENT 'api名称',
  `method` varchar(16) NOT NULL COMMENT '请求方法',
  `path` varchar(500) NOT NULL COMMENT 'api路径',
  `remark` longtext COMMENT '备注',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_sys_api_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_casbin_rule`
--

DROP TABLE IF EXISTS `sys_casbin_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_casbin_rule` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `ptype` varchar(255) NOT NULL COMMENT '策略类型: p / g',
  `v0` varchar(255) NOT NULL COMMENT '角色ID / 用户uuid',
  `v1` longtext NOT NULL COMMENT 'api路径 / 角色名称',
  `v2` varchar(255) DEFAULT NULL COMMENT '请求方法',
  `v3` varchar(255) DEFAULT NULL,
  `v4` varchar(255) DEFAULT NULL,
  `v5` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_sys_casbin_rule_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_config`
--

DROP TABLE IF EXISTS `sys_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_config` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `login_title` varchar(20) NOT NULL COMMENT '登录页面标题',
  `login_sub_title` varchar(50) NOT NULL COMMENT '登录页面子标题',
  `footer` varchar(50) NOT NULL COMMENT '页脚标题',
  `logo` longtext NOT NULL COMMENT 'Logo',
  `system_title` varchar(20) NOT NULL COMMENT '系统标题',
  `system_comment` longtext NOT NULL COMMENT '系统描述',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_sys_config_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_dept`
--

DROP TABLE IF EXISTS `sys_dept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_dept` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `name` varchar(50) NOT NULL COMMENT '部门名称',
  `level` int NOT NULL COMMENT '部门层级',
  `sort` int NOT NULL COMMENT '排序',
  `leader` varchar(20) DEFAULT NULL COMMENT '负责人',
  `phone` varchar(11) DEFAULT NULL COMMENT '手机',
  `email` varchar(50) DEFAULT NULL COMMENT '邮箱',
  `status` int NOT NULL COMMENT '部门状态(0停用 1正常)',
  `del_flag` tinyint(1) NOT NULL COMMENT '删除标志（0删除 1存在）',
  `parent_id` int DEFAULT NULL COMMENT '父部门ID',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  `worklogStandard` text COMMENT '工作日志标准',
  `control` text COMMENT '约束',
  PRIMARY KEY (`id`),
  KEY `ix_sys_dept_id` (`id`),
  KEY `ix_sys_dept_parent_id` (`parent_id`),
  CONSTRAINT `sys_dept_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `sys_dept` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_dict_data`
--

DROP TABLE IF EXISTS `sys_dict_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_dict_data` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `label` varchar(32) NOT NULL COMMENT '字典标签',
  `value` varchar(32) NOT NULL COMMENT '字典值',
  `sort` int NOT NULL COMMENT '排序',
  `status` int NOT NULL COMMENT '状态（0停用 1正常）',
  `remark` longtext COMMENT '备注',
  `type_id` int NOT NULL COMMENT '字典类型关联ID',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `label` (`label`),
  UNIQUE KEY `value` (`value`),
  KEY `type_id` (`type_id`),
  KEY `ix_sys_dict_data_id` (`id`),
  CONSTRAINT `sys_dict_data_ibfk_1` FOREIGN KEY (`type_id`) REFERENCES `sys_dict_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_dict_type`
--

DROP TABLE IF EXISTS `sys_dict_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_dict_type` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `name` varchar(32) NOT NULL COMMENT '字典类型名称',
  `code` varchar(32) NOT NULL COMMENT '字典类型编码',
  `status` int NOT NULL COMMENT '状态（0停用 1正常）',
  `remark` longtext COMMENT '备注',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`),
  KEY `ix_sys_dict_type_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_gen_business`
--

DROP TABLE IF EXISTS `sys_gen_business`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_gen_business` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `app_name` varchar(50) NOT NULL COMMENT '应用名称（英文）',
  `table_name_en` varchar(255) NOT NULL COMMENT '表名称（英文）',
  `table_name_zh` varchar(255) NOT NULL COMMENT '表名称（中文）',
  `table_simple_name_zh` varchar(255) NOT NULL COMMENT '表名称（中文简称）',
  `table_comment` varchar(255) DEFAULT NULL COMMENT '表描述',
  `schema_name` varchar(255) DEFAULT NULL COMMENT 'Schema 名称 (默认为英文表驼峰)',
  `have_datetime_column` tinyint(1) NOT NULL COMMENT '是否存在默认时间列',
  `api_version` varchar(20) NOT NULL COMMENT '代码生成 api 版本，默认为 v1',
  `gen_path` varchar(255) DEFAULT NULL COMMENT '代码生成路径（默认为 app 根路径）',
  `remark` longtext COMMENT '备注',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `table_name_en` (`table_name_en`),
  KEY `ix_sys_gen_business_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_gen_model`
--

DROP TABLE IF EXISTS `sys_gen_model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_gen_model` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `name` varchar(50) NOT NULL COMMENT '列名称',
  `comment` varchar(255) DEFAULT NULL COMMENT '列描述',
  `type` varchar(20) NOT NULL COMMENT '列类型',
  `default` varchar(50) DEFAULT NULL COMMENT '列默认值',
  `sort` int DEFAULT NULL COMMENT '列排序',
  `length` int NOT NULL COMMENT '列长度',
  `is_pk` tinyint(1) NOT NULL COMMENT '是否主键',
  `is_nullable` tinyint(1) NOT NULL COMMENT '是否可为空',
  `gen_business_id` int NOT NULL COMMENT '代码生成业务ID',
  PRIMARY KEY (`id`),
  KEY `gen_business_id` (`gen_business_id`),
  KEY `ix_sys_gen_model_id` (`id`),
  CONSTRAINT `sys_gen_model_ibfk_1` FOREIGN KEY (`gen_business_id`) REFERENCES `sys_gen_business` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_login_log`
--

DROP TABLE IF EXISTS `sys_login_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_login_log` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `user_uuid` varchar(50) NOT NULL COMMENT '用户UUID',
  `username` varchar(20) NOT NULL COMMENT '用户名',
  `status` int NOT NULL COMMENT '登录状态(0失败 1成功)',
  `ip` varchar(50) NOT NULL COMMENT '登录IP地址',
  `country` varchar(50) DEFAULT NULL COMMENT '国家',
  `region` varchar(50) DEFAULT NULL COMMENT '地区',
  `city` varchar(50) DEFAULT NULL COMMENT '城市',
  `user_agent` varchar(255) NOT NULL COMMENT '请求头',
  `os` varchar(50) DEFAULT NULL COMMENT '操作系统',
  `browser` varchar(50) DEFAULT NULL COMMENT '浏览器',
  `device` varchar(50) DEFAULT NULL COMMENT '设备',
  `msg` longtext NOT NULL COMMENT '提示消息',
  `login_time` datetime NOT NULL COMMENT '登录时间',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_sys_login_log_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=75 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_menu`
--

DROP TABLE IF EXISTS `sys_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_menu` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `title` varchar(50) NOT NULL COMMENT '菜单标题',
  `name` varchar(50) NOT NULL COMMENT '菜单名称',
  `level` int NOT NULL COMMENT '菜单层级',
  `sort` int NOT NULL COMMENT '排序',
  `icon` varchar(100) DEFAULT NULL COMMENT '菜单图标',
  `path` varchar(200) DEFAULT NULL COMMENT '路由地址',
  `menu_type` int NOT NULL COMMENT '菜单类型（0目录 1菜单 2按钮）',
  `component` varchar(255) DEFAULT NULL COMMENT '组件路径',
  `perms` varchar(100) DEFAULT NULL COMMENT '权限标识',
  `status` int NOT NULL COMMENT '菜单状态（0停用 1正常）',
  `show` int NOT NULL COMMENT '是否显示（0否 1是）',
  `cache` int NOT NULL COMMENT '是否缓存（0否 1是）',
  `remark` longtext COMMENT '备注',
  `parent_id` int DEFAULT NULL COMMENT '父菜单ID',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_sys_menu_id` (`id`),
  KEY `ix_sys_menu_parent_id` (`parent_id`),
  CONSTRAINT `sys_menu_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `sys_menu` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_opera_log`
--

DROP TABLE IF EXISTS `sys_opera_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_opera_log` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `trace_id` varchar(32) NOT NULL COMMENT '请求跟踪ID',
  `username` varchar(20) DEFAULT NULL COMMENT '用户名',
  `method` varchar(20) NOT NULL COMMENT '请求类型',
  `title` varchar(255) NOT NULL COMMENT '操作模块',
  `path` varchar(500) NOT NULL COMMENT '请求路径',
  `ip` varchar(50) NOT NULL COMMENT 'IP地址',
  `country` varchar(50) DEFAULT NULL COMMENT '国家',
  `region` varchar(50) DEFAULT NULL COMMENT '地区',
  `city` varchar(50) DEFAULT NULL COMMENT '城市',
  `user_agent` varchar(255) NOT NULL COMMENT '请求头',
  `os` varchar(50) DEFAULT NULL COMMENT '操作系统',
  `browser` varchar(50) DEFAULT NULL COMMENT '浏览器',
  `device` varchar(50) DEFAULT NULL COMMENT '设备',
  `args` json DEFAULT NULL COMMENT '请求参数',
  `status` int NOT NULL COMMENT '操作状态（0异常 1正常）',
  `code` varchar(20) NOT NULL COMMENT '操作状态码',
  `msg` longtext COMMENT '提示消息',
  `cost_time` float NOT NULL COMMENT '请求耗时ms',
  `opera_time` datetime NOT NULL COMMENT '操作时间',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `ix_sys_opera_log_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3626 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_role`
--

DROP TABLE IF EXISTS `sys_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_role` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `name` varchar(20) NOT NULL COMMENT '角色名称',
  `data_scope` int DEFAULT NULL COMMENT '权限范围（1：全部数据权限 2：自定义数据权限）',
  `status` int NOT NULL COMMENT '角色状态（0停用 1正常）',
  `remark` longtext COMMENT '备注',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_sys_role_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_role_menu`
--

DROP TABLE IF EXISTS `sys_role_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_role_menu` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `role_id` int NOT NULL COMMENT '角色ID',
  `menu_id` int NOT NULL COMMENT '菜单ID',
  PRIMARY KEY (`id`,`role_id`,`menu_id`),
  UNIQUE KEY `ix_sys_role_menu_id` (`id`),
  KEY `role_id` (`role_id`),
  KEY `menu_id` (`menu_id`),
  CONSTRAINT `sys_role_menu_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sys_role_menu_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `sys_menu` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user`
--

DROP TABLE IF EXISTS `sys_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `uuid` varchar(50) NOT NULL,
  `username` varchar(20) NOT NULL COMMENT '用户名',
  `nickname` varchar(20) NOT NULL COMMENT '昵称',
  `password` varchar(255) DEFAULT NULL COMMENT '密码',
  `salt` varchar(5) DEFAULT NULL COMMENT '加密盐',
  `email` varchar(50) NOT NULL COMMENT '邮箱',
  `is_superuser` tinyint(1) NOT NULL COMMENT '超级权限(0否 1是)',
  `is_staff` tinyint(1) NOT NULL COMMENT '后台管理登陆(0否 1是)',
  `status` int NOT NULL COMMENT '用户账号状态(0停用 1正常)',
  `is_multi_login` tinyint(1) NOT NULL COMMENT '是否重复登陆(0否 1是)',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像',
  `phone` varchar(11) DEFAULT NULL COMMENT '手机号',
  `join_time` datetime NOT NULL COMMENT '注册时间',
  `last_login_time` datetime DEFAULT NULL COMMENT '上次登录',
  `dept_id` int DEFAULT NULL COMMENT '部门关联ID',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  `api_key` varchar(255) DEFAULT NULL COMMENT 'api_key',
  `base_url` varchar(255) DEFAULT NULL COMMENT 'base_url',
  `model` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `nickname` (`nickname`),
  UNIQUE KEY `ix_sys_user_email` (`email`),
  UNIQUE KEY `ix_sys_user_username` (`username`),
  KEY `dept_id` (`dept_id`),
  KEY `ix_sys_user_id` (`id`),
  CONSTRAINT `sys_user_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `sys_dept` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user_dept`
--

DROP TABLE IF EXISTS `sys_user_dept`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_dept` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `dept_id` int NOT NULL COMMENT '部门ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`dept_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `sys_user_dept_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sys_user_dept_ibfk_2` FOREIGN KEY (`dept_id`) REFERENCES `sys_dept` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user_role`
--

DROP TABLE IF EXISTS `sys_user_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_role` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` int NOT NULL COMMENT '用户ID',
  `role_id` int NOT NULL COMMENT '角色ID',
  PRIMARY KEY (`id`,`user_id`,`role_id`),
  UNIQUE KEY `ix_sys_user_role_id` (`id`),
  KEY `user_id` (`user_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `sys_user_role_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sys_user_role_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user_social`
--

DROP TABLE IF EXISTS `sys_user_social`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_social` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `source` varchar(20) NOT NULL COMMENT '第三方用户来源',
  `open_id` varchar(20) DEFAULT NULL COMMENT '第三方用户的 open id',
  `uid` varchar(20) DEFAULT NULL COMMENT '第三方用户的 ID',
  `union_id` varchar(20) DEFAULT NULL COMMENT '第三方用户的 union id',
  `scope` varchar(120) DEFAULT NULL COMMENT '第三方用户授予的权限',
  `code` varchar(50) DEFAULT NULL COMMENT '用户的授权 code',
  `user_id` int DEFAULT NULL COMMENT '用户关联ID',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_sys_user_social_id` (`id`),
  CONSTRAINT `sys_user_social_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `uni_embedding`
--

DROP TABLE IF EXISTS `uni_embedding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `uni_embedding` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `uuid` varchar(50) NOT NULL,
  `vector` longtext,
  `knowledge_entity_uuid` varchar(50) NOT NULL COMMENT '关联的知识实体ID',
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `knowledge_entity_uuid` (`knowledge_entity_uuid`),
  KEY `ix_embedding_id` (`id`),
  CONSTRAINT `uni_embedding_ibfk_1` FOREIGN KEY (`knowledge_entity_uuid`) REFERENCES `knowledge_entity` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=628 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `worklog`
--

DROP TABLE IF EXISTS `worklog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `worklog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(32) NOT NULL,
  `user_uuid` varchar(36) DEFAULT NULL,
  `group_uuid` varchar(32) NOT NULL,
  `content` text,
  `task` text,
  `solution` text,
  `effect` text,
  `create_datetime` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `active` tinyint(1) DEFAULT NULL,
  `embedding` blob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `idx_worklog_uuid` (`uuid`),
  KEY `idx_worklog_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-29 15:45:50
