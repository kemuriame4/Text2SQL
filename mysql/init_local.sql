SET NAMES utf8mb4;
-- ==========================================
-- 1. 创建元数据库 (meta) 并初始化四张核心表
-- ==========================================
CREATE DATABASE IF NOT EXISTS `meta` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `meta`;
CREATE TABLE IF NOT EXISTS `t_table_info` (
  `id` varchar(32) COLLATE utf8mb4_general_ci NOT NULL COMMENT '主键',
  `name` varchar(64) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '名称',
  `role` char(1) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '角色 0:维度表  1:事实表',
  `description` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '描述',
  `del_flag` char(1) COLLATE utf8mb4_general_ci DEFAULT '0' COMMENT '是否删除 0 未删除  1 已删除',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_by` varchar(64) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建者',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_by` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '修改者',
  PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '表信息';
CREATE TABLE IF NOT EXISTS `t_column_info` (
  `id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '列编号',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '列名称',
  `type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '数据类型',
  `role` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '列类型(primary_key,foreign_key,measure,dimension)',
  `examples` json DEFAULT NULL COMMENT '数据示例',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '列描述',
  `alias` json DEFAULT NULL COMMENT '列别名',
  `table_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '所属表编号',
  `del_flag` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '0' COMMENT '是否删除 0 未删除  1 已删除',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建者',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_by` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '修改者',
  PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '字段信息';
CREATE TABLE IF NOT EXISTS `t_metric_info` (
  `id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '指标编码',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '指标名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '指标描述',
  `relevant_columns` json DEFAULT NULL COMMENT '关联的列',
  `alias` json DEFAULT NULL COMMENT '指标别名',
  `del_flag` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '0' COMMENT '是否删除 0 未删除  1 已删除',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建者',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_by` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '修改者',
  PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '指标信息';
CREATE TABLE IF NOT EXISTS `t_column_metric` (
  `column_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '列编号',
  `metric_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '指标编号',
  `del_flag` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '0' COMMENT '是否删除 0 未删除  1 已删除',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_by` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建者',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_by` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '修改者',
  PRIMARY KEY (`column_id`, `metric_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '字段与指标关联表';
-- ==========================================
-- 2. 创建数仓业务库 (dw) 并初始化示例业务表和样例数据
-- ==========================================
CREATE DATABASE IF NOT EXISTS `dw` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `dw`;
-- 地区维度表
CREATE TABLE IF NOT EXISTS `dim_region` (
  `region_id` varchar(32) NOT NULL PRIMARY KEY COMMENT '地区ID',
  `province` varchar(64) DEFAULT NULL COMMENT '省份',
  `city` varchar(64) DEFAULT NULL COMMENT '城市',
  `region_name` varchar(64) DEFAULT NULL COMMENT '大区名称',
  `country` varchar(64) DEFAULT '中国' COMMENT '国家'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '地区维度表';
INSERT INTO `dim_region`
VALUES ('REG001', '广东省', '深圳市', '华南', '中国'),
  ('REG002', '广东省', '广州市', '华南', '中国'),
  ('REG003', '上海市', '上海市', '华东', '中国'),
  ('REG004', '浙江省', '杭州市', '华东', '中国'),
  ('REG005', '北京市', '北京市', '华北', '中国') ON DUPLICATE KEY
UPDATE `region_name` =
VALUES(`region_name`);
-- 客户维度表
CREATE TABLE IF NOT EXISTS `dim_customer` (
  `customer_id` varchar(32) NOT NULL PRIMARY KEY COMMENT '客户ID',
  `customer_name` varchar(64) DEFAULT NULL COMMENT '客户姓名',
  `gender` varchar(16) DEFAULT NULL COMMENT '性别',
  `member_level` varchar(32) DEFAULT NULL COMMENT '会员等级'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '客户维度表';
INSERT INTO `dim_customer`
VALUES ('CUST001', '张三', '男', '钻石会员'),
  ('CUST002', '李四', '女', '黄金会员'),
  ('CUST003', '王五', '男', '白银会员'),
  ('CUST004', '赵六', '女', '普通会员') ON DUPLICATE KEY
UPDATE `customer_name` =
VALUES(`customer_name`);
-- 商品维度表
CREATE TABLE IF NOT EXISTS `dim_product` (
  `product_id` varchar(32) NOT NULL PRIMARY KEY COMMENT '商品ID',
  `product_name` varchar(128) DEFAULT NULL COMMENT '商品名称',
  `category` varchar(64) DEFAULT NULL COMMENT '品类',
  `brand` varchar(64) DEFAULT NULL COMMENT '品牌',
  `unit` varchar(16) DEFAULT '件' COMMENT '单位',
  `price` decimal(10, 2) DEFAULT '0.00' COMMENT '单价'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '商品维度表';
INSERT INTO `dim_product`
VALUES ('PROD001', '无线降噪耳机', '数码影音', '索尼', '台', 1299.00),
  ('PROD002', '机械键盘', '电脑办公', '罗技', '把', 599.00),
  ('PROD003', '人体工学椅', '办公家具', '保友', '张', 2199.00),
  ('PROD004', '4K显示器', '电脑配件', '戴尔', '台', 2499.00) ON DUPLICATE KEY
UPDATE `product_name` =
VALUES(`product_name`);
-- 日期维度表
CREATE TABLE IF NOT EXISTS `dim_date` (
  `date_id` varchar(16) NOT NULL PRIMARY KEY COMMENT '日期ID (yyyyMMdd)',
  `year` int DEFAULT NULL COMMENT '年份',
  `quarter` varchar(16) DEFAULT NULL COMMENT '季度',
  `month` int DEFAULT NULL COMMENT '月份',
  `day` int DEFAULT NULL COMMENT '日'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '日期维度表';
INSERT INTO `dim_date`
VALUES ('20240401', 2024, '第二季度', 4, 1),
  ('20240415', 2024, '第二季度', 4, 15),
  ('20240501', 2024, '第二季度', 5, 1),
  ('20240618', 2024, '第二季度', 6, 18),
  ('20240701', 2024, '第三季度', 7, 1) ON DUPLICATE KEY
UPDATE `quarter` =
VALUES(`quarter`);
-- 订单事实表
CREATE TABLE IF NOT EXISTS `fact_order` (
  `order_id` varchar(32) NOT NULL PRIMARY KEY COMMENT '订单ID',
  `customer_id` varchar(32) DEFAULT NULL COMMENT '客户ID',
  `product_id` varchar(32) DEFAULT NULL COMMENT '商品ID',
  `date_id` varchar(16) DEFAULT NULL COMMENT '下单日期ID',
  `region_id` varchar(32) DEFAULT NULL COMMENT '地区ID',
  `order_quantity` int DEFAULT 1 COMMENT '订单销量',
  `order_amount` decimal(12, 2) DEFAULT '0.00' COMMENT '订单金额'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '订单事实表';
INSERT INTO `fact_order`
VALUES (
    'ORD1001',
    'CUST001',
    'PROD001',
    '20240401',
    'REG001',
    2,
    2598.00
  ),
  (
    'ORD1002',
    'CUST002',
    'PROD002',
    '20240415',
    'REG003',
    1,
    599.00
  ),
  (
    'ORD1003',
    'CUST003',
    'PROD003',
    '20240501',
    'REG004',
    1,
    2199.00
  ),
  (
    'ORD1004',
    'CUST001',
    'PROD004',
    '20240618',
    'REG001',
    1,
    2499.00
  ),
  (
    'ORD1005',
    'CUST004',
    'PROD001',
    '20240701',
    'REG005',
    3,
    3897.00
  ) ON DUPLICATE KEY
UPDATE `order_amount` =
VALUES(`order_amount`);