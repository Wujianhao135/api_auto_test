-- ============================================================
-- FastAPI 电商服务建表脚本（阶段 2.1）
-- 数据库：shop，字符集 utf8mb4
-- 用法：mysql -uroot -p < sql/shop.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS `shop`
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE `shop`;

-- ---------- 1. 用户表（登录用）----------
DROP TABLE IF EXISTS `shop_user`;
CREATE TABLE `shop_user` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username`    VARCHAR(50)  NOT NULL COMMENT '登录账号',
  `password`    VARCHAR(100) NOT NULL COMMENT '密码（哈希存储）',
  `nickname`    VARCHAR(50)  DEFAULT NULL COMMENT '昵称',
  `status`      TINYINT      DEFAULT 1 COMMENT '状态：1正常 0停用',
  `create_time` DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='电商用户表';

-- ---------- 2. 商品表 ----------
DROP TABLE IF EXISTS `shop_product`;
CREATE TABLE `shop_product` (
  `id`          BIGINT        NOT NULL AUTO_INCREMENT COMMENT '商品ID',
  `name`        VARCHAR(100)  NOT NULL COMMENT '商品名称',
  `price`       DECIMAL(10,2) NOT NULL COMMENT '单价',
  `stock`       INT           NOT NULL DEFAULT 0 COMMENT '库存数量',
  `status`      TINYINT       NOT NULL DEFAULT 1 COMMENT '状态：1上架 0下架',
  `description` VARCHAR(500)  DEFAULT NULL COMMENT '商品描述',
  `create_time` DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- ---------- 3. 订单表 ----------
DROP TABLE IF EXISTS `shop_order`;
CREATE TABLE `shop_order` (
  `id`           BIGINT        NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `order_no`     VARCHAR(32)   NOT NULL COMMENT '订单编号（业务唯一）',
  `user_id`      BIGINT        NOT NULL COMMENT '下单用户ID',
  `total_amount` DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
  `status`       TINYINT       NOT NULL DEFAULT 0 COMMENT '状态：0待支付 1已支付 2已取消',
  `create_time`  DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `pay_time`     DATETIME      DEFAULT NULL COMMENT '支付时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- ---------- 4. 订单项表 ----------
DROP TABLE IF EXISTS `shop_order_item`;
CREATE TABLE `shop_order_item` (
  `id`           BIGINT        NOT NULL AUTO_INCREMENT COMMENT '订单项ID',
  `order_id`     BIGINT        NOT NULL COMMENT '所属订单ID',
  `product_id`   BIGINT        NOT NULL COMMENT '商品ID',
  `product_name` VARCHAR(100)  NOT NULL COMMENT '下单时商品名（快照）',
  `quantity`     INT           NOT NULL COMMENT '购买数量',
  `price`        DECIMAL(10,2) NOT NULL COMMENT '下单时单价（快照）',
  PRIMARY KEY (`id`),
  KEY `idx_order_id` (`order_id`),
  CONSTRAINT `fk_item_order` FOREIGN KEY (`order_id`) REFERENCES `shop_order` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单项表';

-- ---------- 5. 支付记录表 ----------
DROP TABLE IF EXISTS `shop_payment_record`;
CREATE TABLE `shop_payment_record` (
  `id`             BIGINT        NOT NULL AUTO_INCREMENT COMMENT '支付记录ID',
  `order_no`       VARCHAR(32)   NOT NULL COMMENT '订单编号',
  `pay_amount`     DECIMAL(10,2) NOT NULL COMMENT '支付金额',
  `pay_status`     TINYINT       NOT NULL COMMENT '支付状态：1成功 0失败',
  `transaction_id` VARCHAR(64)   DEFAULT NULL COMMENT '第三方交易流水号',
  `create_time`    DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_order_no` (`order_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付记录表';
