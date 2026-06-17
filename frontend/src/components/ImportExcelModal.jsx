import React, { useState } from 'react'
import {
  Modal, Upload, Button, Alert, Typography, Space,
  Descriptions, Tag, Progress, Divider, List, message
} from 'antd'
import {
  InboxOutlined, FileExcelOutlined, CheckCircleOutlined,
  LoadingOutlined, WarningOutlined, DownloadOutlined
} from '@ant-design/icons'
import { getToken, clearAuth } from '../auth'

const { Dragger } = Upload
const { Text, Title } = Typography

const SHEET_LIST = [
  { name: 'DS Khách hàng',         table: 'customers' },
  { name: 'DS Dự án',              table: 'products, project_groups' },
  { name: 'Tổ chức nhân sự',       table: 'employees' },
  { name: 'Config',                table: 'phases' },
  { name: 'Tổ chức phòng ban',     table: 'departments' },
  { name: 'Phân bổ nguồn lực',     table: 'resource_allocations, monthly_allocations' },
  { name: 'Phân bổ nguồn lực_Old', table: 'allocation_history' },
  { name: 'Deliverable List',      table: 'milestones' },
  { name: 'Sheet4',                table: 'tasks' },
]

export default function ImportExcelModal({ open, onClose, onSuccess }) {
  const [fileList, setFileList] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleUpload = async () => {
    if (!fileList.length) return
    setLoading(true)
    setResult(null)
    setError(null)

    const formData = new FormData()
    formData.append('file', fileList[0])

    try {
      // Dùng fetch trực tiếp để gửi FormData (không qua api interceptor default)
      const token = getToken()
      const res = await fetch('/api/import/excel', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      })

      // Phiên hết hạn -> đăng xuất & về trang login (giống interceptor của axios)
      if (res.status === 401) {
        clearAuth()
        window.location.href = '/login'
        return
      }

      const data = await res.json().catch(() => ({}))
      if (res.ok && data.success) {
        setResult(data)
        onSuccess?.()
      } else {
        setError(data.message || `Import thất bại (HTTP ${res.status})`)
      }
    } catch (e) {
      setError(e.message || 'Lỗi kết nối')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setFileList([])
    setResult(null)
    setError(null)
    onClose()
  }

  const handleDownloadTemplate = async () => {
    try {
      const token = getToken()
      const res = await fetch('/api/import/template', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.status === 401) {
        clearAuth()
        window.location.href = '/login'
        return
      }
      if (!res.ok) { message.error('Tải template thất bại'); return }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'Resource_Allocation_Template.xlsx'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e) {
      message.error(e.message || 'Lỗi kết nối')
    }
  }

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls',
    beforeUpload: (file) => {
      setFileList([file])
      setResult(null)
      setError(null)
      return false // không auto upload
    },
    onRemove: () => { setFileList([]); setResult(null); setError(null) },
    fileList,
  }

  return (
    <Modal
      title={
        <Space>
          <FileExcelOutlined style={{ color: '#52c41a', fontSize: 18 }} />
          <span>Import dữ liệu từ Excel</span>
        </Space>
      }
      open={open}
      onCancel={handleClose}
      width={620}
      footer={[
        <Button key="cancel" onClick={handleClose} disabled={loading}>
          Đóng
        </Button>,
        <Button
          key="upload"
          type="primary"
          icon={loading ? <LoadingOutlined /> : <FileExcelOutlined />}
          loading={loading}
          disabled={!fileList.length || loading || !!result}
          onClick={handleUpload}
          style={{ background: '#52c41a', borderColor: '#52c41a' }}
        >
          {loading ? 'Đang import...' : 'Bắt đầu Import'}
        </Button>
      ]}
    >
      {/* Sheet list info */}
      <Alert
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        message="File Excel phải có đúng cấu trúc các sheet sau:"
        description={
          <div style={{ marginTop: 6 }}>
            {SHEET_LIST.map(s => (
              <Tag key={s.name} color="blue" style={{ margin: '2px' }}>{s.name}</Tag>
            ))}
            <div style={{ marginTop: 10 }}>
              <Button
                size="small"
                icon={<DownloadOutlined />}
                onClick={handleDownloadTemplate}
              >
                Tải template mẫu
              </Button>
            </div>
          </div>
        }
      />

      {/* Upload area */}
      {!result && (
        <Dragger {...uploadProps} disabled={loading} style={{ marginBottom: 16 }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ color: loading ? '#d9d9d9' : '#1677ff', fontSize: 36 }} />
          </p>
          <p className="ant-upload-text">Kéo thả file Excel hoặc click để chọn</p>
          <p className="ant-upload-hint" style={{ fontSize: 12 }}>
            Hỗ trợ .xlsx, .xls · Dữ liệu cũ sẽ bị xoá và thay thế
          </p>
        </Dragger>
      )}

      {/* Loading progress */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <Progress type="circle" percent={99} status="active" size={60} />
          <div style={{ marginTop: 12, color: '#666' }}>
            Đang xử lý file và import vào database...
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <Alert
          type="error"
          showIcon
          icon={<WarningOutlined />}
          message="Import thất bại"
          description={error}
          style={{ marginTop: 8 }}
        />
      )}

      {/* Success result */}
      {result && (
        <div>
          <Alert
            type="success"
            showIcon
            icon={<CheckCircleOutlined />}
            message="Import thành công!"
            style={{ marginBottom: 12 }}
          />
          <Descriptions bordered size="small" column={2}>
            <Descriptions.Item label="File">{result.fileName}</Descriptions.Item>
            <Descriptions.Item label="SQL statements">{result.sqlStatements}</Descriptions.Item>
            <Descriptions.Item label="Milestones">
              <Tag color="blue">{result.milestones}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Tasks">
              <Tag color="purple">{result.tasks}</Tag>
            </Descriptions.Item>
          </Descriptions>

          <Divider style={{ margin: '12px 0' }} />

          <List
            size="small"
            dataSource={SHEET_LIST}
            renderItem={item => (
              <List.Item style={{ padding: '4px 0' }}>
                <Space>
                  <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  <Text strong>{item.name}</Text>
                  <Text type="secondary">→ {item.table}</Text>
                </Space>
              </List.Item>
            )}
          />
        </div>
      )}
    </Modal>
  )
}
