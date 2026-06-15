import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, InputNumber, Select, Space, Popconfirm,
  Card, Typography, message, Spin, Alert, Tag } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { phaseApi } from '../services/api'

const { Title } = Typography

const GROUP_OPTIONS = ['Tiền dự án', 'Sản xuất', 'Kết thúc']
const GROUP_COLORS = { 'Tiền dự án': 'orange', 'Sản xuất': 'blue', 'Kết thúc': 'green' }

export default function Phases() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState({ open: false, record: null })
  const [form] = Form.useForm()

  const load = () => {
    setLoading(true)
    phaseApi.getAll().then(setData).catch(e => setError(e.message)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      if (modal.record) { await phaseApi.update(modal.record.id, values); message.success('Đã cập nhật') }
      else { await phaseApi.create(values); message.success('Đã thêm') }
      setModal({ open: false, record: null }); load()
    } catch (e) { if (e?.message) message.error(e.message) }
  }

  const openEdit = r => { form.setFieldsValue(r); setModal({ open: true, record: r }) }

  // group phases for display
  const grouped = data.reduce((acc, p) => {
    const g = p.phaseGroup || 'Khác'
    if (!acc[g]) acc[g] = []
    acc[g].push(p)
    return acc
  }, {})

  const columns = [
    { title: 'Nhóm giai đoạn', dataIndex: 'phaseGroup', key: 'phaseGroup', width: 160,
      render: v => <Tag color={GROUP_COLORS[v] || 'default'}>{v || '-'}</Tag> },
    { title: 'Tên giai đoạn thành phần', dataIndex: 'phaseName', key: 'phaseName' },
    { title: 'Ghi chú', dataIndex: 'note', key: 'note', width: 250, ellipsis: true },
    { title: 'Thứ tự', dataIndex: 'sortOrder', key: 'sortOrder', width: 80 },
    {
      title: 'Thao tác', key: 'actions', width: 100,
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Xóa giai đoạn này?" onConfirm={async () => { await phaseApi.delete(r.id); load(); message.success('Đã xóa') }}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ]

  if (loading) return <Spin style={{ display: 'block', margin: '80px auto' }} size="large" />
  if (error) return <Alert type="error" message={error} showIcon />

  return (
    <Card bordered={false}>
      <div className="page-header">
        <Title level={5} style={{ margin: 0 }}>Cấu hình Giai đoạn ({data.length})</Title>
        <Button type="primary" icon={<PlusOutlined />}
          onClick={() => { form.resetFields(); setModal({ open: true, record: null }) }}>
          Thêm giai đoạn
        </Button>
      </div>
      <Table columns={columns} dataSource={data} rowKey="id" size="small"
        pagination={{ pageSize: 30 }}
        rowClassName={(_, i) => i % 2 === 0 ? '' : 'ant-table-row-striped'} />

      <Modal title={modal.record ? 'Sửa giai đoạn' : 'Thêm giai đoạn'}
        open={modal.open} onOk={handleSave} onCancel={() => setModal({ open: false, record: null })} width={500}>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="phaseGroup" label="Nhóm giai đoạn" rules={[{ required: true }]}>
            <Select mode="tags" options={GROUP_OPTIONS.map(g => ({ value: g, label: g }))} />
          </Form.Item>
          <Form.Item name="phaseName" label="Tên giai đoạn thành phần" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="note" label="Ghi chú"><Input /></Form.Item>
          <Form.Item name="sortOrder" label="Thứ tự"><InputNumber style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
