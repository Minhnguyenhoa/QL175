# Hệ thống Quản trị Dự án

## Công nghệ sử dụng
- **Backend**: Spring Boot 3.2 + Spring Data JPA
- **Frontend**: React 18 + Ant Design + Recharts + Vite
- **Database**: MySQL 8.0

## Cấu trúc dự án
```
QT_175/
├── backend/          Spring Boot project
├── frontend/         React project
└── database/         SQL init scripts
```

## Hướng dẫn cài đặt

### 1. Tạo database MySQL
```sql
-- Mở MySQL Workbench hoặc MySQL CLI
CREATE DATABASE project_mgmt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Sau đó chạy file database/init.sql để có dữ liệu mẫu
```

### 2. Cấu hình Backend
Sửa file `backend/src/main/resources/application.properties`:
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/project_mgmt?...
spring.datasource.username=root        # <-- sửa username MySQL
spring.datasource.password=root        # <-- sửa password MySQL
```

### 3. Chạy Backend (Spring Boot)
```bash
cd backend
mvn spring-boot:run
# hoặc mở bằng IntelliJ IDEA
```
Backend chạy tại: http://localhost:8080

### 4. Cài đặt và chạy Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend chạy tại: http://localhost:5173

## API Endpoints
| Method | URL                         | Mô tả                    |
|--------|-----------------------------|--------------------------|
| GET    | /api/dashboard              | Thống kê tổng quan       |
| GET    | /api/customers              | Danh sách khách hàng     |
| GET    | /api/project-groups         | Danh sách đề án          |
| GET    | /api/products               | Danh sách sản phẩm       |
| GET    | /api/employees              | Danh sách nhân sự        |
| GET    | /api/allocations            | Phân bổ nguồn lực        |
| GET    | /api/milestones             | Milestone / Deliverable  |
| POST/PUT/DELETE | (tương ứng)        | CRUD đầy đủ              |

## Tính năng
- **Dashboard**: Thống kê tổng quan, biểu đồ tròn trạng thái milestone, biểu đồ nhân sự theo công ty
- **Quản lý Dự án**: CRUD đề án (Project Group) và sản phẩm (Product), lọc/tìm kiếm
- **Khách hàng**: Quản lý chủ đầu tư và đơn vị thụ hưởng
- **Nhân sự**: CRUD nhân viên, tìm kiếm theo tên/công ty
- **Phân bổ nguồn lực**: Ma trận phân bổ % theo tháng, lọc theo dự án/nhân sự
- **Milestone**: Theo dõi tiến độ, lọc trạng thái quá hạn/sắp đến hạn
