# CI/CD — Build & Deploy

Luồng: **push lên `main` → GitHub Actions build image (backend + frontend) → đẩy lên GHCR → SSH vào VPS chạy `scripts/deploy.sh` (pull image + restart)**. VPS không build gì cả.

```
git push origin main
      │
      ▼
GitHub Actions (ubuntu runner)
  ├─ build backend  → ghcr.io/minhnguyenhoa/ql175-backend:latest
  ├─ build frontend → ghcr.io/minhnguyenhoa/ql175-frontend:latest
      │
      ▼ (ssh)
VPS: scripts/deploy.sh
  ├─ git fetch + checkout chọn lọc (compose, nginx, database) — KHÔNG đụng certbot/conf
  ├─ docker compose -f docker-compose.prod.yml pull
  └─ docker compose -f docker-compose.prod.yml up -d
```

## File liên quan
| File | Vai trò |
|------|---------|
| `.github/workflows/deploy.yml` | Workflow CI/CD |
| `docker-compose.prod.yml` | Compose production — dùng image GHCR, `db-seed` nằm trong profile `seed` (không tự chạy) |
| `scripts/deploy.sh` | Script chạy trên VPS: pull image + restart |
| `docker-compose.yml` | Giữ nguyên cho dev local (build tại chỗ) |

## Cấu hình 1 lần

### 1. GitHub Secrets
Vào **repo → Settings → Secrets and variables → Actions → New repository secret**, thêm:

| Secret | Giá trị |
|--------|---------|
| `VPS_HOST` | IP hoặc domain VPS (vd `resalloc.site`) |
| `VPS_USER` | user SSH trên VPS (vd `root`) |
| `VPS_SSH_KEY` | **private key** SSH (toàn bộ nội dung, gồm cả dòng BEGIN/END) |
| `VPS_PORT` | cổng SSH (để trống = 22) |
| `VPS_PROJECT_DIR` | đường dẫn repo trên VPS: `/www/QL175` |

> `GITHUB_TOKEN` không cần tạo — Actions tự cấp, đã đủ quyền push/pull GHCR cho repo này.

### 2. Tạo SSH key cho Actions (chạy trên VPS)
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/gh_actions -N ""
cat ~/.ssh/gh_actions.pub >> ~/.ssh/authorized_keys   # cho phép key này đăng nhập
cat ~/.ssh/gh_actions                                  # COPY phần này vào secret VPS_SSH_KEY
```

### 3. (Sau lần deploy đầu) GHCR package
Lần đầu Actions push, 2 package `ql175-backend` / `ql175-frontend` được tạo ở chế độ **private**, gắn với repo. VPS pull bằng `GITHUB_TOKEN` tạm thời (script tự `docker login`) nên vẫn chạy được.
- Nếu muốn pull không cần login: vào **GitHub → Packages → từng package → Package settings → Change visibility → Public**.

## Deploy
- **Tự động:** mỗi lần `git push origin main`.
- **Thủ công từ GitHub:** tab **Actions → Build & Deploy → Run workflow**.
- **Thủ công trên VPS** (không qua CI):
  ```bash
  cd /www/QL175 && bash scripts/deploy.sh
  ```

## Seed dữ liệu (chỉ khi cần)
`db-seed` không bao giờ tự chạy. Khi muốn nạp dữ liệu mẫu:
```bash
docker compose -f docker-compose.prod.yml --profile seed up db-seed
```
