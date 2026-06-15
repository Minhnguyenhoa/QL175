import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, Select, Space, Popconfirm, Tag,
  Card, Typography, message, Spin, Alert, Row, Col } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { employeeApi } from '../services/api'

const { Title } = Typography

const CONTRACT_TYPES = ['Chính thức', 'Outsourcing', 'Thời vụ']
const WORK_MODES = ['GTel Site', 'Remote', 'Hybrid', 'Online']
const WORK_TIMES = ['Full-time', 'Part-time']
const COMPANIES = ['GTEL ICT', 'MIGI', 'AGILETECH', 'ALADIN', 'VISSOFT']

export default function Employees() {
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState({ open: false, record: null })
  const [form] = Form.useForm()
  const [search, setSearch] = useState('')

  const loadData = () => {
    setLoading(true)
    employeeApi.getAll()
      .then(setEmployees)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadData() }, [])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      if (modal.record) {
        await employeeApi.update(modal.record.id, values)
        message.success('Đã cập nhật nhân sự')
      } else {
        await employeeApi.create(values)
        message.success('Đã thêm nhân sự')
      }
      setModal({ open: false, record: null })
      loadData()
    } catch (e) { if (e?.message) message.error(e.message) }
  }

  const openEdit = record => {
    form.setFieldsValue(record)
    setModal({ open: true, record })
  }

  const filtered = employees.filter(e =>
    !search || e.name?.toLowerCase().includes(search.toLowerCase()) ||
    e.company?.toLowerCase().includes(search.toLowerCase())
  )

  const columns = [
    { title: 'STT', key: 'stt', width: 55, render: (_, __, i) => i + 1 },
    { title: 'Họ tên', dataIndex: 'name', key: 'name', width: 180,
      render: v => <span style={{ fontWeight: 500 }}>{v}</span> },
    { title: 'Công ty', dataIndex: 'company', key: 'company', width: 120,
      render: v => <Tag color={v === 'GTEL ICT' ? 'blue' : 'orange'}>{v || '-'}</Tag> },
    { title: 'Phòng/Trung tâm', dataIndex: 'department', key: 'department', width: 120 },
    { title: 'Role', dataIndex: 'role', key: 'role', width: 120 },
    { title: 'Hình thức HĐ', dataIndex: 'contractType', key: 'contractType', width: 130,
      render: v => <Tag color={v === 'Chính thức' ? 'green' : 'geekblue'}>{v || '-'}</Tag> },
    { title: 'Làm việc', dataIndex: 'workMode', key: 'workMode', width: 110 },
    { title: 'Thời gian', dataIndex: 'workTime', key: 'workTime', width: 100 },
    { title: 'Trạng thái', dataIndex: 'workStatus', key: 'workStatus', width: 110 },
    { title: 'Thao tác', key: 'actions', width: 100, fixed: 'right',
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Xóa nhân sự này?" onConfirm={async () => {
            await employeeApi.delete(r.id); loadData(); message.success('Đã xóa')
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
        <Title level={5} style={{ margin: 0 }}>Nhân sự ({employees.length})</Title>
        <Space>
          <Input.Search placeholder="Tìm tên, công ty..." value={search}
            onChange={e => setSearch(e.target.value)} style={{ width: 240 }} allowClear />
          <Button type="primary" icon={<PlusOutlined />}
            onClick={() => { form.resetFields(); setModal({ open: true, record: null }) }}>
            Thêm nhân sự
          </Button>
        </Space>
      </div>
      <Table columns={columns} dataSource={filtered} rowKey="id"
        size="small" scroll={{ x: 1200 }} pagination={{ pageSize: 20 }} />

      <Modal title={modal.record ? 'Sửa nhân sự' : 'Thêm nhân sự'}
        open={modal.open} onOk={handleSave}
        onCancel={() => setModal({ open: false, record: null })} width={600}>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="name" label="Họ tên" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="account" label="Account">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="company" label="Công ty">
                <Select allowClear mode="tags" options={COMPANIES.map(c => ({ value: c, label: c }))} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="department" label="Phòng / Trung tâm">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="role" label="Role">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="level" label="Level">
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="contractType" label="Hình thức hợp đồng">
                <Select options={CONTRACT_TYPES.map(t => ({ value: t, label: t }))} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="workMode" label="Hình thức làm việc">
                <Select options={WORK_MODES.map(m => ({ value: m, label: m }))} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="workTime" label="Thời gian làm việc">
                <Select options={WORK_TIMES.map(t => ({ value: t, label: t }))} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="workStatus" label="Trạng thái làm việc">
                <Input />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </Card>
  )
}
