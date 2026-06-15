import React, { useEffect, useState } from 'react'
import { Card, Select, Typography, Spin, Alert, Space, Tag, Table, Row, Col,
  Statistic, Descriptions, Progress, Empty } from 'antd'
import { UserOutlined } from '@ant-design/icons'
import { employeeApi, allocationApi, milestoneApi } from '../services/api'

const { Title, Text } = Typography

const MONTHS = [
  'T6-2025','T7-2025','T8-2025','T9-2025','T10-2025','T11-2025','T12-2025',
  'T1-2026','T2-2026','T3-2026','T4-2026','T5-2026','T6-2026'
]

export default function PersonalView() {
  const [employees, setEmployees] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [employee, setEmployee] = useState(null)
  const [allocations, setAllocations] = useState([])
  const [loading, setLoading] = useState(false)
  const [initLoading, setInitLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    employeeApi.getAll().then(setEmployees).catch(e => setError(e.message)).finally(() => setInitLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedId) { setEmployee(null); setAllocations([]); return }
    setLoading(true)
    Promise.all([employeeApi.getById(selectedId), allocationApi.getByEmployee(selectedId)])
      .then(([emp, allocs]) => { setEmployee(emp); setAllocations(allocs) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [selectedId])

  const getMonthPct = (alloc, month) => {
    const m = alloc.monthlyAllocations?.find(ma => ma.yearMonth === month)
    return m ? Math.round(parseFloat(m.percent) * 100) : null
  }

  // monthly total across projects
  const monthlyTotal = MONTHS.reduce((acc, m) => {
    acc[m] = allocations.reduce((sum, a) => {
      const p = getMonthPct(a, m)
      return sum + (p || 0)
    }, 0)
    return acc
  }, {})

  const allocationColumns = [
    { title: 'Dự án', dataIndex: 'productCode', key: 'productCode', width: 90,
      render: v => <Tag color="purple">{v}</Tag> },
    { title: 'Tên sản phẩm', dataIndex: 'productName', key: 'productName', ellipsis: true },
    { title: 'Vai trò', dataIndex: 'roleInProject', key: 'role', width: 160 },
    { title: 'Từ', dataIndex: 'fromDate', key: 'from', width: 100,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '—' },
    { title: 'Đến', dataIndex: 'toDate', key: 'to', width: 100,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '—' },
    { title: '%KH', dataIndex: 'allocationPercent', key: 'pct', width: 70,
      render: v => v ? <Tag color="blue">{Math.round(parseFloat(v) * 100)}%</Tag> : '—' },
    ...MONTHS.slice(0, 9).map(m => ({
      title: <span style={{ fontSize: 10 }}>{m}</span>, key: m, width: 65, align: 'center',
      render: (_, r) => {
        const p = getMonthPct(r, m)
        return p != null ? (
          <span style={{ fontSize: 11, fontWeight: 600, color: p >= 100 ? '#ff4d4f' : '#1677ff' }}>{p}%</span>
        ) : <span style={{ color: '#ddd' }}>—</span>
      }
    }))
  ]

  if (initLoading) return <Spin style={{ display: 'block', margin: '80px auto' }} size="large" />
  if (error) return <Alert type="error" message={error} showIcon />

  const projects = [...new Set(allocations.map(a => a.productCode).filter(Boolean))]
  const totalPct = Object.values(monthlyTotal).reduce((a, b) => a + b, 0)
  const peakMonth = Object.entries(monthlyTotal).sort((a, b) => b[1] - a[1])[0]

  return (
    <Card bordered={false}>
      <div className="page-header" style={{ marginBottom: 20 }}>
        <Title level={5} style={{ margin: 0 }}>
          <UserOutlined style={{ marginRight: 8 }} />
          View cá nhân — Thay thế sheet Mr/Ms trong Excel
        </Title>
        <Select
          showSearch style={{ width: 280 }} placeholder="Chọn nhân sự..."
          value={selectedId} onChange={setSelectedId}
          filterOption={(i, o) => o.label.toLowerCase().includes(i.toLowerCase())}
          options={employees.map(e => ({ value: e.id, label: `${e.name} (${e.company || ''})` }))}
        />
      </div>

      {!selectedId && (
        <Empty description="Chọn nhân sự để xem thông tin cá nhân" style={{ padding: 60 }} />
      )}

      {loading && <Spin style={{ display: 'block', margin: '40px auto' }} />}

      {employee && !loading && (
        <>
          {/* Profile card */}
          <Card size="small" style={{ marginBottom: 16, background: '#fafafa', borderRadius: 8 }}>
            <Descriptions column={{ xs: 1, sm: 2, md: 3 }} size="small">
              <Descriptions.Item label="Họ tên"><strong>{employee.name}</strong></Descriptions.Item>
              <Descriptions.Item label="Công ty"><Tag color={employee.company === 'GTEL ICT' ? 'blue' : 'orange'}>{employee.company || '—'}</Tag></Descriptions.Item>
              <Descriptions.Item label="Phòng/TT">{employee.department || '—'}</Descriptions.Item>
              <Descriptions.Item label="Role">{employee.role || '—'}</Descriptions.Item>
              <Descriptions.Item label="Hình thức HĐ"><Tag color={employee.contractType === 'Chính thức' ? 'green' : 'geekblue'}>{employee.contractType || '—'}</Tag></Descriptions.Item>
              <Descriptions.Item label="Làm việc">{employee.workMode} / {employee.workTime}</Descriptions.Item>
            </Descriptions>
          </Card>

          {/* Stats */}
          <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
            <Col xs={12} sm={6}>
              <Card size="small" style={{ borderRadius: 8 }}>
                <Statistic title="Số dự án" value={projects.length} valueStyle={{ color: '#722ed1' }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small" style={{ borderRadius: 8 }}>
                <Statistic title="Số phân bổ" value={allocations.length} valueStyle={{ color: '#1677ff' }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small" style={{ borderRadius: 8 }}>
                <Statistic title="Tháng đỉnh" value={peakMonth ? `${peakMonth[1]}%` : '—'}
                  valueStyle={{ color: peakMonth && peakMonth[1] > 100 ? '#ff4d4f' : '#52c41a' }} />
              </Card>
            </Col>
            <Col xs={12} sm={6}>
              <Card size="small" style={{ borderRadius: 8 }}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>Dự án tham gia</div>
                <div>{projects.map(p => <Tag key={p} color="purple" style={{ marginBottom: 2 }}>{p}</Tag>)}</div>
              </Card>
            </Col>
          </Row>

          {/* Monthly load chart */}
          <Card size="small" title="Tải trọng theo tháng" style={{ marginBottom: 16, borderRadius: 8 }}>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {MONTHS.map(m => {
                const v = monthlyTotal[m] || 0
                const color = v > 100 ? '#ff4d4f' : v >= 80 ? '#faad14' : '#52c41a'
                return v > 0 ? (
                  <div key={m} style={{ textAlign: 'center', minWidth: 60 }}>
                    <Progress type="circle" percent={Math.min(v, 100)} width={50} strokeColor={color}
                      format={() => <span style={{ fontSize: 10, fontWeight: 600 }}>{v}%</span>} />
                    <div style={{ fontSize: 10, marginTop: 4, color: '#888' }}>{m}</div>
                  </div>
                ) : null
              })}
            </div>
          </Card>

          {/* Allocation detail */}
          <Card size="small" title={`Chi tiết phân bổ (${allocations.length} dự án-phân bổ)`} style={{ borderRadius: 8 }}>
            <Table columns={allocationColumns} dataSource={allocations} rowKey="id"
              size="small" scroll={{ x: 900 }} pagination={false} />
          </Card>
        </>
      )}
    </Card>
  )
}
