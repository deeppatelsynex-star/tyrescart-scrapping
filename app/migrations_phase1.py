import json
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from db import get_connection

PHASE1_TABLES = [
    # 1. Websites table
    """
    CREATE TABLE IF NOT EXISTS `websites` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `code` VARCHAR(50) NOT NULL UNIQUE,
        `name` VARCHAR(120) NOT NULL,
        `domain` VARCHAR(255) NULL,
        `default_store_id` BIGINT UNSIGNED NULL,
        `is_default` TINYINT(1) NOT NULL DEFAULT 0,
        `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
        `sort_order` INT UNSIGNED NOT NULL DEFAULT 0,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `deleted_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        `deleted_at` TIMESTAMP NULL DEFAULT NULL,
        INDEX `idx_websites_status` (`status`),
        INDEX `idx_websites_created_by` (`created_by`),
        INDEX `idx_websites_updated_by` (`updated_by`),
        INDEX `idx_websites_deleted_at` (`deleted_at`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 2. Store Views table (Locales)
    """
    CREATE TABLE IF NOT EXISTS `store_views` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `store_id` BIGINT UNSIGNED NOT NULL,
        `website_id` BIGINT UNSIGNED NOT NULL,
        `code` VARCHAR(50) NOT NULL,
        `name` VARCHAR(120) NOT NULL,
        `locale` VARCHAR(10) NOT NULL,
        `currency_code` VARCHAR(3) NOT NULL DEFAULT 'AED',
        `is_active` TINYINT(1) NOT NULL DEFAULT 1,
        `sort_order` INT UNSIGNED NOT NULL DEFAULT 0,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `deleted_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        `deleted_at` TIMESTAMP NULL DEFAULT NULL,
        UNIQUE KEY `uq_store_code` (`store_id`, `code`),
        INDEX `idx_store_views_website` (`website_id`, `locale`),
        INDEX `idx_store_views_created_by` (`created_by`),
        INDEX `idx_store_views_updated_by` (`updated_by`),
        INDEX `idx_store_views_deleted_at` (`deleted_at`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 3. Dynamic Attribute Sets table
    """
    CREATE TABLE IF NOT EXISTS `attribute_sets` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `name` VARCHAR(120) NOT NULL,
        `slug` VARCHAR(140) NOT NULL UNIQUE,
        `description` TEXT NULL,
        `is_system` TINYINT(1) NOT NULL DEFAULT 0,
        `sort_order` INT UNSIGNED NOT NULL DEFAULT 0,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `deleted_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        `deleted_at` TIMESTAMP NULL DEFAULT NULL,
        INDEX `idx_attr_sets_created_by` (`created_by`),
        INDEX `idx_attr_sets_updated_by` (`updated_by`),
        INDEX `idx_attr_sets_deleted_at` (`deleted_at`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 4. Dynamic Attribute Groups table
    """
    CREATE TABLE IF NOT EXISTS `attribute_groups` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `attribute_set_id` BIGINT UNSIGNED NOT NULL,
        `name` JSON NOT NULL,
        `code` VARCHAR(80) NOT NULL,
        `sort_order` INT UNSIGNED NOT NULL DEFAULT 0,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX `idx_attr_groups_set_id` (`attribute_set_id`),
        INDEX `idx_attr_groups_created_by` (`created_by`),
        INDEX `idx_attr_groups_updated_by` (`updated_by`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 5. Dynamic Attributes table (EAV Schema Definition with Scoping)
    """
    CREATE TABLE IF NOT EXISTS `attributes` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `code` VARCHAR(80) NOT NULL UNIQUE,
        `name` JSON NOT NULL,
        `type` ENUM('text', 'textarea', 'number', 'decimal', 'select', 'multiselect', 'boolean', 'color', 'date', 'file', 'json', 'rich_text') NOT NULL DEFAULT 'text',
        `scope` ENUM('global', 'website', 'store', 'store_view') NOT NULL DEFAULT 'global',
        `unit` VARCHAR(30) NULL,
        `default_value` TEXT NULL,
        `validation_rules` JSON NULL,
        `is_required` TINYINT(1) NOT NULL DEFAULT 0,
        `is_unique` TINYINT(1) NOT NULL DEFAULT 0,
        `is_filterable` TINYINT(1) NOT NULL DEFAULT 1,
        `is_searchable` TINYINT(1) NOT NULL DEFAULT 1,
        `is_comparable` TINYINT(1) NOT NULL DEFAULT 1,
        `is_visible_on_front` TINYINT(1) NOT NULL DEFAULT 1,
        `is_system` TINYINT(1) NOT NULL DEFAULT 0,
        `sort_order` INT UNSIGNED NOT NULL DEFAULT 0,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `deleted_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        `deleted_at` TIMESTAMP NULL DEFAULT NULL,
        INDEX `idx_attributes_code` (`code`),
        INDEX `idx_attributes_type` (`type`),
        INDEX `idx_attributes_scope` (`scope`),
        INDEX `idx_attributes_filterable` (`is_filterable`),
        INDEX `idx_attributes_created_by` (`created_by`),
        INDEX `idx_attributes_updated_by` (`updated_by`),
        INDEX `idx_attributes_deleted_at` (`deleted_at`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 6. Attribute Options table (for select / multiselect)
    """
    CREATE TABLE IF NOT EXISTS `attribute_options` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `attribute_id` BIGINT UNSIGNED NOT NULL,
        `value` VARCHAR(150) NOT NULL,
        `label` JSON NOT NULL,
        `swatch_value` VARCHAR(100) NULL,
        `sort_order` INT UNSIGNED NOT NULL DEFAULT 0,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX `idx_attr_options_attr_id` (`attribute_id`),
        INDEX `idx_attr_options_value` (`value`),
        INDEX `idx_attr_options_created_by` (`created_by`),
        INDEX `idx_attr_options_updated_by` (`updated_by`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 7. Attribute Group Pivot table
    """
    CREATE TABLE IF NOT EXISTS `attribute_group_attributes` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `attribute_group_id` BIGINT UNSIGNED NOT NULL,
        `attribute_id` BIGINT UNSIGNED NOT NULL,
        `sort_order` INT UNSIGNED NOT NULL DEFAULT 0,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY `uq_group_attribute` (`attribute_group_id`, `attribute_id`),
        INDEX `idx_group_attr_attr_id` (`attribute_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 8. Product Attribute Values (Scoped Typed EAV)
    """
    CREATE TABLE IF NOT EXISTS `product_attribute_values` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `product_id` BIGINT UNSIGNED NOT NULL,
        `attribute_id` BIGINT UNSIGNED NOT NULL,
        `website_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `store_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `store_view_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `value_text` TEXT NULL,
        `value_number` DECIMAL(12,4) NULL,
        `value_boolean` TINYINT(1) NULL DEFAULT NULL,
        `value_date` DATE NULL DEFAULT NULL,
        `value_json` JSON NULL,
        `option_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY `uq_prod_attr_scope` (`product_id`, `attribute_id`, `website_id`, `store_id`, `store_view_id`),
        INDEX `idx_pav_prod_attr` (`product_id`, `attribute_id`),
        INDEX `idx_pav_attr_num` (`attribute_id`, `value_number`),
        INDEX `idx_pav_attr_opt` (`attribute_id`, `option_id`),
        INDEX `idx_pav_scope` (`website_id`, `store_id`, `store_view_id`),
        INDEX `idx_pav_created_by` (`created_by`),
        INDEX `idx_pav_updated_by` (`updated_by`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 9. Scoped Product Prices Table
    """
    CREATE TABLE IF NOT EXISTS `product_prices` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `product_id` BIGINT UNSIGNED NOT NULL,
        `website_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `store_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `currency_code` VARCHAR(3) NOT NULL DEFAULT 'AED',
        `regular_price` DECIMAL(10,2) NOT NULL,
        `special_price` DECIMAL(10,2) NULL,
        `special_from` DATE NULL,
        `special_to` DATE NULL,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY `uq_prod_price_scope` (`product_id`, `website_id`, `store_id`, `currency_code`),
        INDEX `idx_prod_prices_lookup` (`product_id`, `website_id`, `store_id`),
        INDEX `idx_prod_prices_created_by` (`created_by`),
        INDEX `idx_prod_prices_updated_by` (`updated_by`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 10. Scoped Product Inventories Table
    """
    CREATE TABLE IF NOT EXISTS `product_inventories` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `product_id` BIGINT UNSIGNED NOT NULL,
        `store_id` BIGINT UNSIGNED NOT NULL,
        `warehouse_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `qty` INT NOT NULL DEFAULT 0,
        `min_qty` INT NOT NULL DEFAULT 0,
        `is_in_stock` TINYINT(1) NOT NULL DEFAULT 1,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY `uq_prod_inv_store` (`product_id`, `store_id`),
        INDEX `idx_prod_inv_stock` (`store_id`, `is_in_stock`, `qty`),
        INDEX `idx_prod_inv_created_by` (`created_by`),
        INDEX `idx_prod_inv_updated_by` (`updated_by`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 11. Product Websites Pivot
    """
    CREATE TABLE IF NOT EXISTS `product_websites` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `product_id` BIGINT UNSIGNED NOT NULL,
        `website_id` BIGINT UNSIGNED NOT NULL,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY `uq_prod_website` (`product_id`, `website_id`),
        INDEX `idx_pw_website` (`website_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 12. Product Stores Pivot
    """
    CREATE TABLE IF NOT EXISTS `product_stores` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `product_id` BIGINT UNSIGNED NOT NULL,
        `store_id` BIGINT UNSIGNED NOT NULL,
        `created_by` BIGINT UNSIGNED NULL,
        `updated_by` BIGINT UNSIGNED NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY `uq_prod_store` (`product_id`, `store_id`),
        INDEX `idx_ps_store` (`store_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 13. Admin User Websites Pivot
    """
    CREATE TABLE IF NOT EXISTS `admin_user_websites` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `admin_user_id` BIGINT UNSIGNED NOT NULL,
        `website_id` BIGINT UNSIGNED NOT NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY `uq_admin_website` (`admin_user_id`, `website_id`),
        INDEX `idx_auw_website` (`website_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 14. Admin User Stores Pivot
    """
    CREATE TABLE IF NOT EXISTS `admin_user_stores` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `admin_user_id` BIGINT UNSIGNED NOT NULL,
        `store_id` BIGINT UNSIGNED NOT NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY `uq_admin_store` (`admin_user_id`, `store_id`),
        INDEX `idx_aus_store` (`store_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,

    # 15. Activity / Modification Audit Log Table
    """
    CREATE TABLE IF NOT EXISTS `activity_logs` (
        `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `user_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `website_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `store_id` BIGINT UNSIGNED NULL DEFAULT NULL,
        `action` VARCHAR(50) NOT NULL,
        `entity_type` VARCHAR(80) NOT NULL,
        `entity_id` BIGINT UNSIGNED NOT NULL,
        `old_values` JSON NULL,
        `new_values` JSON NULL,
        `ip_address` VARCHAR(45) NULL,
        `user_agent` TEXT NULL,
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX `idx_act_user` (`user_id`),
        INDEX `idx_act_entity` (`entity_type`, `entity_id`),
        INDEX `idx_act_action` (`action`),
        INDEX `idx_act_scope` (`website_id`, `store_id`),
        INDEX `idx_act_created_at` (`created_at`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
]

ALTER_EXISTING_TABLES = [
    # Alter stores table
    ("stores", "website_id", "ALTER TABLE `stores` ADD COLUMN `website_id` BIGINT UNSIGNED NULL AFTER `id`"),
    ("stores", "code", "ALTER TABLE `stores` ADD COLUMN `code` VARCHAR(50) NULL AFTER `website_id`"),
    ("stores", "root_category_id", "ALTER TABLE `stores` ADD COLUMN `root_category_id` BIGINT UNSIGNED NULL"),
    ("stores", "default_store_view_id", "ALTER TABLE `stores` ADD COLUMN `default_store_view_id` BIGINT UNSIGNED NULL"),
    ("stores", "inventory_source_id", "ALTER TABLE `stores` ADD COLUMN `inventory_source_id` BIGINT UNSIGNED NULL"),
    ("stores", "deleted_by", "ALTER TABLE `stores` ADD COLUMN `deleted_by` BIGINT UNSIGNED NULL AFTER `deleted_at`"),

    # Alter products table
    ("products", "website_id", "ALTER TABLE `products` ADD COLUMN `website_id` BIGINT UNSIGNED NULL AFTER `id`"),
    ("products", "attribute_set_id", "ALTER TABLE `products` ADD COLUMN `attribute_set_id` BIGINT UNSIGNED NULL AFTER `website_id`"),
    ("products", "deleted_by", "ALTER TABLE `products` ADD COLUMN `deleted_by` BIGINT UNSIGNED NULL AFTER `deleted_at`"),
    ("products", "attributes_json", "ALTER TABLE `products` ADD COLUMN `attributes_json` JSON NULL AFTER `description`"),

    # Alter brands table
    ("brands", "deleted_by", "ALTER TABLE `brands` ADD COLUMN `deleted_by` BIGINT UNSIGNED NULL AFTER `deleted_at`"),

    # Alter categories table
    ("categories", "deleted_by", "ALTER TABLE `categories` ADD COLUMN `deleted_by` BIGINT UNSIGNED NULL AFTER `deleted_at`"),
    ("categories", "default_attribute_set_id", "ALTER TABLE `categories` ADD COLUMN `default_attribute_set_id` BIGINT UNSIGNED NULL"),

    # Alter orders table
    ("orders", "website_id", "ALTER TABLE `orders` ADD COLUMN `website_id` BIGINT UNSIGNED NULL AFTER `id`"),
    ("orders", "store_id", "ALTER TABLE `orders` ADD COLUMN `store_id` BIGINT UNSIGNED NULL AFTER `website_id`"),
    ("orders", "deleted_by", "ALTER TABLE `orders` ADD COLUMN `deleted_by` BIGINT UNSIGNED NULL AFTER `deleted_at`"),

    # Alter enquiries table
    ("enquiries", "website_id", "ALTER TABLE `enquiries` ADD COLUMN `website_id` BIGINT UNSIGNED NULL AFTER `id`"),
    ("enquiries", "deleted_by", "ALTER TABLE `enquiries` ADD COLUMN `deleted_by` BIGINT UNSIGNED NULL AFTER `deleted_at`"),

    # Alter admin_users table
    ("admin_users", "deleted_by", "ALTER TABLE `admin_users` ADD COLUMN `deleted_by` BIGINT UNSIGNED NULL AFTER `deleted_at`"),
    ("admin_users", "created_by", "ALTER TABLE `admin_users` ADD COLUMN `created_by` BIGINT UNSIGNED NULL AFTER `remember_token`"),
    ("admin_users", "updated_by", "ALTER TABLE `admin_users` ADD COLUMN `updated_by` BIGINT UNSIGNED NULL AFTER `created_by`"),
]


def run_phase1_migrations():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            print("🚀 Starting Phase 1 Schema Migrations...")

            # 1. Create new Phase 1 tables
            for ddl in PHASE1_TABLES:
                cursor.execute(ddl)
            print("✅ Created all Phase 1 multi-website, multi-store, and dynamic attribute tables.")

            # 2. Alter existing tables to add missing columns
            for table, col, alter_sql in ALTER_EXISTING_TABLES:
                cursor.execute(
                    "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
                    (table, col)
                )
                if not cursor.fetchone():
                    try:
                        cursor.execute(alter_sql)
                        print(f"  + Added column `{col}` to `{table}`")
                    except Exception as e:
                        print(f"  ! Error adding `{col}` to `{table}`: {e}")

            conn.commit()
            print("✅ Phase 1 schema migrations committed successfully!")
    finally:
        conn.close()


if __name__ == "__main__":
    run_phase1_migrations()
