import React, { useState } from 'react'
import { Form, Input, Button, Card, Typography, Alert } from 'antd'
import { UserOutlined, LockOutlined, ProjectOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { setAuth } from '../auth'

const { Title, Text } = Typography

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const onFinish = async ({ username, password }) => {
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post('/api/auth/login', { username, password })
      setAuth(res.data.token, { username: res.data.username, fullName: res.data.fullName })
      navigate('/', { replace: true })
    } catch (e) {
      const status = e.response?.status
      if (status === 401 || status === 403) {
        setError('Tên đăng nhập hoặc mật khẩu không đúng')
      } else if (status) {
        // 5xx / lỗi khác từ server -> không phải sai mật khẩu
        setError(`Máy chủ đang gặp sự cố (HTTP ${status}). Vui lòng thử lại sau.`)
      } else {
        setError('Không kết nối được máy chủ. Kiểm tra mạng hoặc thử lại sau.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #1677ff 0%, #0958d9 100%)'
    }}>
      <Card style={{ width: 380, borderRadius: 12, boxShadow: '0 8px 32px rgba(0,0,0,0.18)' }}>
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <ProjectOutlined style={{ fontSize: 36, color: '#1677ff', marginBottom: 8 }} />
          <Title level={4} style={{ margin: 0 }}>Quản trị Dự án</Title>
          <Text type="secondary" style={{ fontSize: 13 }}>Đăng nhập để tiếp tục</Text>
        </div>

        {error && <Alert type="error" message={error} showIcon style={{ marginBottom: 16 }} />}

        <Form onFinish={onFinish} layout="vertical" size="large">
          <Form.Item name="username" rules={[{ required: true, message: 'Nhập tên đăng nhập' }]}>
            <Input prefix={<UserOutlined />} placeholder="Tên đăng nhập" autoFocus />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: 'Nhập mật khẩu' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Mật khẩu" />
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Đăng nhập
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>Tài khoản mặc định: admin / admin123</Text>
        </div>
      </Card>
    </div>
  )
}
