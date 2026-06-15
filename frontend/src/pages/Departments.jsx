import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, InputNumber, Space, Popconfirm,
  Card, Typography, message, Spin, Alert } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { departmentApi } from '../services/api'

const { Title } = Typography

export default function Departments() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState({ open: false, record: null })
  const [form] = Form.useForm()

  const load = () => {
    setLoading(true)
    departmentApi.getAll().then(setData).catch(e => setError(e.message)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      if (modal.record) { await departmentApi.update(modal.record.id, values); message.success('Đã cập nhật') }
      else { await departmentApi.create(values); message.success('Đã thêm') }
      setModal({ open: false, record: null }); load()
    } catch (e) { if (e?.message) message.error(e.message) }
  }

  const openEdit = r => { form.setFieldsValue(r); setModal({ open: true, record: r }) }

  const columns = [
    { title: 'Trung tâm', dataIndex: 'center', key: 'center', width: 200 },
    { title: 'Bộ phận', dataIndex: 'division', key: 'division' },
    { title: 'GĐ / Quản lý', dataIndex: 'manager', key: 'manager', width: 200 },
    { title: 'Thứ tự', dataIndex: 'sortOrder', key: 'sortOrder', width: 90 },
    {
      title: 'Thao tác', key: 'actions', width: 100,
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Xóa bộ phận này?" onConfirm={async () => { await departmentApi.delete(r.id); load(); message.success('Đã xóa') }}>
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
        <Title level={5} style={{ margin: 0 }}>Tổ chức Phòng ban ({data.length})</Title>
        <Button type="primary" icon={<PlusOutlined />}
          onClick={() => { form.resetFields(); setModal({ open: true, record: null }) }}>
          Thêm bộ phận
        </Button>
      </div>
      <Table columns={columns} dataSource={data} rowKey="id" size="small" pagination={{ pageSize: 20 }} />

      <Modal title={modal.record ? 'Sửa bộ phận' : 'Thêm bộ phận'}
        open={modal.open} onOk={handleSave} onCancel={() => setModal({ open: false, record: null })} width={500}>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="center" label="Trung tâm" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="division" label="Bộ phận"><Input /></Form.Item>
          <Form.Item name="manager" label="GĐ / Quản lý"><Input /></Form.Item>
          <Form.Item name="sortOrder" label="Thứ tự hiển thị"><InputNumber style={{ width: '100%' }} /></Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
