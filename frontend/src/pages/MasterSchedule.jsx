import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, InputNumber, Select, Space, Popconfirm,
  Card, Typography, message, Spin, Alert, Tag } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { taskApi, productApi } from '../services/api'
import { useProject } from '../contexts/ProjectContext'

const { Title } = Typography

const PHASE_GROUPS = ['Giai đoạn 1', 'Giai đoạn 2', 'Giai đoạn 3', '1. Chuẩn bị']

export default function MasterSchedule() {
  const { selectedProject } = useProject()
  const [tasks, setTasks] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState({ open: false, record: null })
  const [form] = Form.useForm()
  const [filterProduct, setFilterProduct] = useState(null)
  const [filterPhase, setFilterPhase] = useState(null)
  const [expandedFeature, setExpandedFeature] = useState(null)

  useEffect(() => {
    setFilterProduct(selectedProject?.id ?? null)
  }, [selectedProject])

  const load = () => {
    setLoading(true)
    Promise.all([taskApi.getAll(), productApi.getAll()])
      .then(([t, p]) => { setTasks(t); setProducts(p) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      if (modal.record) { await taskApi.update(modal.record.id, values); message.success('Đã cập nhật') }
      else { await taskApi.create(values); message.success('Đã thêm task') }
      setModal({ open: false, record: null }); load()
    } catch (e) { if (e?.message) message.error(e.message) }
  }

  const openEdit = r => { form.setFieldsValue(r); setModal({ open: true, record: r }) }

  const filtered = tasks.filter(t => {
    if (filterProduct && t.productId !== filterProduct) return false
    if (filterPhase && t.phaseGroup !== filterPhase) return false
    return true
  })

  const columns = [
    { title: 'Giai đoạn', dataIndex: 'phaseGroup', key: 'phaseGroup', width: 130,
      render: v => <Tag color="blue">{v || '-'}</Tag> },
    { title: 'Dự án', dataIndex: 'productCode', key: 'productCode', width: 80,
      render: v => <Tag color="purple">{v || '-'}</Tag> },
    { title: '#', dataIndex: 'taskNo', key: 'taskNo', width: 55, align: 'center' },
    { title: 'Tên Task / Chức năng', dataIndex: 'taskName', key: 'taskName', width: 220,
      render: v => <span style={{ fontWeight: 500 }}>{v}</span> },
    { title: 'Nhóm tính năng', dataIndex: 'featureGroup', key: 'featureGroup', width: 200, ellipsis: true },
    { title: 'Nội dung chi tiết', dataIndex: 'content', key: 'content',
      render: v => v ? (
        <div style={{ whiteSpace: 'pre-line', fontSize: 12, color: '#555', maxHeight: 80, overflow: 'auto' }}>{v}</div>
      ) : '-' },
    {
      title: 'Thao tác', key: 'actions', width: 95, fixed: 'right',
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Xóa task này?" onConfirm={async () => { await taskApi.delete(r.id); load(); message.success('Đã xóa') }}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  // unique phase groups from current data
  const phaseGroups = [...new Set(tasks.map(t => t.phaseGroup).filter(Boolean))]

  if (loading) return <Spin style={{ display: 'block', margin: '80px auto' }} size="large" />
  if (error) return <Alert type="error" message={error} showIcon />

  return (
    <Card bordered={false}>
      <div className="page-header" style={{ flexWrap: 'wrap', gap: 8 }}>
        <Title level={5} style={{ margin: 0 }}>Master Schedule / WBS ({filtered.length} tasks)</Title>
        <Space wrap>
          <Select placeholder="Lọc dự án" allowClear style={{ width: 180 }}
            value={filterProduct} onChange={setFilterProduct}
            options={products.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))} />
          <Select placeholder="Lọc giai đoạn" allowClear style={{ width: 160 }}
            value={filterPhase} onChange={setFilterPhase}
            options={phaseGroups.map(g => ({ value: g, label: g }))} />
          <Button type="primary" icon={<PlusOutlined />}
            onClick={() => { form.resetFields(); setModal({ open: true, record: null }) }}>
            Thêm task
          </Button>
        </Space>
      </div>
      <Table columns={columns} dataSource={filtered} rowKey="id"
        size="small" scroll={{ x: 1000 }} pagination={{ pageSize: 20 }} />

      <Modal title={modal.record ? 'Sửa task' : 'Thêm task'}
        open={modal.open} onOk={handleSave} onCancel={() => setModal({ open: false, record: null })} width={620}>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="productId" label="Dự án / Sản phẩm" rules={[{ required: true }]}>
            <Select options={products.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))} />
          </Form.Item>
          <Form.Item name="phaseGroup" label="Giai đoạn">
            <Select mode="tags" options={[...PHASE_GROUPS, ...phaseGroups].filter((v,i,a)=>a.indexOf(v)===i).map(g => ({ value: g, label: g }))} />
          </Form.Item>
          <Form.Item name="taskNo" label="Số thứ tự task">
            <InputNumber style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="taskName" label="Tên task / Chức năng" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="featureGroup" label="Nhóm tính năng">
            <Input />
          </Form.Item>
          <Form.Item name="content" label="Nội dung chi tiết">
            <Input.TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
