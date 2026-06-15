-- ============================================================
-- clear_data.sql — Xóa toàn bộ dữ liệu nghiệp vụ (giữ lại tài khoản đăng nhập)
-- Dùng khi muốn bàn giao ứng dụng "sạch" để người dùng tự import Excel.
-- KHÔNG xóa bảng `users` => tài khoản admin vẫn đăng nhập được.
-- Cách chạy:  mysql -u root -p project_mgmt < database/clear_data.sql
-- ============================================================
USE project_mgmt;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE allocation_history_monthly;
TRUNCATE TABLE allocation_history;
TRUNCATE TABLE monthly_allocations;
TRUNCATE TABLE resource_allocations;
TRUNCATE TABLE tasks;
TRUNCATE TABLE milestones;
TRUNCATE TABLE products;
TRUNCATE TABLE project_groups;
TRUNCATE TABLE customers;
TRUNCATE TABLE employees;
TRUNCATE TABLE departments;
TRUNCATE TABLE phases;

SET FOREIGN_KEY_CHECKS = 1;
