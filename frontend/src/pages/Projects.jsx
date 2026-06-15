import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, Select, DatePicker, Tag, Space, Popconfirm,
  Tabs, Card, Typography, message, Spin, Alert } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, FolderOutlined } from '@ant-design/icons'
import { projectGroupApi, productApi, customerApi } from '../services/api'
import dayjs from 'dayjs'

const { Title } = Typography

const STATUS_OPTIONS = ['On Track', 'Warning', 'Critical', 'Completed', 'On Hold']
const PHASE_OPTIONS = [
  'Tiền dự án', 'Đề xuất', 'Khảo sát', 'Thầu', 'Ký Hợp đồng',
  'Kickoff', 'Phân tích yêu cầu nghiệp vụ', 'Coding', 'Kiểm thử nội bộ',
  'Pilot', 'UAT', 'Golive', '3. Tài liệu bàn giao', '4. UAT', '5. Đào tạo + Triển khai'
]

const STATUS_COLOR = { 'On Track': 'success', 'Warning': 'warning', 'Critical': 'error', 'Completed': 'processing', 'On Hold': 'default' }

export default function Projects() {
  const [groups, setGroups] = useState([])
  const [products, setProducts] = useState([])
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [groupModal, setGroupModal] = useState({ open: false, record: null })
  const [productModal, setProductModal] = useState({ open: false, record: null })
  const [groupForm] = Form.useForm()
  const [productForm] = Form.useForm()

  const loadData = () => {
    setLoading(true)
    Promise.all([projectGroupApi.getAll(), productApi.getAll(), customerApi.getAll()])
      .then(([g, p, c]) => { setGroups(g); setProducts(p); setCustomers(c) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadData() }, [])

  const handleGroupSave = async () => {
    try {
      const values = await groupForm.validateFields()
      if (groupModal.record) {
        await projectGroupApi.update(groupModal.record.id, values)
        message.success('Đã cập nhật đề án')
      } else {
        await projectGroupApi.create(values)
        message.success('Đã tạo đề án')
      }
      setGroupModal({ open: false, record: null })
      loadData()
    } catch (e) { if (e?.message) message.error(e.message) }
  }

  const handleProductSave = async () => {
    try {
      const values = await productForm.validateFields()
      const payload = {
        ...values,
        startDate: values.startDate?.format('YYYY-MM-DD'),
        endDate: values.endDate?.format('YYYY-MM-DD'),
      }
      if (productModal.record) {
        await productApi.update(productModal.record.id, payload)
        message.success('Đã cập nhật sản phẩm')
      } else {
        await productApi.create(payload)
        message.success('Đã tạo sản phẩm')
      }
      setProductModal({ open: false, record: null })
      loadData()
    } catch (e) { if (e?.message) message.error(e.message) }
  }

  const openEditGroup = record => {
    groupForm.setFieldsValue({ ...record })
    setGroupModal({ open: true, record })
  }

  const openEditProduct = record => {
    productForm.setFieldsValue({
      ...record,
      projectGroupId: record.projectGroupId,
      startDate: record.startDate ? dayjs(record.startDate) : null,
      endDate: record.endDate ? dayjs(record.endDate) : null,
    })
    setProductModal({ open: true, record })
  }

  const groupColumns = [
    { title: 'Mã đề án', dataIndex: 'code', key: 'code', width: 120, render: v => <Tag color="blue">{v}</Tag> },
    { title: 'Tên đề án', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Chủ nhiệm', dataIndex: 'director', key: 'director', width: 160 },
    { title: 'Khách hàng', dataIndex: 'customerName', key: 'customerName', width: 180 },
    { title: 'Số SP', key: 'products', width: 70,
      render: (_, r) => products.filter(p => p.projectGroupId === r.id).length },
    { title: 'Thao tác', key: 'actions', width: 100,
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEditGroup(r)} />
          <Popconfirm title="Xóa đề án này?" onConfirm={async () => {
            await projectGroupApi.delete(r.id); loadData(); message.success('Đã xóa')
          }}><Button size="small" danger icon={<DeleteOutlined />} /></Popconfirm>
        </Space>
      )
    }
  ]

  const productColumns = [
    { title: 'Mã SP', dataIndex: 'code', key: 'code', width: 100, render: v => <Tag color="purple">{v}</Tag> },
    { title: 'Tên sản phẩm', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Đề án', dataIndex: 'projectGroupCode', key: 'projectGroupCode', width: 100 },
    { title: 'PM', dataIndex: 'pm', key: 'pm', width: 160 },
    { title: 'Start', dataIndex: 'startDate', key: 'startDate', width: 110,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '-' },
    { title: 'End', dataIndex: 'endDate', key: 'endDate', width: 110,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '-' },
    { title: 'Trạng thái', dataIndex: 'status', key: 'status', width: 110,
      render: v => <Tag color={STATUS_COLOR[v] || 'default'}>{v || '-'}</Tag> },
    { title: 'Giai đoạn', dataIndex: 'currentPhase', key: 'currentPhase', width: 200, ellipsis: true },
    { title: 'KH CV', dataIndex: 'hasWorkPlan', key: 'hasWorkPlan', width: 80,
      render: v => <Tag color={v ? 'success' : 'default'}>{v ? 'Yes' : 'No'}</Tag> },
    { title: 'Thao tác', key: 'actions', width: 100,
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEditProduct(r)} />
          <Popconfirm title="Xóa sản phẩm này?" onConfirm={async () => {
            await productApi.delete(r.id); loadData(); message.success('Đã xóa')
          }}><Button size="small" danger icon={<DeleteOutlined />} /></Popconfirm>
        </Space>
      )
    }
  ]

  if (loading) return <Spin style={{ display: 'block', margin: '80px auto' }} size="large" />
  if (error) return <Alert type="error" message={error} showIcon />

  return (
    <div>
      <Tabs defaultActiveKey="products" items={[
        {
          key: 'products', label: 'Sản phẩm / Dự án',
          children: (
            <Card bordered={false}>
              <div className="page-header">
                <Title level={5} style={{ margin: 0 }}>Danh sách sản phẩm ({products.length})</Title>
                <Button type="primary" icon={<PlusOutlined />}
                  onClick={() => { productForm.resetFields(); setProductModal({ open: true, record: null }) }}>
                  Thêm sản phẩm
                </Button>
              </div>
              <Table columns={productColumns} dataSource={products} rowKey="id"
                size="small" scroll={{ x: 1100 }} pagination={{ pageSize: 15 }} />
            </Card>
          )
        },
        {
          key: 'groups', label: 'Đề án (Project Group)',
          children: (
            <Card bordered={false}>
              <div className="page-header">
                <Title level={5} style={{ margin: 0 }}>Danh sách đề án ({groups.length})</Title>
                <Button type="primary" icon={<PlusOutlined />}
                  onClick={() => { groupForm.resetFields(); setGroupModal({ open: true, record: null }) }}>
                  Thêm đề án
                </Button>
              </div>
              <Table columns={groupColumns} dataSource={groups} rowKey="id"
                size="small" scroll={{ x: 800 }} pagination={{ pageSize: 15 }} />
            </Card>
          )
        }
      ]} />

      {/* Group Modal */}
      <Modal title={groupModal.record ? 'Sửa đề án' : 'Thêm đề án'}
        open={groupModal.open} onOk={handleGroupSave}
        onCancel={() => setGroupModal({ open: false, record: null })} width={560}>
        <Form form={groupForm} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="code" label="Mã đề án" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="name" label="Tên đề án" rules={[{ required: true }]}>
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="director" label="Chủ nhiệm đề án">
            <Input />
          </Form.Item>
          <Form.Item name="customerId" label="Khách hàng">
            <Select allowClear options={customers.map(c => ({ value: c.id, label: `${c.investorCode} - ${c.investorName}` }))} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Product Modal */}
      <Modal title={productModal.record ? 'Sửa sản phẩm' : 'Thêm sản phẩm'}
        open={productModal.open} onOk={handleProductSave}
        onCancel={() => setProductModal({ open: false, record: null })} width={620}>
        <Form form={productForm} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="projectGroupId" label="Đề án" rules={[{ required: true }]}>
            <Select options={groups.map(g => ({ value: g.id, label: `${g.code} - ${g.name}` }))} />
          </Form.Item>
          <Form.Item name="code" label="Mã sản phẩm" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="name" label="Tên sản phẩm" rules={[{ required: true }]}>
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="pm" label="Project Manager">
            <Input />
          </Form.Item>
          <Form.Item name="startDate" label="Ngày bắt đầu">
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="endDate" label="Ngày kết thúc">
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="status" label="Trạng thái">
            <Select options={STATUS_OPTIONS.map(s => ({ value: s, label: s }))} />
          </Form.Item>
          <Form.Item name="currentPhase" label="Giai đoạn hiện tại">
            <Select allowClear showSearch options={PHASE_OPTIONS.map(p => ({ value: p, label: p }))} />
          </Form.Item>
          <Form.Item name="hasWorkPlan" label="Đã có kế hoạch công việc?">
            <Select options={[{ value: true, label: 'Yes' }, { value: false, label: 'No' }]} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
