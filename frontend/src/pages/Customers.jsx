import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, Space, Popconfirm, Card, Typography, message, Spin, Alert } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { customerApi } from '../services/api'

const { Title } = Typography

export default function Customers() {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState({ open: false, record: null })
  const [form] = Form.useForm()

  const loadData = () => {
    setLoading(true)
    customerApi.getAll()
      .then(setCustomers)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadData() }, [])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      if (modal.record) {
        await customerApi.update(modal.record.id, values)
        message.success('Đã cập nhật')
      } else {
        await customerApi.create(values)
        message.success('Đã tạo khách hàng')
      }
      setModal({ open: false, record: null })
      loadData()
    } catch (e) { if (e?.message) message.error(e.message) }
  }

  const openEdit = record => {
    form.setFieldsValue(record)
    setModal({ open: true, record })
  }

  const columns = [
    { title: 'STT', key: 'stt', width: 60, render: (_, __, i) => i + 1 },
    { title: 'Mã chủ đầu tư', dataIndex: 'investorCode', key: 'investorCode', width: 150 },
    { title: 'Tên chủ đầu tư', dataIndex: 'investorName', key: 'investorName', ellipsis: true },
    { title: 'Mã đơn vị thụ hưởng', dataIndex: 'beneficiaryCode', key: 'beneficiaryCode', width: 170 },
    { title: 'Tên đơn vị thụ hưởng', dataIndex: 'beneficiaryName', key: 'beneficiaryName', ellipsis: true },
    { title: 'Mã đề án', dataIndex: 'projectGroupCode', key: 'projectGroupCode', width: 120 },
    {
      title: 'Thao tác', key: 'actions', width: 100,
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Xóa khách hàng này?" onConfirm={async () => {
            await customerApi.delete(r.id); loadData(); message.success('Đã xóa')
          }}><Button size="small" danger icon={<DeleteOutlined />} /></Popconfirm>
        </Space>
      )
    }
  ]

  if (loading) return <Spin style={{ display: 'block', margin: '80px auto' }} size="large" />
  if (error) return <Alert type="error" message={error} showIcon />

  return (
    <Card bordered={false}>
      <div className="page-header">
        <Title level={5} style={{ margin: 0 }}>Khách hàng / Chủ đầu tư ({customers.length})</Title>
        <Button type="primary" icon={<PlusOutlined />}
          onClick={() => { form.resetFields(); setModal({ open: true, record: null }) }}>
          Thêm khách hàng
        </Button>
      </div>
      <Table columns={columns} dataSource={customers} rowKey="id"
        size="small" scroll={{ x: 900 }} pagination={{ pageSize: 20 }} />

      <Modal title={modal.record ? 'Sửa khách hàng' : 'Thêm khách hàng'}
        open={modal.open} onOk={handleSave}
        onCancel={() => setModal({ open: false, record: null })} width={560}>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="investorCode" label="Mã chủ đầu tư" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="investorName" label="Tên chủ đầu tư">
            <Input />
          </Form.Item>
          <Form.Item name="beneficiaryCode" label="Mã đơn vị thụ hưởng">
            <Input />
          </Form.Item>
          <Form.Item name="beneficiaryName" label="Tên đơn vị thụ hưởng">
            <Input />
          </Form.Item>
          <Form.Item name="projectGroupCode" label="Mã đề án liên kết">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
