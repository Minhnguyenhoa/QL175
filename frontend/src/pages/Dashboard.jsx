import React, { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Table, Tag, Typography, Spin, Alert, Progress, Badge, Divider, Tooltip } from 'antd'
import {
  ProjectOutlined, TeamOutlined, ScheduleOutlined,
  WarningOutlined, CheckCircleOutlined, ClockCircleOutlined,
  RiseOutlined, UserOutlined, PieChartOutlined
} from '@ant-design/icons'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip as RTooltip, ResponsiveContainer,
  Cell, PieChart, Pie, Legend
} from 'recharts'
import { dashboardApi } from '../services/api'
import { useProject } from '../contexts/ProjectContext'

const { Title, Text } = Typography

const PROD_COLORS = {
  HIS: '#1677ff', LIS: '#13c2c2', EMR: '#722ed1',
  KSK: '#fa8c16', QLTTDL: '#52c41a', THDB: '#eb2f96'
}
const REMIND_TAG = {
  'Quá hạn': 'error', 'Sắp đến hạn': 'warning',
  'Chưa đến hạn': 'success', 'Chưa bắt đầu': 'processing', 'Chưa có kế hoạch': 'default'
}

const COMPANY_COLORS = ['#1677ff','#52c41a','#faad14','#ff4d4f','#722ed1','#13c2c2','#fa8c16','#eb2f96','#a0d911','#096dd9']

function KpiCard({ title, value, color, icon, suffix }) {
  return (
    <Card size="small" style={{ borderRadius: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{
          width: 44, height: 44, borderRadius: 10, background: color + '18',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, color
        }}>
          {icon}
        </div>
        <div>
          <div style={{ fontSize: 12, color: '#888', marginBottom: 2 }}>{title}</div>
          <div style={{ fontSize: 22, fontWeight: 700, color, lineHeight: 1 }}>
            {value}{suffix && <span style={{ fontSize: 13, fontWeight: 400, marginLeft: 3 }}>{suffix}</span>}
          </div>
        </div>
      </div>
    </Card>
  )
}

function ProductProgressCard({ p }) {
  const color = PROD_COLORS[p.code] || '#1677ff'
  const total = Number(p.total) || 0
  const done = Number(p.done) || 0
  const inProg = Number(p.in_progress) || 0
  const overdue = Number(p.overdue) || 0
  const pct = total > 0 ? Math.round(done / total * 100) : 0

  return (
    <Card size="small" style={{ borderRadius: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.06)', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Tag color={color} style={{ margin: 0, fontWeight: 700, fontSize: 13 }}>{p.code}</Tag>
          {overdue > 0 && <Badge count={overdue} color="#ff4d4f" size="small" overflowCount={999} />}
        </div>
        <Text style={{ fontSize: 11, color: '#999' }}>{p.cur_phase || '—'}</Text>
      </div>
      <div style={{ fontSize: 11, color: '#555', marginBottom: 8, height: 28, overflow: 'hidden',
        display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
        {p.name}
      </div>
      <Progress percent={pct} size="small"
        strokeColor={pct < 20 ? '#ff4d4f' : pct < 50 ? '#faad14' : '#52c41a'}
        format={v => <span style={{ fontSize: 11 }}>{v}%</span>} />
      <Row gutter={4} style={{ marginTop: 8 }}>
        {[
          { label: 'Tổng', value: total, color: '#555' },
          { label: 'Xong', value: done, color: '#52c41a' },
          { label: 'Đang TH', value: inProg, color: '#1677ff' },
          { label: 'Quá hạn', value: overdue, color: '#ff4d4f' },
        ].map(s => (
          <Col key={s.label} span={6} style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 15, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 10, color: '#aaa' }}>{s.label}</div>
          </Col>
        ))}
      </Row>
    </Card>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const { selectedProject } = useProject()

  useEffect(() => {
    setLoading(true)
    setError(null)
    dashboardApi.get(selectedProject?.id)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [selectedProject])

  if (loading) return <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>
  if (error) return <Alert type="error" message={error}
    description="Không thể kết nối tới backend. Hãy đảm bảo Spring Boot đang chạy." showIcon />

  const byProduct = data.byProduct || []
  const byCompany = data.byCompany || []
  const allocationByProduct = data.allocationByProduct || []
  const recentOverdue = data.recentOverdue || []

  // Build company pie data: GTEL vs Outsourcing
  const gtelHC = Number(data.gtelEmployees) || 0
  const totalEmp = Number(data.totalEmployees) || 0
  const outsourceHC = totalEmp - gtelHC
  const gtelVsOs = [
    { name: 'GTEL ICT', value: gtelHC },
    { name: 'Outsourcing', value: outsourceHC },
  ]

  // Milestone summary
  const total = Number(data.totalMilestones) || 0
  const done = Number(data.doneMilestones) || 0
  const inProg = Number(data.inProgressMilestones) || 0
  const overdue = Number(data.overdueMilestones) || 0
  const upcoming = Number(data.upcomingMilestones) || 0
  const notStarted = total - done - inProg - overdue - upcoming
  const msPieData = [
    { name: 'Hoàn thành', value: done, color: '#52c41a' },
    { name: 'Đang thực hiện', value: inProg, color: '#1677ff' },
    { name: 'Quá hạn', value: overdue, color: '#ff4d4f' },
    { name: 'Sắp đến hạn', value: upcoming, color: '#faad14' },
    { name: 'Chưa bắt đầu', value: Math.max(0, notStarted), color: '#d9d9d9' },
  ].filter(d => d.value > 0)

  const overdueColumns = [
    { title: 'Dự án', dataIndex: 'product_code', key: 'product_code', width: 75,
      render: v => <Tag color={PROD_COLORS[v] || 'default'} style={{ fontWeight: 600 }}>{v}</Tag> },
    { title: 'Milestone', dataIndex: 'component_milestone', key: 'component_milestone', width: 180, ellipsis: true },
    { title: 'Chi tiết', dataIndex: 'detail_milestone', key: 'detail_milestone', ellipsis: true },
    { title: 'Deadline', dataIndex: 'plan_end_date', key: 'plan_end_date', width: 100,
      render: d => d ? <span style={{ color: '#ff4d4f', fontWeight: 500 }}>
        {new Date(d).toLocaleDateString('vi-VN')}</span> : '-' },
    { title: 'TT', dataIndex: 'remind', key: 'remind', width: 115,
      render: v => <Tag color={REMIND_TAG[v] || 'default'} style={{ fontSize: 11 }}>{v || '-'}</Tag> },
  ]

  const mmBarData = allocationByProduct.map(a => ({ name: a.code, mm: Number(a.mm) || 0, hc: Number(a.hc) || 0 }))
  const companyBarData = byCompany.slice(0, 8).map((c, i) => ({ name: c.company, hc: Number(c.hc) || 0, color: COMPANY_COLORS[i] }))

  const doneGlobalPct = total > 0 ? Math.round(done / total * 100) : 0

  return (
    <div style={{ padding: '0 2px' }}>
      {/* ── Row 1: KPI cards ───────────────────────────── */}
      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={8} md={4}>
          <KpiCard title="Tổng Milestone" value={total} color="#1677ff" icon={<ScheduleOutlined />} />
        </Col>
        <Col xs={12} sm={8} md={4}>
          <KpiCard title="Hoàn thành" value={done} color="#52c41a" icon={<CheckCircleOutlined />} />
        </Col>
        <Col xs={12} sm={8} md={4}>
          <KpiCard title="Đang thực hiện" value={inProg} color="#1677ff" icon={<ClockCircleOutlined />} />
        </Col>
        <Col xs={12} sm={8} md={4}>
          <KpiCard title="Quá hạn" value={overdue} color="#ff4d4f" icon={<WarningOutlined />} />
        </Col>
        <Col xs={12} sm={8} md={4}>
          <KpiCard title="Nhân sự" value={totalEmp} color="#722ed1" icon={<TeamOutlined />} suffix={`(${gtelHC} GTEL)`} />
        </Col>
        <Col xs={12} sm={8} md={4}>
          <KpiCard title="Tổng MM phân bổ" value={Number(data.totalMM) || 0} color="#fa8c16" icon={<RiseOutlined />} suffix="MM" />
        </Col>
      </Row>

      {/* ── Row 2: Global progress bar ─────────────────── */}
      <Card size="small" style={{ marginBottom: 16, borderRadius: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <Text strong style={{ fontSize: 13 }}>Tiến độ tổng thể dự án</Text>
              <Text style={{ fontSize: 13, color: '#52c41a', fontWeight: 600 }}>{doneGlobalPct}% milestone hoàn thành</Text>
            </div>
            <Progress
              percent={doneGlobalPct}
              strokeColor={{ '0%': '#faad14', '100%': '#52c41a' }}
              trailColor="#f0f0f0"
              strokeWidth={12}
              format={() => null}
            />
            <div style={{ display: 'flex', gap: 16, marginTop: 6, flexWrap: 'wrap' }}>
              {msPieData.map(d => (
                <span key={d.name} style={{ fontSize: 11, color: '#666' }}>
                  <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 4,
                    background: d.color, marginRight: 4 }} />
                  {d.name}: <b style={{ color: d.color }}>{d.value}</b>
                </span>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* ── Row 3: Per-product cards ───────────────────── */}
      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        {byProduct.map(p => (
          <Col key={p.code} xs={24} sm={12} md={8} lg={4}>
            <ProductProgressCard p={p} />
          </Col>
        ))}
      </Row>

      {/* ── Row 4: Charts + allocation ─────────────────── */}
      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        <Col xs={24} md={8}>
          <Card size="small" title={<span><PieChartOutlined /> Milestone theo trạng thái</span>}
            style={{ borderRadius: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={msPieData} cx="50%" cy="50%" outerRadius={70} dataKey="value"
                  label={({ percent }) => `${(percent * 100).toFixed(0)}%`} labelLine={false}>
                  {msPieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <RTooltip formatter={(v, n) => [v, n]} />
                <Legend iconSize={10} formatter={(v) => <span style={{ fontSize: 11 }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        <Col xs={24} md={8}>
          <Card size="small" title={<span><TeamOutlined /> Nhân sự theo công ty</span>}
            style={{ borderRadius: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={companyBarData} margin={{ top: 4, right: 8, bottom: 24, left: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 9 }} angle={-30} textAnchor="end" interval={0} />
                <YAxis tick={{ fontSize: 10 }} />
                <RTooltip formatter={(v) => [v, 'Nhân sự']} />
                <Bar dataKey="hc" radius={[3, 3, 0, 0]}>
                  {companyBarData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>

        <Col xs={24} md={8}>
          <Card size="small" title={<span><RiseOutlined /> Phân bổ MM theo dự án</span>}
            style={{ borderRadius: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <div style={{ padding: '8px 0' }}>
              {mmBarData.map(a => (
                <div key={a.name} style={{ marginBottom: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                    <span>
                      <Tag color={PROD_COLORS[a.name] || 'default'} style={{ margin: 0, fontSize: 11 }}>{a.name}</Tag>
                      <span style={{ fontSize: 11, color: '#888', marginLeft: 4 }}>{a.hc} người</span>
                    </span>
                    <span style={{ fontSize: 12, fontWeight: 600, color: PROD_COLORS[a.name] || '#333' }}>
                      {a.mm} MM
                    </span>
                  </div>
                  <Progress
                    percent={Math.round(a.mm / (Number(data.totalMM) || 1) * 100)}
                    strokeColor={PROD_COLORS[a.name] || '#1677ff'}
                    size="small" showInfo={false} />
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>

      {/* ── Row 5: GTEL vs OS + Overdue table ─────────── */}
      <Row gutter={[12, 12]}>
        <Col xs={24} md={6}>
          <Card size="small" title={<span><UserOutlined /> GTEL vs Outsourcing</span>}
            style={{ borderRadius: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={gtelVsOs} cx="50%" cy="50%" outerRadius={55} dataKey="value"
                  label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`} labelLine={false}>
                  <Cell fill="#1677ff" />
                  <Cell fill="#fa8c16" />
                </Pie>
                <RTooltip formatter={(v, n) => [v + ' người', n]} />
                <Legend iconSize={10} formatter={(v) => <span style={{ fontSize: 11 }}>{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
            <Divider style={{ margin: '8px 0' }} />
            {byCompany.map((c, i) => (
              <div key={c.company} style={{ display: 'flex', justifyContent: 'space-between',
                marginBottom: 4, fontSize: 12 }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ width: 8, height: 8, borderRadius: 4, background: COMPANY_COLORS[i],
                    display: 'inline-block' }} />
                  {c.company}
                </span>
                <b>{c.hc}</b>
              </div>
            ))}
          </Card>
        </Col>

        <Col xs={24} md={18}>
          <Card size="small"
            title={<span><WarningOutlined style={{ color: '#ff4d4f' }} /> Milestone quá hạn / sắp đến hạn ({recentOverdue.length})</span>}
            style={{ borderRadius: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
            <Table
              columns={overdueColumns}
              dataSource={recentOverdue}
              rowKey={(r, i) => i}
              size="small"
              pagination={{ pageSize: 8, size: 'small' }}
              scroll={{ x: 680 }}
              rowClassName={r => r.remind === 'Quá hạn' ? 'ant-table-row-error' : ''}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
