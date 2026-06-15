import React, { useEffect, useState } from 'react'
import { Card, Typography, Spin, Alert, Select, Space, Tag, Table, Row, Col, Statistic, Progress } from 'antd'
import { milestoneApi, productApi } from '../services/api'
import { useProject } from '../contexts/ProjectContext'

const { Title } = Typography

const REMIND_COLOR = {
  'Quá hạn': '#ff4d4f', 'Sắp đến hạn': '#faad14',
  'Chưa đến hạn': '#52c41a', 'Chưa bắt đầu': '#1677ff', 'Chưa có kế hoạch': '#d9d9d9'
}
const REMIND_TAG = {
  'Quá hạn': 'error', 'Sắp đến hạn': 'warning',
  'Chưa đến hạn': 'success', 'Chưa bắt đầu': 'processing', 'Chưa có kế hoạch': 'default'
}

export default function TimelineSummary() {
  const { selectedProject } = useProject()
  const [milestones, setMilestones] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterProduct, setFilterProduct] = useState(null)
  const [filterPhase, setFilterPhase] = useState(null)
  const [filterRemind, setFilterRemind] = useState(null)

  useEffect(() => {
    setFilterProduct(selectedProject?.id ?? null)
  }, [selectedProject])

  useEffect(() => {
    Promise.all([milestoneApi.getAll(), productApi.getAll()])
      .then(([m, p]) => { setMilestones(m); setProducts(p) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Spin style={{ display: 'block', margin: '80px auto' }} size="large" />
  if (error) return <Alert type="error" message={error} showIcon />

  const phases = [...new Set(milestones.map(m => m.phase).filter(Boolean))]
  const remindTypes = [...new Set(milestones.map(m => m.remind).filter(Boolean))]

  const filtered = milestones.filter(m => {
    if (filterProduct && m.productId !== filterProduct) return false
    if (filterPhase && m.phase !== filterPhase) return false
    if (filterRemind && m.remind !== filterRemind) return false
    return true
  })

  // Stats per product
  const productStats = products.map(p => {
    const pms = milestones.filter(m => m.productId === p.id)
    const byRemind = pms.reduce((acc, m) => {
      acc[m.remind] = (acc[m.remind] || 0) + 1
      return acc
    }, {})
    const done = pms.filter(m => m.actualEndDate).length
    const progress = pms.length > 0 ? Math.round(done / pms.length * 100) : 0
    return { ...p, total: pms.length, done, progress, byRemind }
  }).filter(p => p.total > 0)

  // Summary table by product × status
  const summaryColumns = [
    { title: 'Dự án', dataIndex: 'code', key: 'code', width: 90, render: v => <Tag color="purple">{v}</Tag> },
    { title: 'Tên sản phẩm', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Tổng MS', dataIndex: 'total', key: 'total', width: 80, align: 'center' },
    { title: 'Tiến độ', key: 'progress', width: 130,
      render: (_, r) => <Progress percent={r.progress} size="small" strokeColor={r.progress < 30 ? '#ff4d4f' : r.progress < 70 ? '#faad14' : '#52c41a'} /> },
    ...['Quá hạn','Sắp đến hạn','Chưa đến hạn','Chưa bắt đầu','Chưa có kế hoạch'].map(s => ({
      title: <Tag color={REMIND_TAG[s]}>{s}</Tag>, key: s, width: 110, align: 'center',
      render: (_, r) => {
        const cnt = r.byRemind[s] || 0
        return cnt > 0 ? <span style={{ color: REMIND_COLOR[s], fontWeight: 600 }}>{cnt}</span> : <span style={{ color: '#ccc' }}>—</span>
      }
    })),
  ]

  // Detail table
  const detailColumns = [
    { title: 'Giai đoạn', dataIndex: 'phase', key: 'phase', width: 120, render: v => <Tag>{v}</Tag> },
    { title: 'Dự án', dataIndex: 'productCode', key: 'productCode', width: 80, render: v => <Tag color="purple">{v}</Tag> },
    { title: 'Milestone', dataIndex: 'componentMilestone', key: 'componentMilestone', width: 200, ellipsis: true },
    { title: 'Chi tiết', dataIndex: 'detailMilestone', key: 'detailMilestone', ellipsis: true },
    { title: 'Plan End', dataIndex: 'planEndDate', key: 'planEndDate', width: 110,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '—' },
    { title: 'Actual End', dataIndex: 'actualEndDate', key: 'actualEndDate', width: 110,
      render: d => d ? <span style={{ color: '#52c41a' }}>{new Date(d).toLocaleDateString('vi-VN')}</span> : '—' },
    { title: 'Trạng thái', dataIndex: 'remind', key: 'remind', width: 140,
      render: v => <Tag color={REMIND_TAG[v] || 'default'}>{v || '—'}</Tag> },
  ]

  const overdue = milestones.filter(m => m.remind === 'Quá hạn').length
  const upcoming = milestones.filter(m => m.remind === 'Sắp đến hạn').length
  const notStarted = milestones.filter(m => m.remind === 'Chưa bắt đầu').length
  const onTrack = milestones.filter(m => m.remind === 'Chưa đến hạn').length

  return (
    <div>
      {/* KPI row */}
      <Row gutter={[12, 12]} style={{ marginBottom: 20 }}>
        {[
          { title: 'Tổng Milestone', value: milestones.length, color: '#1677ff' },
          { title: 'Quá hạn', value: overdue, color: '#ff4d4f' },
          { title: 'Sắp đến hạn', value: upcoming, color: '#faad14' },
          { title: 'Chưa bắt đầu', value: notStarted, color: '#8c8c8c' },
          { title: 'Đúng tiến độ', value: onTrack, color: '#52c41a' },
        ].map(k => (
          <Col key={k.title} xs={12} sm={8} md={6} lg={4}>
            <Card size="small" style={{ borderRadius: 8, boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
              <Statistic title={k.title} value={k.value} valueStyle={{ color: k.color, fontSize: 22 }} />
            </Card>
          </Col>
        ))}
      </Row>

      {/* Summary per product */}
      <Card bordered={false} style={{ marginBottom: 16 }}
        title={<Title level={5} style={{ margin: 0 }}>Tóm tắt tiến độ theo Dự án</Title>}>
        <Table columns={summaryColumns} dataSource={productStats} rowKey="id"
          size="small" pagination={false} scroll={{ x: 800 }} />
      </Card>

      {/* Detail table with filters */}
      <Card bordered={false} title={
        <Space wrap>
          <Title level={5} style={{ margin: 0 }}>Chi tiết Timeline ({filtered.length})</Title>
          <Select placeholder="Dự án" allowClear style={{ width: 160 }}
            value={filterProduct} onChange={setFilterProduct}
            options={products.map(p => ({ value: p.id, label: `${p.code}` }))} />
          <Select placeholder="Giai đoạn" allowClear style={{ width: 140 }}
            value={filterPhase} onChange={setFilterPhase}
            options={phases.map(p => ({ value: p, label: p }))} />
          <Select placeholder="Trạng thái" allowClear style={{ width: 160 }}
            value={filterRemind} onChange={setFilterRemind}
            options={remindTypes.map(r => ({ value: r, label: r }))} />
        </Space>
      }>
        <Table columns={detailColumns} dataSource={filtered} rowKey="id"
          size="small" scroll={{ x: 900 }} pagination={{ pageSize: 20 }}
          rowClassName={r => r.remind === 'Quá hạn' ? 'ant-table-row-error' : ''} />
      </Card>
    </div>
  )
}
