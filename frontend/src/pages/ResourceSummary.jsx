import React, { useEffect, useState } from 'react'
import { Table, Card, Typography, Spin, Alert, Tag, Tooltip, Select, Space, Badge } from 'antd'
import { WarningOutlined } from '@ant-design/icons'
import { resourceSummaryApi } from '../services/api'

const { Title, Text } = Typography

const MONTHS = [
  'T6-2025','T7-2025','T8-2025','T9-2025','T10-2025','T11-2025','T12-2025',
  'T1-2026','T2-2026','T3-2026','T4-2026','T5-2026','T6-2026','T7-2026',
  'T8-2026','T9-2026','T10-2026','T11-2026','T12-2026'
]

function PercentCell({ value, overloaded }) {
  if (value == null || value === 0) return <span style={{ color: '#ccc' }}>—</span>
  const pct = Math.round(value * 100)
  const color = overloaded ? '#ff4d4f' : pct >= 80 ? '#faad14' : '#52c41a'
  const bg = overloaded ? '#fff1f0' : pct >= 80 ? '#fffbe6' : '#f6ffed'
  return (
    <Tooltip title={overloaded ? `⚠ Quá tải: ${pct}%` : `${pct}%`}>
      <div style={{
        background: bg, color, fontWeight: 600, fontSize: 11,
        borderRadius: 4, padding: '1px 4px', textAlign: 'center',
        border: `1px solid ${color}33`, whiteSpace: 'nowrap'
      }}>
        {overloaded && '⚠ '}{pct}%
      </div>
    </Tooltip>
  )
}

export default function ResourceSummary() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterCompany, setFilterCompany] = useState(null)
  const [filterContract, setFilterContract] = useState(null)
  const [visibleMonths, setVisibleMonths] = useState(MONTHS.slice(0, 13))

  useEffect(() => {
    resourceSummaryApi.getSummary()
      .then(setData).catch(e => setError(e.message)).finally(() => setLoading(false))
  }, [])

  const filtered = data.filter(d => {
    if (filterCompany && d.employeeCompany !== filterCompany) return false
    if (filterContract && d.contractType !== filterContract) return false
    return true
  })

  const companies = [...new Set(data.map(d => d.employeeCompany).filter(Boolean))]

  const overloadedCount = data.reduce((acc, d) => {
    return acc + Object.values(d.overloaded || {}).filter(Boolean).length
  }, 0)

  const fixedCols = [
    {
      title: 'Nhân sự', dataIndex: 'employeeName', key: 'name', width: 170, fixed: 'left',
      render: (v, r) => (
        <div>
          <div style={{ fontWeight: 500 }}>{v}</div>
          <div style={{ fontSize: 11, color: '#888' }}>{r.employeeCompany}</div>
        </div>
      )
    },
    { title: 'Loại HĐ', dataIndex: 'contractType', key: 'contract', width: 105, fixed: 'left',
      render: v => <Tag color={v === 'Chính thức' ? 'green' : 'blue'} style={{ fontSize: 11 }}>{v || '—'}</Tag> },
    { title: 'Dự án', dataIndex: 'projects', key: 'projects', width: 150, fixed: 'left',
      render: v => v?.length ? v.map(p => <Tag key={p} color="purple" style={{ fontSize: 11, marginBottom: 2 }}>{p}</Tag>) : '—' },
  ]

  const monthCols = visibleMonths.map(m => ({
    title: <span style={{ fontSize: 11 }}>{m}</span>,
    key: m, width: 78, align: 'center',
    render: (_, r) => {
      const val = r.monthlyTotal?.[m]
      const over = r.overloaded?.[m]
      return <PercentCell value={val ? parseFloat(val) : null} overloaded={over} />
    }
  }))

  const columns = [...fixedCols, ...monthCols]

  if (loading) return <Spin style={{ display: 'block', margin: '80px auto' }} size="large" />
  if (error) return <Alert type="error" message={error} showIcon />

  return (
    <Card bordered={false}>
      <div className="page-header" style={{ flexWrap: 'wrap', gap: 8 }}>
        <Space>
          <Title level={5} style={{ margin: 0 }}>Resource Summary — Tải trọng nhân sự</Title>
          {overloadedCount > 0 && (
            <Tag color="error" icon={<WarningOutlined />}>
              {overloadedCount} tháng/người quá tải
            </Tag>
          )}
        </Space>
        <Space wrap>
          <Select placeholder="Lọc công ty" allowClear style={{ width: 150 }}
            value={filterCompany} onChange={setFilterCompany}
            options={companies.map(c => ({ value: c, label: c }))} />
          <Select placeholder="Loại hợp đồng" allowClear style={{ width: 150 }}
            value={filterContract} onChange={setFilterContract}
            options={[{ value: 'Chính thức', label: 'Chính thức' }, { value: 'Outsourcing', label: 'Outsourcing' }]} />
          <Select mode="multiple" placeholder="Chọn tháng hiển thị" style={{ width: 280 }}
            value={visibleMonths} onChange={setVisibleMonths} maxTagCount={3}
            options={MONTHS.map(m => ({ value: m, label: m }))} />
        </Space>
      </div>

      <div style={{ marginBottom: 12, fontSize: 12, color: '#888' }}>
        <span style={{ background: '#f6ffed', border: '1px solid #52c41a33', padding: '1px 6px', borderRadius: 4, marginRight: 8 }}>≤79% — Bình thường</span>
        <span style={{ background: '#fffbe6', border: '1px solid #faad1433', padding: '1px 6px', borderRadius: 4, marginRight: 8 }}>80–99% — Cận tải</span>
        <span style={{ background: '#fff1f0', border: '1px solid #ff4d4f33', padding: '1px 6px', borderRadius: 4 }}>≥100% — Quá tải</span>
      </div>

      <Table columns={columns} dataSource={filtered} rowKey="employeeId"
        size="small" scroll={{ x: 170 * 3 + visibleMonths.length * 78 }}
        pagination={{ pageSize: 30 }}
        rowClassName={r => Object.values(r.overloaded || {}).some(Boolean) ? 'ant-table-row-warning' : ''} />
    </Card>
  )
}
