import React, { useEffect, useState } from 'react'
import {
  Card, Table, Button, Modal, Form, Input, InputNumber, DatePicker, Space,
  Tag, Typography, Popconfirm, message, Tooltip, Row, Col, Progress
} from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, HistoryOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { allocationHistoryApi } from '../services/api'

const { Title, Text } = Typography

const MONTHS = [
  'T6-2025','T7-2025','T8-2025','T9-2025','T10-2025','T11-2025','T12-2025',
  'T1-2026','T2-2026','T3-2026','T4-2026','T5-2026','T6-2026','T7-2026',
  'T8-2026','T9-2026','T10-2026','T11-2026','T12-2026',
]

export default function AllocationHistoryPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [detailRow, setDetailRow] = useState(null)
  const [form] = Form.useForm()

  const load = () => {
    setLoading(true)
    allocationHistoryApi.getAll()
      .then(setData)
      .catch(e => message.error(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const openCreate = () => { setEditing(null); form.resetFields(); setModalOpen(true) }

  const openEdit = (row) => {
    setEditing(row)
    form.setFieldsValue({
      employeeName: row.employeeName,
      projectsText: row.projectsText,
      roleInProject: row.roleInProject,
      fromDate: row.fromDate ? dayjs(row.fromDate) : null,
      toDate: row.toDate ? dayjs(row.toDate) : null,
      allocationPercent: row.allocationPercent ? Math.round(parseFloat(row.allocationPercent) * 100) : 100,
    })
    setModalOpen(true)
  }

  const handleSave = async () => {
    try {
      const vals = await form.validateFields()
      const payload = {
        employeeName: vals.employeeName,
        projectsText: vals.projectsText,
        roleInProject: vals.roleInProject,
        fromDate: vals.fromDate ? vals.fromDate.format('YYYY-MM-DD') : null,
        toDate: vals.toDate ? vals.toDate.format('YYYY-MM-DD') : null,
        allocationPercent: (vals.allocationPercent || 100) / 100,
        monthlyAllocations: editing?.monthlyAllocations || [],
      }
      if (editing) {
        await allocationHistoryApi.update(editing.id, payload)
        message.success('Đã cập nhật')
      } else {
        await allocationHistoryApi.create(payload)
        message.success('Đã tạo mới')
      }
      setModalOpen(false)
      load()
    } catch {}
  }

  const handleDelete = async (id) => {
    await allocationHistoryApi.delete(id).catch(e => message.error(e.message))
    load()
    message.success('Đã xoá')
  }

  const getMonthPct = (row, month) => {
    const m = row.monthlyAllocations?.find(ma => ma.yearMonth === month)
    return m ? parseFloat(m.percent) : null
  }

  const columns = [
    { title: 'Nhân sự', dataIndex: 'employeeName', key: 'emp', width: 160,
      render: v => <Text strong>{v}</Text> },
    { title: 'Dự án (cũ)', dataIndex: 'projectsText', key: 'proj', ellipsis: true,
      render: v => v ? v.split(',').map(p => (
        <Tag key={p.trim()} color="geekblue" style={{ marginBottom: 2 }}>{p.trim()}</Tag>
      )) : '—' },
    { title: 'Vai trò', dataIndex: 'roleInProject', key: 'role', width: 150 },
    { title: 'Từ ngày', dataIndex: 'fromDate', key: 'from', width: 100,
      render: d => d ? dayjs(d).format('DD/MM/YYYY') : '—' },
    { title: 'Đến ngày', dataIndex: 'toDate', key: 'to', width: 100,
      render: d => d ? dayjs(d).format('DD/MM/YYYY') : '—' },
    { title: '%KH', dataIndex: 'allocationPercent', key: 'pct', width: 70, align: 'center',
      render: v => <Tag color="blue">{Math.round(parseFloat(v || 1) * 100)}%</Tag> },
    ...MONTHS.slice(0, 13).map(m => ({
      title: <Tooltip title={m}><span style={{ fontSize: 10 }}>{m.replace('-20', "'")}</span></Tooltip>,
      key: m, width: 52, align: 'center',
      render: (_, r) => {
        const p = getMonthPct(r, m)
        if (p == null) return <span style={{ color: '#e0e0e0', fontSize: 10 }}>—</span>
        const pct = Math.round(p * 100)
        return <span style={{ fontSize: 11, fontWeight: 600, color: pct >= 100 ? '#52c41a' : '#faad14' }}>{pct}%</span>
      }
    })),
    {
      title: 'Hành động', key: 'actions', width: 90, fixed: 'right',
      render: (_, r) => (
        <Space size={4}>
          <Button icon={<EditOutlined />} size="small" onClick={() => openEdit(r)} />
          <Popconfirm title="Xác nhận xoá?" onConfirm={() => handleDelete(r.id)}>
            <Button icon={<DeleteOutlined />} size="small" danger />
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <>
      <Card bordered={false}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <Title level={5} style={{ margin: 0 }}>
              <HistoryOutlined style={{ marginRight: 8 }} />
              Phân bổ nguồn lực (Phiên bản cũ) — Sheet 10
            </Title>
            <Text type="secondary" style={{ fontSize: 12 }}>
              Format gộp: một dòng/người, danh sách dự án phân cách bởi dấu phẩy, tổng %KH = 100%
            </Text>
          </div>
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Thêm mới</Button>
        </div>

        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          size="small"
          scroll={{ x: 1400 }}
          pagination={{ pageSize: 20, showSizeChanger: true }}
        />
      </Card>

      {/* Monthly detail drawer */}
      {detailRow && (
        <Modal title={`Chi tiết tháng — ${detailRow.employeeName}`} open={!!detailRow}
          onCancel={() => setDetailRow(null)} footer={null} width={700}>
          <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
            Dự án: {detailRow.projectsText}
          </Text>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {MONTHS.map(m => {
              const p = getMonthPct(detailRow, m)
              if (p == null) return null
              const pct = Math.round(p * 100)
              const color = pct >= 100 ? '#52c41a' : '#faad14'
              return (
                <div key={m} style={{ textAlign: 'center', minWidth: 64 }}>
                  <Progress type="circle" percent={Math.min(pct, 100)} width={52} strokeColor={color}
                    format={() => <span style={{ fontSize: 10, fontWeight: 700 }}>{pct}%</span>} />
                  <div style={{ fontSize: 10, marginTop: 4, color: '#888' }}>{m}</div>
                </div>
              )
            })}
          </div>
        </Modal>
      )}

      <Modal
        title={editing ? 'Sửa bản ghi' : 'Thêm bản ghi mới'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        width={560}
        okText="Lưu"
        cancelText="Huỷ"
      >
        <Form form={form} layout="vertical" size="small" style={{ marginTop: 12 }}>
          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="employeeName" label="Họ tên nhân sự" rules={[{ required: true }]}>
                <Input placeholder="Nguyễn Văn A" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="roleInProject" label="Vai trò">
                <Input placeholder="Dev / QA / PM..." />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="projectsText" label="Danh sách dự án (phân cách bởi dấu phẩy)" rules={[{ required: true }]}>
            <Input placeholder="HIS, LIS, EMR, KSK" />
          </Form.Item>
          <Row gutter={12}>
            <Col span={8}>
              <Form.Item name="fromDate" label="Từ ngày">
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="toDate" label="Đến ngày">
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="allocationPercent" label="% Phân bổ (tổng)" initialValue={100}>
                <InputNumber min={0} max={200} formatter={v => `${v}%`} parser={v => v.replace('%', '')} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </>
  )
}
