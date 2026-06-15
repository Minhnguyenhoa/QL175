-- Tạo database
CREATE DATABASE IF NOT EXISTS project_mgmt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE project_mgmt;

-- Dữ liệu mẫu từ file Excel

-- Customers (DS Khách hàng)
INSERT IGNORE INTO customers (investor_code, investor_name, beneficiary_code, beneficiary_name, project_group_code) VALUES
('H05', 'Cục Công nghệ thông tin', 'H06', 'Cục Y tế', 'H05YTS');

-- Project Groups (DS Dự án - level đề án)
INSERT IGNORE INTO project_groups (code, name, director, customer_id) VALUES
('H05YTS', 'Ứng dụng CNTT trong quản lý y tế, quản lý bệnh viện, bệnh xá ngành công an', NULL, 1);

-- Products (DS Dự án - level sản phẩm)
INSERT IGNORE INTO products (code, name, project_group_id, pm, start_date, end_date, status, current_phase, has_work_plan) VALUES
('HIS',    'Phần mềm quản lý bệnh viện',                                          1, 'Hoàng Ngọc Sỹ', '2025-11-20', '2026-09-15', 'Warning', 'Kiểm thử nội bộ, Pilot', true),
('LIS',    'Phần mềm quản lý xét nghiệm',                                         1, 'Hoàng Ngọc Sỹ', '2025-11-20', '2026-09-15', 'Warning', 'Kiểm thử nội bộ, Pilot', true),
('EMR',    'Phần mềm quản lý lưu trữ và khai thác bệnh án điện tử',               1, 'Hoàng Ngọc Sỹ', '2025-11-20', '2026-09-15', 'Warning', 'Kiểm thử nội bộ, Pilot', true),
('KSK',    'Phần mềm quản lý lưu trữ và khai thác hồ sơ khám sức khỏe CBCS',    1, 'Hoàng Ngọc Sỹ', '2025-11-20', '2026-09-15', 'Warning', 'Kiểm thử nội bộ, Pilot', false),
('QLTTDL', 'Phần mềm quản lý trung tâm dữ liệu y tế',                            1, 'Hoàng Ngọc Sỹ', '2025-11-20', '2026-09-15', 'Warning', 'Kiểm thử nội bộ, Pilot', false),
('THDB',   'Phần mềm quản lý tích hợp đồng bộ dữ liệu',                          1, 'Hoàng Ngọc Sỹ', '2025-11-20', '2026-09-15', 'Warning', 'Kiểm thử nội bộ, Pilot', true);

-- Employees (Tổ chức nhân sự)
INSERT IGNORE INTO employees (name, company, department, contract_type, work_mode, work_time) VALUES
('Hoàng Ngọc Sỹ',          'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Nguyễn Duy Thảo',        'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Nguyễn Ngọc Tân',        'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Đặng Văn Kiên',          'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Đặng Như Quỳnh',         'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Lại Thùy Linh',          'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Nguyễn Anh Đức',         'MIGI',       NULL,   'Outsourcing',  'GTel Site', 'Full-time'),
('Nguyễn Minh Tú',         'MIGI',       NULL,   'Outsourcing',  'GTel Site', 'Full-time'),
('Nguyễn Thanh Hằng',      'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Phạm Thị Tuyết Chinh',   'AGILETECH',  NULL,   'Outsourcing',  'GTel Site', 'Full-time'),
('Trần Thị Phương Anh',    'MIGI',       NULL,   'Outsourcing',  'GTel Site', 'Full-time'),
('Trần Thu Trang',         'ALADIN',     NULL,   'Outsourcing',  'GTel Site', 'Full-time'),
('Vũ Duy Khánh',           'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Vũ Thị Hồng Loan',       'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Chu Nguyên Chương',      'VISSOFT',    NULL,   'Outsourcing',  'GTel Site', 'Full-time'),
('Chu Văn Vinh',           'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Hoàng Văn Học',          'VISSOFT',    NULL,   'Outsourcing',  'GTel Site', 'Full-time'),
('Ngô Văn Phương',         'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Nguyễn Đức Mạnh',        'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time'),
('Bùi Đức Hiếu',           'GTEL ICT',   'PM 1', 'Chính thức',   'GTel Site', 'Full-time');

-- Phases (Config sheet)
INSERT IGNORE INTO phases (phase_group, phase_name, note, sort_order) VALUES
('Tiền dự án', 'Đề xuất',                                              NULL, 1),
('Tiền dự án', 'Khảo sát',                                             NULL, 2),
('Tiền dự án', 'Thuyết minh sơ bộ phần mềm',                          'Một số trường hợp cần PoC', 3),
('Tiền dự án', 'Xây dựng báo cáo nghiên cứu kinh tế & chủ trương ĐT', NULL, 4),
('Tiền dự án', 'Thầu',                                                 NULL, 5),
('Tiền dự án', 'Ký Hợp đồng',                                         NULL, 6),
('Sản xuất',   'Chưa bắt đầu',                                        NULL, 7),
('Sản xuất',   'Kickoff',                                              NULL, 8),
('Sản xuất',   'Khảo sát',                                             NULL, 9),
('Sản xuất',   'Phân tích yêu cầu nghiệp vụ',                         NULL, 10),
('Sản xuất',   'Coding',                                               NULL, 11),
('Sản xuất',   'Kiểm thử nội bộ',                                     NULL, 12),
('Sản xuất',   'Pilot',                                                NULL, 13),
('Sản xuất',   'UAT',                                                  NULL, 14),
('Sản xuất',   'Golive',                                               NULL, 15);

-- Allocation History (Sheet 10 - Phân bổ nguồn lực_Old format)
-- Format: one row per person, comma-separated projects, 100% total allocation
-- Monthly percent = working-day fraction (e.g. 0.5238 = joined mid-month)
INSERT IGNORE INTO allocation_history (employee_name, projects_text, role_in_project, from_date, to_date, allocation_percent) VALUES
('Hoàng Ngọc Sỹ',        'HIS, LIS, EMR, KSK, QLTTDL, THDB', '1. PO, 2. PM', '2025-06-15', '2026-05-30', 1.0000),
('Nguyễn Duy Thảo',      'HIS, LIS, EMR, KSK, QLTTDL',       'SA',           '2025-12-01', '2026-05-30', 1.0000),
('Nguyễn Ngọc Tân',      'HIS, LIS, EMR',                     'Dev',          '2025-08-01', '2026-09-15', 1.0000),
('Đặng Văn Kiên',        'HIS, EMR',                          'Dev',          '2025-09-01', '2026-09-15', 1.0000),
('Đặng Như Quỳnh',       'LIS, KSK',                          'QA/Test',      '2025-07-01', '2026-06-30', 1.0000),
('Lại Thùy Linh',        'HIS, LIS, EMR, KSK, QLTTDL, THDB', 'BA',           '2025-06-15', '2026-05-30', 1.0000),
('Nguyễn Anh Đức',       'HIS',                               'Dev',          '2025-10-01', '2026-09-15', 1.0000),
('Nguyễn Minh Tú',       'HIS',                               'Dev',          '2025-10-01', '2026-09-15', 1.0000),
('Nguyễn Thanh Hằng',    'HIS, LIS, EMR, KSK, QLTTDL, THDB', 'BA/QA',        '2025-06-15', '2026-05-30', 1.0000),
('Phạm Thị Tuyết Chinh', 'EMR, KSK',                          'Dev',          '2025-11-01', '2026-06-30', 1.0000),
('Trần Thị Phương Anh',  'HIS',                               'Dev',          '2025-10-01', '2026-09-15', 1.0000),
('Trần Thu Trang',       'LIS, THDB',                         'Dev',          '2025-11-01', '2026-06-30', 1.0000),
('Vũ Duy Khánh',         'HIS, QLTTDL',                       'Dev',          '2025-09-01', '2026-09-15', 1.0000),
('Vũ Thị Hồng Loan',     'HIS, LIS, EMR',                     'QA/Test',      '2025-07-01', '2026-05-30', 1.0000),
('Chu Nguyên Chương',    'HIS',                               'Dev',          '2025-12-01', '2026-09-15', 1.0000),
('Chu Văn Vinh',         'HIS, EMR, THDB',                    'Dev',          '2025-09-01', '2026-09-15', 1.0000),
('Hoàng Văn Học',        'HIS',                               'Dev',          '2025-12-01', '2026-09-15', 1.0000),
('Ngô Văn Phương',       'QLTTDL, THDB',                      'Dev',          '2025-11-01', '2026-05-30', 1.0000),
('Nguyễn Đức Mạnh',      'HIS, LIS',                          'Dev',          '2025-08-01', '2026-09-15', 1.0000),
('Bùi Đức Hiếu',         'HIS',                               'Dev',          '2025-10-01', '2026-09-15', 1.0000);

-- Monthly allocations for AllocationHistory row 1 (Hoàng Ngọc Sỹ, 2025-06-15 to 2026-05-30)
INSERT IGNORE INTO allocation_history_monthly (history_id, `year_month`, `percent`) VALUES
(1, 'T6-2025', 0.5238),
(1, 'T7-2025', 1.0000),
(1, 'T8-2025', 1.0000),
(1, 'T9-2025', 1.0000),
(1, 'T10-2025', 1.0000),
(1, 'T11-2025', 1.0000),
(1, 'T12-2025', 1.0000),
(1, 'T1-2026', 1.0000),
(1, 'T2-2026', 1.0000),
(1, 'T3-2026', 1.0000),
(1, 'T4-2026', 1.0000),
(1, 'T5-2026', 1.0000);

-- Row 2 (Nguyễn Duy Thảo, 2025-12-01 to 2026-05-30)
INSERT IGNORE INTO allocation_history_monthly (history_id, `year_month`, `percent`) VALUES
(2, 'T12-2025', 1.0000),
(2, 'T1-2026', 1.0000),
(2, 'T2-2026', 1.0000),
(2, 'T3-2026', 1.0000),
(2, 'T4-2026', 1.0000),
(2, 'T5-2026', 1.0000);

-- Row 3 (Nguyễn Ngọc Tân, 2025-08-01 to 2026-09-15)
INSERT IGNORE INTO allocation_history_monthly (history_id, `year_month`, `percent`) VALUES
(3, 'T8-2025', 1.0000),
(3, 'T9-2025', 1.0000),
(3, 'T10-2025', 1.0000),
(3, 'T11-2025', 1.0000),
(3, 'T12-2025', 1.0000),
(3, 'T1-2026', 1.0000),
(3, 'T2-2026', 1.0000),
(3, 'T3-2026', 1.0000),
(3, 'T4-2026', 1.0000),
(3, 'T5-2026', 1.0000),
(3, 'T6-2026', 1.0000),
(3, 'T7-2026', 1.0000),
(3, 'T8-2026', 1.0000),
(3, 'T9-2026', 0.5000);

-- Row 6 (Lại Thùy Linh, 2025-06-15 to 2026-05-30)
INSERT IGNORE INTO allocation_history_monthly (history_id, `year_month`, `percent`) VALUES
(6, 'T6-2025', 0.5238),
(6, 'T7-2025', 1.0000),
(6, 'T8-2025', 1.0000),
(6, 'T9-2025', 1.0000),
(6, 'T10-2025', 1.0000),
(6, 'T11-2025', 1.0000),
(6, 'T12-2025', 1.0000),
(6, 'T1-2026', 1.0000),
(6, 'T2-2026', 1.0000),
(6, 'T3-2026', 1.0000),
(6, 'T4-2026', 1.0000),
(6, 'T5-2026', 1.0000);

-- Row 9 (Nguyễn Thanh Hằng, 2025-06-15 to 2026-05-30)
INSERT IGNORE INTO allocation_history_monthly (history_id, `year_month`, `percent`) VALUES
(9, 'T6-2025', 0.5238),
(9, 'T7-2025', 1.0000),
(9, 'T8-2025', 1.0000),
(9, 'T9-2025', 1.0000),
(9, 'T10-2025', 1.0000),
(9, 'T11-2025', 1.0000),
(9, 'T12-2025', 1.0000),
(9, 'T1-2026', 1.0000),
(9, 'T2-2026', 1.0000),
(9, 'T3-2026', 1.0000),
(9, 'T4-2026', 1.0000),
(9, 'T5-2026', 1.0000);

-- Master Schedule tasks (Sheet4) - HIS sample
INSERT IGNORE INTO tasks (phase_group, product_id, task_no, task_name, feature_group, content) VALUES
('Giai đoạn 1', 1, 1,  'Quản trị hệ thống',                   'Quản trị hệ thống',              '- Phân quyền CSKCB\n- Phân quyền user\n- Phân quyền dữ liệu hệ thống:\n+ Phân quyền kho\n+ Phân quyền dịch vụ kỹ thuật\n+ Phân quyền đối tượng\n+ Phân quyền khoa'),
('Giai đoạn 1', 1, 2,  'Quản lý danh mục',                    'Quản lý danh mục',               'Danh mục dùng chung:\n + Địa phương\n + Dân tộc\n Danh mục nghiệp vụ:\n + Cơ sở khám chữa bệnh\n + Danh mục dịch vụ kỹ thuật\n + Danh mục giá dịch vụ'),
('Giai đoạn 1', 1, 3,  'Quản lý tiếp đón người bệnh',         'Quản lý tiếp đón người bệnh',    '- Quản lý thông tin, khai thác tiếp đón Bệnh nhân\n- In phiếu thông tin: Tờ chỉ định, Barcode, vòng tay, phiếu khám bệnh'),
('Giai đoạn 1', 1, 4,  'Quản lý khám bệnh',                   'Quản lý khám bệnh',              '- Quản lý khám bệnh\n- Quản lý kê đơn\n- Quản lý thông tin thực hiện vật lý trị liệu\n- Quản lý mẫu phiếu in và ký số Đơn thuốc/ Vật tư\n- Thanh toán: Bảng kê chi phí KCB'),
('Giai đoạn 1', 1, 5,  'Cận lâm sàng (TDCN, CDHA, SA, NS)',   'Cận lâm sàng',                  'Danh sách thực hiện chẩn đoán hình ảnh (XQ, CT, MRI)\nThực hiện Chẩn đoán hình ảnh (kỹ thuật viên)\nĐọc kết quả Chẩn đoán hình ảnh (bác sĩ)'),
('Giai đoạn 1', 1, 6,  'Quản lý xét nghiệm',                  'Quản lý xét nghiệm',             '- Danh sách chờ xét nghiệm\n- Thực hiện xét nghiệm\n- Nhập kết quả xét nghiệm\n- Ký số kết quả xét nghiệm'),
('Giai đoạn 1', 1, 7,  'Quản lý nội trú',                     'Quản lý nội trú',                '- Nhập viện/Chuyển viện/Xuất viện\n- Quản lý buồng bệnh, giường bệnh\n- Quản lý điều trị nội trú'),
('Giai đoạn 1', 1, 8,  'Quản lý Dược - VTYT',                 'Quản lý Dược - VTYT',            '- Quản lý nhập kho, xuất kho thuốc/VTYT\n- Quản lý tồn kho\n- Cấp phát thuốc'),
('Giai đoạn 1', 1, 9,  'Viện phí',                            'Viện phí',                       '- Tính giá dịch vụ kỹ thuật\n- Thanh toán viện phí nội trú/ngoại trú\n- Báo cáo doanh thu'),
('Giai đoạn 1', 1, 10, 'Báo cáo thống kê',                    'Báo cáo thống kê',               '- Báo cáo thống kê tình hình KCB\n- Báo cáo tổng hợp theo yêu cầu'),
-- LIS tasks
('Giai đoạn 1', 2, 1,  'Quản lý danh mục xét nghiệm',         'Quản lý danh mục',               '- Danh mục xét nghiệm\n- Danh mục thiết bị\n- Cấu hình giá trị bình thường'),
('Giai đoạn 1', 2, 2,  'Tiếp nhận mẫu',                       'Tiếp nhận mẫu',                  '- Tiếp nhận yêu cầu xét nghiệm\n- In barcode mẫu\n- Phân loại mẫu'),
('Giai đoạn 1', 2, 3,  'Thực hiện xét nghiệm',                'Thực hiện xét nghiệm',           '- Nhập kết quả thủ công/tự động\n- Kiểm soát chất lượng\n- Ký số kết quả');

