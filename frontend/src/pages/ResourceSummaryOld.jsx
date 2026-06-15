import React, { useEffect, useState, useMemo } from 'react'
import { Card, Table, Typography, Spin, Alert, Tag, Tooltip, Select, Row, Col, Statistic, Badge } from 'antd'
import { HistoryOutlined, WarningOutlined } from '@ant-design/icons'
import { allocationHistoryApi } from '../services/api'

const { Title, Text } = Typography

const MONTHS = [
  'T6-2025','T7-2025','T8-2025','T9-2025','T10-2025','T11-2025','T12-2025',
  'T1-2026','T2-2026','T3-2026','T4-2026','T5-2026','T6-2026','T7-2026',
  'T8-2026','T9-2026','T10-2026','T11-2026','T12-2026',
]

function cellColor(pct) {
  if (pct == null || pct === 0) return 'transparent'
  if (pct >= 100) return '#fff1f0'
  if (pct >= 80) return '#fffbe6'
  return '#f6ffed'
}

function cellTextColor(pct) {
  if (pct >= 100) return '#cf1322'
  if (pct >= 80) return '#d46b08'
  return '#389e0d'
}

export default function ResourceSummaryOld() {
  const [rawData, setRawData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedMonths, setSelectedMonths] = useState(MONTHS.slice(0, 13))

  useEffect(() => {
    allocationHistoryApi.getAll()
      .then(setRawData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  // Aggregate: group by employeeName, sum monthly % across all rows for that person
  const summary = useMemo(() => {
    const map = {}
    for (const row of rawData) {
      const name = row.employeeName
      if (!map[name]) {
        map[name] = { employeeName: name, projects: new Set(), monthlyTotal: {} }
      }
      // collect projects
      if (row.projectsText) {
        row.projectsText.split(',').forEach(p => map[name].projects.add(p.trim()))
      }
      // sum monthly
      for (const ma of (row.monthlyAllocations || [])) {
        const prev = map[name].monthlyTotal[ma.yearMonth] || 0
        map[name].monthlyTotal[ma.yearMonth] = prev + parseFloat(ma.percent || 0)
      }
    }
    return Object.values(map).map(e => ({
      ...e,
      projects: [...e.projects],
      overloadedMonths: Object.entries(e.monthlyTotal)
        .filter(([, v]) => v * 100 >= 100)
        .map(([m]) => m),
    })).sort((a, b) => a.employeeName.localeCompare(b.employeeName, 'vi'))
  }, [rawData])

  const overloadedCount = summary.filter(e => e.overloadedMonths.length > 0).length

  const columns = [
    {
      title: 'Nhân sự', dataIndex: 'employeeName', key: 'emp', width: 160, fixed: 'left',
      render: (v, r) => (
        <div>
          <Text strong style={{ fontSize: 13 }}>{v}</Text>
          {r.overloadedMonths.length > 0 && (
            <Tooltip title={`Quá tải: ${r.overloadedMonths.join(', ')}`}>
              <Tag color="red" icon={<WarningOutlined />} style={{ marginLeft: 4, fontSize: 10 }}>
                {r.overloadedMonths.length}T
              </Tag>
            </Tooltip>
          )}
        </div>
      )
    },
    {
      title: 'Dự án tham gia', dataIndex: 'projects', key: 'proj', width: 220,
      render: arr => arr.map(p => <Tag key={p} color="geekblue" style={{ marginBottom: 2 }}>{p}</Tag>)
    },
    ...selectedMonths.map(m => ({
      title: <Tooltip title={m}><span style={{ fontSize: 10 }}>{m.replace('-20', "'")}</span></Tooltip>,
      key: m, width: 60, align: 'center',
      render: (_, r) => {
        const raw = r.monthlyTotal[m]
        if (raw == null || raw === 0) return <span style={{ color: '#e0e0e0' }}>—</span>
        const pct = Math.round(raw * 100)
        return (
          <div style={{
            background: cellColor(pct), borderRadius: 4, padding: '2px 0',
            fontWeight: 700, fontSize: 12, color: cellTextColor(pct)
          }}>
            {pct}%
          </div>
        )
      }
    })),
  ]

  if (loading) return <Spin style={{ display: 'block', margin: '80px auto' }} size="large" />
  if (error) return <Alert type="error" message={error} showIcon />

  return (
    <Card bordered={false}>
      <div style={{ marginBottom: 16 }}>
        <Title level={5} style={{ margin: 0 }}>
          <HistoryOutlined style={{ marginRight: 8 }} />
          Resource Summary (Phiên bản cũ) — Sheet 11
        </Title>
        <Text type="secondary" style={{ fontSize: 12 }}>
          Tổng hợp từ dữ liệu phân bổ cũ (Sheet 10). Màu xanh ≤79%, vàng 80–99%, đỏ ≥100%.
        </Text>
      </div>

      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic title="Tổng nhân sự" value={summary.length} valueStyle={{ color: '#1677ff' }} />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic title="Người quá tải" value={overloadedCount}
              valueStyle={{ color: overloadedCount > 0 ? '#ff4d4f' : '#52c41a' }}
              prefix={overloadedCount > 0 ? <WarningOutlined /> : null} />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic title="Số bản ghi nguồn" value={rawData.length} valueStyle={{ color: '#722ed1' }} />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small" style={{ borderRadius: 8 }}>
            <Statistic title="Số tháng hiển thị" value={selectedMonths.length} />
          </Card>
        </Col>
      </Row>

      <div style={{ marginBottom: 12 }}>
        <Text style={{ marginRight: 8, fontSize: 13 }}>Chọn tháng hiển thị:</Text>
        <Select
          mode="multiple" value={selectedMonths} onChange={setSelectedMonths}
          options={MONTHS.map(m => ({ value: m, label: m }))}
          style={{ width: '100%', maxWidth: 700 }}
          maxTagCount={8}
          placeholder="Chọn tháng..."
        />
      </div>

      <div style={{ marginBottom: 8, display: 'flex', gap: 16 }}>
        {[
          { color: '#f6ffed', border: '#b7eb8f', label: '≤ 79% — Bình thường' },
          { color: '#fffbe6', border: '#ffe58f', label: '80–99% — Cảnh báo' },
          { color: '#fff1f0', border: '#ffa39e', label: '≥ 100% — Quá tải' },
        ].map(({ color, border, label }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
            <div style={{ width: 14, height: 14, background: color, border: `1px solid ${border}`, borderRadius: 2 }} />
            {label}
          </div>
        ))}
      </div>

      <Table
        columns={columns}
        dataSource={summary}
        rowKey="employeeName"
        size="small"
        scroll={{ x: 300 + selectedMonths.length * 60 }}
        pagination={false}
        bordered
        rowClassName={r => r.overloadedMonths.length > 0 ? 'overloaded-row' : ''}
      />

      <style>{`.overloaded-row td:first-child { border-left: 3px solid #ff4d4f !important; }`}</style>
    </Card>
  )
}
