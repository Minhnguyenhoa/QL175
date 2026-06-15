import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, Select, DatePicker, Card, Typography,
  message, Spin, Alert, Space, Popconfirm, Tag, Switch, Row, Col } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, WarningOutlined } from '@ant-design/icons'
import { milestoneApi, productApi } from '../services/api'
import { useProject } from '../contexts/ProjectContext'
import dayjs from 'dayjs'

const { Title } = Typography

const REMIND_COLOR = {
  'Quá hạn': 'error', 'Sắp đến hạn': 'warning',
  'Chưa đến hạn': 'success', 'Chưa bắt đầu': 'processing', 'Chưa có kế hoạch': 'default'
}
const STATUS_COLOR = {
  'Quá hạn': '#ff4d4f', 'Sắp đến hạn': '#faad14',
  'Chưa đến hạn': '#52c41a', 'Chưa bắt đầu': '#1677ff'
}

const PHASES = ['Giai đoạn 1', 'Giai đoạn 2', 'Giai đoạn 3']
const REMIND_OPTIONS = ['Quá hạn', 'Sắp đến hạn', 'Chưa đến hạn', 'Chưa bắt đầu', 'Chưa có kế hoạch']

export default function Milestones() {
  const { selectedProject } = useProject()
  const [milestones, setMilestones] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState({ open: false, record: null })
  const [form] = Form.useForm()
  const [filterProduct, setFilterProduct] = useState(null)
  const [filterRemind, setFilterRemind] = useState(null)
  const [filterPhase, setFilterPhase] = useState(null)

  // Đồng bộ với global project selector
  useEffect(() => {
    setFilterProduct(selectedProject?.id ?? null)
  }, [selectedProject])

  const loadData = () => {
    setLoading(true)
    Promise.all([milestoneApi.getAll(), productApi.getAll()])
      .then(([m, p]) => { setMilestones(m); setProducts(p) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadData() }, [])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      const payload = {
        ...values,
        planStartDate: values.planStartDate?.format('YYYY-MM-DD'),
        planEndDate: values.planEndDate?.format('YYYY-MM-DD'),
        actualStartDate: values.actualStartDate?.format('YYYY-MM-DD'),
        actualEndDate: values.actualEndDate?.format('YYYY-MM-DD'),
      }
      if (modal.record) {
        await milestoneApi.update(modal.record.id, payload)
        message.success('Đã cập nhật milestone')
      } else {
        await milestoneApi.create(payload)
        message.success('Đã tạo milestone')
      }
      setModal({ open: false, record: null })
      loadData()
    } catch (e) { if (e?.message) message.error(e.message) }
  }

  const openEdit = record => {
    form.setFieldsValue({
      ...record,
      planStartDate: record.planStartDate ? dayjs(record.planStartDate) : null,
      planEndDate: record.planEndDate ? dayjs(record.planEndDate) : null,
      actualStartDate: record.actualStartDate ? dayjs(record.actualStartDate) : null,
      actualEndDate: record.actualEndDate ? dayjs(record.actualEndDate) : null,
    })
    setModal({ open: true, record })
  }

  const filtered = milestones.filter(m => {
    if (filterProduct && m.productId !== filterProduct) return false
    if (filterRemind && m.remind !== filterRemind) return false
    if (filterPhase && m.phase !== filterPhase) return false
    return true
  })

  const columns = [
    { title: 'Giai đoạn', dataIndex: 'phase', key: 'phase', width: 120,
      render: v => <Tag>{v || '-'}</Tag> },
    { title: 'Dự án', dataIndex: 'productCode', key: 'productCode', width: 90,
      render: v => <Tag color="purple">{v || '-'}</Tag> },
    { title: 'Milestone', dataIndex: 'componentMilestone', key: 'componentMilestone', width: 200, ellipsis: true },
    { title: 'Chi tiết', dataIndex: 'detailMilestone', key: 'detailMilestone', width: 240, ellipsis: true },
    { title: 'GTEL', dataIndex: 'hasGtel', key: 'hasGtel', width: 60, align: 'center',
      render: v => v ? <Tag color="blue">x</Tag> : null },
    { title: 'Plan Start', dataIndex: 'planStartDate', key: 'planStartDate', width: 105,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '-' },
    { title: 'Plan End', dataIndex: 'planEndDate', key: 'planEndDate', width: 105,
      render: d => d ? <span style={{ color: STATUS_COLOR[d] }}>{new Date(d).toLocaleDateString('vi-VN')}</span> : '-' },
    { title: 'Actual Start', dataIndex: 'actualStartDate', key: 'actualStartDate', width: 105,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '-' },
    { title: 'Actual End', dataIndex: 'actualEndDate', key: 'actualEndDate', width: 105,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '-' },
    { title: 'Trạng thái', dataIndex: 'remind', key: 'remind', width: 135,
      render: v => <Tag color={REMIND_COLOR[v] || 'default'}>{v || '-'}</Tag> },
    { title: 'Thao tác', key: 'actions', width: 90, fixed: 'right',
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Xóa milestone này?" onConfirm={async () => {
            await milestoneApi.delete(r.id); loadData(); message.success('Đã xóa')
          }}><Button size="small" danger icon={<DeleteOutlined />} /></Popconfirm>
        </Space>
      )
    }
  ]

  const overdueCount = milestones.filter(m => m.remind === 'Quá hạn').length
  const upcomingCount = milestones.filter(m => m.remind === 'Sắp đến hạn').length

  if (loading) return <Spin style={{ display: 'block', margin: '80px auto' }} size="large" />
  if (error) return <Alert type="error" message={error} showIcon />

  return (
    <Card bordered={false}>
      <div className="page-header" style={{ flexWrap: 'wrap', gap: 8 }}>
        <Space>
          <Title level={5} style={{ margin: 0 }}>Milestone ({filtered.length})</Title>
          {overdueCount > 0 && <Tag color="error" icon={<WarningOutlined />}>Quá hạn: {overdueCount}</Tag>}
          {upcomingCount > 0 && <Tag color="warning">Sắp đến hạn: {upcomingCount}</Tag>}
        </Space>
        <Space wrap>
          <Select placeholder="Lọc dự án" allowClear style={{ width: 180 }}
            value={filterProduct} onChange={setFilterProduct}
            options={products.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))} />
          <Select placeholder="Lọc trạng thái" allowClear style={{ width: 170 }}
            value={filterRemind} onChange={setFilterRemind}
            options={REMIND_OPTIONS.map(r => ({ value: r, label: r }))} />
          <Select placeholder="Lọc giai đoạn" allowClear style={{ width: 150 }}
            value={filterPhase} onChange={setFilterPhase}
            options={PHASES.map(p => ({ value: p, label: p }))} />
          <Button type="primary" icon={<PlusOutlined />}
            onClick={() => { form.resetFields(); setModal({ open: true, record: null }) }}>
            Thêm milestone
          </Button>
        </Space>
      </div>
      <Table columns={columns} dataSource={filtered} rowKey="id"
        size="small" scroll={{ x: 1300 }} pagination={{ pageSize: 20 }}
        rowClassName={r => r.remind === 'Quá hạn' ? 'ant-table-row-error' : ''} />

      <Modal title={modal.record ? 'Sửa milestone' : 'Thêm milestone'}
        open={modal.open} onOk={handleSave}
        onCancel={() => setModal({ open: false, record: null })} width={700}>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="productId" label="Dự án" rules={[{ required: true }]}>
                <Select options={products.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="phase" label="Giai đoạn">
                <Select options={PHASES.map(p => ({ value: p, label: p }))} />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="componentMilestone" label="Milestone thành phần">
                <Input />
              </Form.Item>
            </Col>
            <Col span={24}>
              <Form.Item name="detailMilestone" label="Milestone chi tiết">
                <Input.TextArea rows={2} />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="hasGtel" label="GTEL" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="hasOutsourceGtel" label="Outsource (GtelSite)" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="hasOutsourceOnline" label="Outsource Online" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="planStartDate" label="Plan Start">
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="planEndDate" label="Plan End">
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="actualStartDate" label="Actual Start">
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="actualEndDate" label="Actual End">
                <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="remind" label="Trạng thái">
                <Select options={REMIND_OPTIONS.map(r => ({ value: r, label: r }))} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="currentPhase" label="Giai đoạn hiện tại">
                <Input />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </Card>
  )
}
