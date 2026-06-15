import React, { useEffect, useState, useRef } from 'react'
import { Card, Row, Col, Table, Tag, Spin, Button, Statistic, Progress, Divider, Space, Typography, message, Tooltip, Select } from 'antd'
import { PrinterOutlined, FileTextOutlined, WarningOutlined, CheckCircleOutlined, TeamOutlined, ProjectOutlined, UploadOutlined, FilePdfOutlined, ReloadOutlined } from '@ant-design/icons'
import api from '../services/api'
import ImportExcelModal from '../components/ImportExcelModal'

const { Title, Text } = Typography

const PRODUCT_LABELS = {
  HIS: '🏥 HIS - Quản lý bệnh viện',
  LIS: '⚗ LIS - Quản lý xét nghiệm',
  EMR: '📋 EMR - Bệnh án điện tử',
  KSK: '🩺 KSK - Sức khỏe CBCS',
  QLTTDL: '🖥 QLTTDL - Trung tâm DL',
  THDB: '🔗 THDB - Tích hợp đồng bộ',
}

const STATUS_COLOR = { Warning: 'orange', 'On Track': 'green', Overdue: 'red', Normal: 'blue' }

export default function ReportPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [exportLoading, setExportLoading] = useState(false)
  const [slideLoading, setSlideLoading] = useState(false)
  const [importOpen, setImportOpen] = useState(false)
  const [projectGroups, setProjectGroups] = useState([])
  const [selectedProject, setSelectedProject] = useState(null)
  const printRef = useRef()

  const loadData = () => {
    setLoading(true)
    api.get('/report/summary')
      .then(d => setData(d))
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadData()
    api.get('/report/project-groups')
      .then(groups => {
        setProjectGroups(groups)
        // Mặc định: chọn tất cả
        setSelectedProject([])
      })
      .catch(() => {})
  }, [])

  const handlePrint = () => window.print()

  const handleExportSlides = async () => {
    setSlideLoading(true)
    try {
      const token = localStorage.getItem('qt175_token')
      const today = new Date()
      const dateStr = `${String(today.getDate()).padStart(2,'0')}/${String(today.getMonth()+1).padStart(2,'0')}/${today.getFullYear()}`
      const projValue = (!selectedProject || selectedProject.length === 0)
        ? 'ALL'
        : selectedProject.join(',')
      const res = await fetch(`/api/report/export-slides?date=${encodeURIComponent(dateStr)}&project=${encodeURIComponent(projValue)}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) { message.error('Xuất Slide thất bại'); return }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `BaoCaoSlide_${dateStr.replace(/\//g,'-')}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      message.success('Đã xuất báo cáo slide!')
    } catch(e) {
      message.error('Lỗi: ' + e.message)
    } finally {
      setSlideLoading(false)
    }
  }

  const handleExportPdf = async () => {
    setExportLoading(true)
    try {
      const token = localStorage.getItem('qt175_token')
      const today = new Date()
      const dateStr = `${String(today.getDate()).padStart(2,'0')}/${String(today.getMonth()+1).padStart(2,'0')}/${today.getFullYear()}`
      // selectedProject là array: [] = tất cả, ['H05YTS'] = 1, ['H05YTS','H06ABC'] = nhiều
      const projValue = (!selectedProject || selectedProject.length === 0)
        ? 'ALL'
        : selectedProject.join(',')
      const res = await fetch(`/api/report/export-pdf?date=${encodeURIComponent(dateStr)}&project=${encodeURIComponent(projValue)}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!res.ok) { message.error('Xuất PDF thất bại'); return }
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `BaoCaoTienDo_${dateStr.replace(/\//g,'-')}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      message.success('Đã xuất PDF!')
    } catch(e) {
      message.error('Lỗi: ' + e.message)
    } finally {
      setExportLoading(false)
    }
  }

  if (loading) return <div style={{ textAlign: 'center', padding: 60 }}><Spin size="large" /></div>
  if (!data) return <div style={{ padding: 40, color: 'red' }}>Không tải được dữ liệu báo cáo.</div>

  const { overview, byPhase, byProduct, milestoneComponents, employees, allocationByProduct, reportDate } = data

  const completionPct = overview.total > 0
    ? Math.round((overview.done / overview.total) * 100 * 100) / 100 : 0

  // Columns for milestone components table
  const componentCols = [
    { title: '#', key: 'idx', render: (_, __, i) => i + 1, width: 40 },
    { title: 'Hệ thống', dataIndex: 'productCode', key: 'code', width: 80,
      render: v => <Tag color="blue">{v}</Tag> },
    { title: 'Milestone thành phần', dataIndex: 'component_milestone', key: 'comp',
      ellipsis: true },
    { title: 'Tổng', dataIndex: 'total', key: 'total', width: 60, align: 'center' },
    { title: 'Hoàn thành', dataIndex: 'done', key: 'done', width: 80, align: 'center',
      render: (v, r) => {
        const pct = r.total > 0 ? Math.round((v / r.total) * 100) : 0
        return <span style={{ color: pct === 100 ? '#52c41a' : '#fa8c16' }}>{pct}%</span>
      }
    },
  ]

  // By-product columns
  const productCols = [
    { title: 'Hệ thống', dataIndex: 'code', key: 'code', width: 90,
      render: v => <Tag color="blue">{v}</Tag> },
    { title: 'Tên', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Tổng MS', dataIndex: 'totalMilestone', key: 'total', align: 'center', width: 80 },
    { title: 'Hoàn thành', key: 'done', align: 'center', width: 80,
      render: (_, r) => {
        const pct = r.totalMilestone > 0 ? Math.round((r.done / r.totalMilestone) * 100) : 0
        return <Text style={{ color: pct === 100 ? '#52c41a' : pct > 50 ? '#fa8c16' : '#ff4d4f' }}>{pct}%</Text>
      }
    },
    { title: 'Quá hạn', dataIndex: 'overdue', key: 'overdue', align: 'center', width: 70,
      render: v => v > 0 ? <Tag color="red">{v}</Tag> : <Tag color="green">0</Tag> },
    { title: 'Trạng thái', dataIndex: 'projectStatus', key: 'status', width: 100,
      render: v => <Tag color={STATUS_COLOR[v] || 'default'}>{v || '—'}</Tag> },
  ]

  // Employee by company columns
  const companyCols = [
    { title: 'Đơn vị', dataIndex: 'company', key: 'company' },
    { title: 'Headcount', dataIndex: 'headcount', key: 'hc', align: 'right' },
    { title: 'Tỷ trọng', key: 'pct', align: 'right',
      render: (_, r) => `${employees.total > 0 ? Math.round((r.headcount / employees.total) * 100) : 0}%` },
  ]

  const roleCols = [
    { title: 'Vai trò', dataIndex: 'role', key: 'role' },
    { title: 'HC', dataIndex: 'headcount', key: 'hc', align: 'right' },
    { title: '%', key: 'pct', align: 'right',
      render: (_, r) => `${employees.total > 0 ? Math.round((r.headcount / employees.total) * 100) : 0}%` },
  ]

  const allocCols = [
    { title: 'Hệ thống', dataIndex: 'code', key: 'code', width: 90,
      render: v => <Tag color="blue">{v}</Tag> },
    { title: 'Tên', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Nhân sự (HC)', dataIndex: 'headcount', key: 'hc', align: 'center', width: 100 },
  ]

  const gtelCompanies = (employees.byCompany || []).filter(c => c.company === 'GTEL ICT')
  const gtelHC = gtelCompanies.reduce((s, c) => s + (c.headcount || 0), 0)
  const outsourceHC = employees.total - gtelHC

  return (
    <>
      {/* Toolbar — hidden when printing */}
      <div className="no-print" style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Button
            icon={<UploadOutlined />}
            onClick={() => setImportOpen(true)}
            style={{ borderColor: '#52c41a', color: '#52c41a' }}
          >
            Import Excel
          </Button>
          <Tooltip title="Tải lại dữ liệu từ database">
            <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading} />
          </Tooltip>
        </Space>
        <Space>
          <Select
            mode="multiple"
            value={selectedProject}
            onChange={setSelectedProject}
            style={{ minWidth: 200, maxWidth: 340 }}
            placeholder="Tất cả dự án"
            allowClear
            maxTagCount={2}
            options={projectGroups.map(g => ({
              value: g.code,
              label: g.code,
              title: g.name || g.code,
            }))}
          />
          <Button
            type="primary"
            icon={<FilePdfOutlined />}
            loading={exportLoading}
            onClick={handleExportPdf}
            style={{ background: '#cf1322', borderColor: '#cf1322' }}
          >
            {(!selectedProject || selectedProject.length === 0)
              ? 'Xuất PDF (Tất cả)'
              : `Xuất PDF (${selectedProject.join(', ')})`}
          </Button>
          <Button
            type="primary"
            icon={<FilePdfOutlined />}
            loading={slideLoading}
            onClick={handleExportSlides}
            style={{ background: '#16357d', borderColor: '#16357d' }}
          >
            Xuất Slide
          </Button>
          <Button icon={<PrinterOutlined />} onClick={handlePrint}>
            In trang
          </Button>
        </Space>
      </div>

      <ImportExcelModal
        open={importOpen}
        onClose={() => setImportOpen(false)}
        onSuccess={() => { setImportOpen(false); loadData() }}
      />

      <div ref={printRef} className="report-body">

        {/* ══ COVER ══════════════════════════════════════════════════════════ */}
        <Card style={{ marginBottom: 24, background: 'linear-gradient(135deg,#003a8c 0%,#1677ff 100%)', color: '#fff', borderRadius: 12 }}>
          <Row gutter={24} align="middle">
            <Col span={14}>
              <Text style={{ color: '#91caff', fontSize: 13, letterSpacing: 2 }}>H05YTS — HỆ THỐNG CNTT Y TẾ</Text>
              <Title level={2} style={{ color: '#fff', margin: '8px 0' }}>BÁO CÁO TIẾN ĐỘ DỰ ÁN</Title>
              <Text style={{ color: '#bae0ff', fontSize: 13 }}>{reportDate} · Giai đoạn 1</Text>
            </Col>
            <Col span={10}>
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic title={<span style={{ color: '#91caff', fontSize: 11 }}>TỔNG MILESTONE</span>}
                    value={overview.total} valueStyle={{ color: '#fff', fontSize: 28 }} />
                </Col>
                <Col span={12}>
                  <Statistic title={<span style={{ color: '#91caff', fontSize: 11 }}>TỶ LỆ HT</span>}
                    value={completionPct} suffix="%" valueStyle={{ color: completionPct >= 70 ? '#95f204' : '#ffc53d', fontSize: 28 }} />
                </Col>
              </Row>
            </Col>
          </Row>
        </Card>

        {/* ══ SECTION 1: TỔNG THỂ ═══════════════════════════════════════════ */}
        <Title level={4} style={{ borderLeft: '4px solid #1677ff', paddingLeft: 12, marginBottom: 16 }}>
          1 · Tổng thể tiến độ dự án
        </Title>
        <Row gutter={16} style={{ marginBottom: 20 }}>
          {[
            { label: 'Tổng Milestone', value: overview.total, color: '#1677ff', icon: <ProjectOutlined /> },
            { label: 'Đã hoàn thành', value: overview.done,
              suffix: `${overview.total > 0 ? Math.round(overview.done / overview.total * 100) : 0}%`,
              color: '#52c41a', icon: <CheckCircleOutlined /> },
            { label: 'Đang thực hiện', value: overview.inProgress,
              suffix: `${overview.total > 0 ? Math.round(overview.inProgress / overview.total * 100) : 0}%`,
              color: '#fa8c16' },
            { label: 'Chưa bắt đầu', value: overview.notStarted,
              suffix: `${overview.total > 0 ? Math.round(overview.notStarted / overview.total * 100) : 0}%`,
              color: '#8c8c8c' },
            { label: 'Quá hạn', value: overview.overdue, color: '#ff4d4f', icon: <WarningOutlined /> },
          ].map((item, i) => (
            <Col span={4} key={i} style={{ minWidth: 140 }}>
              <Card size="small" style={{ textAlign: 'center', borderTop: `3px solid ${item.color}` }}>
                <div style={{ color: item.color, fontSize: 24, fontWeight: 700 }}>
                  {item.value}
                  {item.suffix && <span style={{ fontSize: 13, marginLeft: 4 }}>{item.suffix}</span>}
                </div>
                <div style={{ fontSize: 11, color: '#888', marginTop: 2 }}>{item.label}</div>
              </Card>
            </Col>
          ))}
          <Col flex={1}>
            <Card size="small" style={{ height: '100%' }}>
              <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>Tiến độ tổng thể</div>
              <Progress percent={completionPct} strokeColor={{ '0%': '#1677ff', '100%': '#52c41a' }}
                format={p => <span style={{ fontWeight: 700 }}>{p}%</span>} />
            </Card>
          </Col>
        </Row>

        {/* By Phase */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          {(byPhase || []).map((p, i) => {
            const pct = p.total > 0 ? Math.round((p.done / p.total) * 100) : 0
            return (
              <Col span={12} key={i}>
                <Card size="small" title={<span style={{ fontSize: 13 }}>{p.phase}</span>}
                  extra={<Tag color={pct >= 70 ? 'green' : 'orange'}>{pct}% HT</Tag>}>
                  <Row>
                    <Col span={8}><Statistic title="Tổng" value={p.total} valueStyle={{ fontSize: 18 }} /></Col>
                    <Col span={8}><Statistic title="Hoàn thành" value={p.done} valueStyle={{ fontSize: 18, color: '#52c41a' }} /></Col>
                    <Col span={8}><Statistic title="Quá hạn" value={p.overdue || 0} valueStyle={{ fontSize: 18, color: '#ff4d4f' }} /></Col>
                  </Row>
                </Card>
              </Col>
            )
          })}
        </Row>

        <Divider />

        {/* ══ SECTION 2: THEO SẢN PHẨM ══════════════════════════════════════ */}
        <Title level={4} style={{ borderLeft: '4px solid #1677ff', paddingLeft: 12, marginBottom: 16 }}>
          2 · Tiến độ theo hệ thống
        </Title>
        <Table
          dataSource={byProduct || []}
          columns={productCols}
          rowKey="code"
          size="small"
          pagination={false}
          style={{ marginBottom: 24 }}
          summary={pageData => {
            const t = pageData.reduce((a, r) => ({ total: a.total + (r.totalMilestone || 0), done: a.done + (r.done || 0), ov: a.ov + (r.overdue || 0) }), { total: 0, done: 0, ov: 0 })
            const pct = t.total > 0 ? Math.round(t.done / t.total * 100) : 0
            return (
              <Table.Summary.Row style={{ fontWeight: 700 }}>
                <Table.Summary.Cell colSpan={2}>TỔNG CỘNG</Table.Summary.Cell>
                <Table.Summary.Cell align="center">{t.total}</Table.Summary.Cell>
                <Table.Summary.Cell align="center" style={{ color: pct === 100 ? '#52c41a' : '#fa8c16' }}>{pct}%</Table.Summary.Cell>
                <Table.Summary.Cell align="center"><Tag color="red">{t.ov}</Tag></Table.Summary.Cell>
                <Table.Summary.Cell />
              </Table.Summary.Row>
            )
          }}
        />

        {/* ══ SECTION 3: MILESTONE THÀNH PHẦN GĐ1 ══════════════════════════ */}
        <Title level={4} style={{ borderLeft: '4px solid #1677ff', paddingLeft: 12, marginBottom: 16 }}>
          3 · Chi tiết Milestone thành phần — Giai đoạn 1
        </Title>
        <Table
          dataSource={milestoneComponents || []}
          columns={componentCols}
          rowKey={(r, i) => `${r.productCode}-${r.component_milestone}-${i}`}
          size="small"
          pagination={false}
          style={{ marginBottom: 24 }}
          rowClassName={(r) => {
            const pct = r.total > 0 ? Math.round((r.done / r.total) * 100) : 0
            return pct === 100 ? 'row-done' : pct < 50 ? 'row-low' : ''
          }}
        />

        <Divider />

        {/* ══ SECTION 4: NHÂN SỰ ════════════════════════════════════════════ */}
        <Title level={4} style={{ borderLeft: '4px solid #722ed1', paddingLeft: 12, marginBottom: 16 }}>
          4 · Nhân sự dự án — {reportDate}
        </Title>
        <Row gutter={16} style={{ marginBottom: 20 }}>
          {[
            { label: 'Tổng Headcount', value: employees.total, color: '#722ed1' },
            { label: 'GTEL ICT', value: gtelHC,
              suffix: `${employees.total > 0 ? Math.round(gtelHC / employees.total * 100) : 0}%`,
              color: '#1677ff' },
            { label: 'Outsourcing', value: outsourceHC,
              suffix: `${employees.total > 0 ? Math.round(outsourceHC / employees.total * 100) : 0}%`,
              color: '#fa8c16' },
          ].map((item, i) => (
            <Col span={4} key={i} style={{ minWidth: 140 }}>
              <Card size="small" style={{ textAlign: 'center', borderTop: `3px solid ${item.color}` }}>
                <div style={{ color: item.color, fontSize: 26, fontWeight: 700 }}>
                  {item.value}
                  {item.suffix && <span style={{ fontSize: 13, marginLeft: 4 }}>{item.suffix}</span>}
                </div>
                <div style={{ fontSize: 11, color: '#888' }}>{item.label}</div>
              </Card>
            </Col>
          ))}
          <Col flex={1}>
            <Card size="small" title="Phân bổ nhân sự theo dự án" extra={<TeamOutlined />}>
              {(allocationByProduct || []).map(p => (
                <div key={p.code} style={{ marginBottom: 4 }}>
                  <Row justify="space-between" align="middle">
                    <Col><Tag color="blue">{p.code}</Tag> <Text style={{ fontSize: 12 }}>{p.headcount} HC</Text></Col>
                  </Row>
                </div>
              ))}
            </Card>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={12}>
            <Card size="small" title="Cơ cấu theo đơn vị" style={{ marginBottom: 16 }}>
              <Table dataSource={employees.byCompany || []} columns={companyCols}
                rowKey="company" size="small" pagination={false} />
            </Card>
          </Col>
          <Col span={12}>
            <Card size="small" title="Cơ cấu theo vai trò">
              <Table dataSource={employees.byRole || []} columns={roleCols}
                rowKey="role" size="small" pagination={false} />
            </Card>
          </Col>
        </Row>

      </div>

      {/* Print CSS */}
      <style>{`
        @media print {
          .no-print { display: none !important; }
          .ant-layout-sider, .ant-layout-header { display: none !important; }
          .ant-layout-content { margin: 0 !important; padding: 0 !important; }
          body { font-size: 12px; }
          .report-body { padding: 0; }
          .ant-card { break-inside: avoid; }
        }
        .row-done td { background: #f6ffed !important; }
        .row-low td { background: #fff2e8 !important; }
      `}</style>
    </>
  )
}
