import React, { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, Select, DatePicker, Card, Typography,
  message, Spin, Alert, Space, Popconfirm, Tag, Tooltip, Progress } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { allocationApi, productApi, employeeApi } from '../services/api'
import { useProject } from '../contexts/ProjectContext'
import dayjs from 'dayjs'

const { Title } = Typography

const MONTHS = [
  'T6-2025','T7-2025','T8-2025','T9-2025','T10-2025','T11-2025','T12-2025',
  'T1-2026','T2-2026','T3-2026','T4-2026','T5-2026','T6-2026','T7-2026','T8-2026','T9-2026'
]

export default function Allocations() {
  const { selectedProject } = useProject()
  const [allocations, setAllocations] = useState([])
  const [products, setProducts] = useState([])
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState({ open: false, record: null })
  const [form] = Form.useForm()
  const [filterProduct, setFilterProduct] = useState(null)
  const [filterEmployee, setFilterEmployee] = useState(null)

  useEffect(() => {
    setFilterProduct(selectedProject?.id ?? null)
  }, [selectedProject])

  const loadData = () => {
    setLoading(true)
    Promise.all([allocationApi.getAll(), productApi.getAll(), employeeApi.getAll()])
      .then(([a, p, e]) => { setAllocations(a); setProducts(p); setEmployees(e) })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadData() }, [])

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      const payload = {
        ...values,
        fromDate: values.fromDate?.format('YYYY-MM-DD'),
        toDate: values.toDate?.format('YYYY-MM-DD'),
        allocationPercent: values.allocationPercent ? parseFloat(values.allocationPercent) / 100 : null,
        monthlyAllocations: values.monthlyAllocations || [],
      }
      if (modal.record) {
        await allocationApi.update(modal.record.id, payload)
        message.success('Đã cập nhật')
      } else {
        await allocationApi.create(payload)
        message.success('Đã tạo phân bổ')
      }
      setModal({ open: false, record: null })
      loadData()
    } catch (e) { if (e?.message) message.error(e.message) }
  }

  const openEdit = record => {
    form.setFieldsValue({
      ...record,
      allocationPercent: record.allocationPercent ? Math.round(record.allocationPercent * 100) : null,
      fromDate: record.fromDate ? dayjs(record.fromDate) : null,
      toDate: record.toDate ? dayjs(record.toDate) : null,
    })
    setModal({ open: true, record })
  }

  const filtered = allocations.filter(a => {
    if (filterProduct && a.productId !== filterProduct) return false
    if (filterEmployee && a.employeeId !== filterEmployee) return false
    return true
  })

  const getMonthPercent = (allocation, month) => {
    const monthly = allocation.monthlyAllocations?.find(m => m.yearMonth === month)
    return monthly ? Math.round(monthly.percent * 100) : null
  }

  const columns = [
    { title: 'Dự án', dataIndex: 'productCode', key: 'productCode', width: 90,
      render: v => <Tag color="purple">{v}</Tag>, fixed: 'left' },
    { title: 'Nhân sự', dataIndex: 'employeeName', key: 'employeeName', width: 160,
      render: (v, r) => (
        <div>
          <div style={{ fontWeight: 500 }}>{v}</div>
          <div style={{ fontSize: 12, color: '#888' }}>{r.employeeCompany}</div>
        </div>
      ), fixed: 'left' },
    { title: 'Vai trò', dataIndex: 'roleInProject', key: 'roleInProject', width: 150, ellipsis: true },
    { title: 'Từ ngày', dataIndex: 'fromDate', key: 'fromDate', width: 100,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '-' },
    { title: 'Đến ngày', dataIndex: 'toDate', key: 'toDate', width: 100,
      render: d => d ? new Date(d).toLocaleDateString('vi-VN') : '-' },
    { title: '% KH', dataIndex: 'allocationPercent', key: 'allocationPercent', width: 80,
      render: v => v ? <Tag color="blue">{Math.round(v * 100)}%</Tag> : '-' },
    ...MONTHS.map(m => ({
      title: m, key: m, width: 75, align: 'center',
      render: (_, r) => {
        const p = getMonthPercent(r, m)
        return p != null ? (
          <Tooltip title={`${p}%`}>
            <div className="percent-bar" style={{ width: 50, margin: '0 auto' }}>
              <div className="percent-bar-fill" style={{ width: `${Math.min(p, 100)}%` }} />
            </div>
            <div style={{ fontSize: 11, textAlign: 'center', marginTop: 2 }}>{p}%</div>
          </Tooltip>
        ) : <span style={{ color: '#ccc' }}>-</span>
      }
    })),
    { title: 'Thao tác', key: 'actions', width: 90, fixed: 'right',
      render: (_, r) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(r)} />
          <Popconfirm title="Xóa phân bổ này?" onConfirm={async () => {
            await allocationApi.delete(r.id); loadData(); message.success('Đã xóa')
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
        <Title level={5} style={{ margin: 0 }}>Phân bổ nguồn lực ({filtered.length} bản ghi)</Title>
        <Space wrap>
          <Select placeholder="Lọc theo dự án" allowClear style={{ width: 180 }}
            value={filterProduct} onChange={setFilterProduct}
            options={products.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))} />
          <Select placeholder="Lọc theo nhân sự" allowClear style={{ width: 200 }}
            value={filterEmployee} onChange={setFilterEmployee}
            options={employees.map(e => ({ value: e.id, label: e.name }))}
            showSearch filterOption={(input, opt) => opt.label.toLowerCase().includes(input.toLowerCase())} />
          <Button type="primary" icon={<PlusOutlined />}
            onClick={() => { form.resetFields(); setModal({ open: true, record: null }) }}>
            Thêm phân bổ
          </Button>
        </Space>
      </div>
      <Table columns={columns} dataSource={filtered} rowKey="id"
        size="small" scroll={{ x: 1800 }} pagination={{ pageSize: 20 }} />

      <Modal title={modal.record ? 'Sửa phân bổ' : 'Thêm phân bổ nguồn lực'}
        open={modal.open} onOk={handleSave}
        onCancel={() => setModal({ open: false, record: null })} width={620}>
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="productId" label="Dự án / Sản phẩm" rules={[{ required: true }]}>
            <Select showSearch filterOption={(i, o) => o.label.toLowerCase().includes(i.toLowerCase())}
              options={products.map(p => ({ value: p.id, label: `${p.code} - ${p.name}` }))} />
          </Form.Item>
          <Form.Item name="employeeId" label="Nhân sự" rules={[{ required: true }]}>
            <Select showSearch filterOption={(i, o) => o.label.toLowerCase().includes(i.toLowerCase())}
              options={employees.map(e => ({ value: e.id, label: `${e.name} (${e.company || ''})` }))} />
          </Form.Item>
          <Form.Item name="roleInProject" label="Vai trò trong dự án">
            <Input placeholder="VD: SA, Dev, Tester, PM..." />
          </Form.Item>
          <Form.Item name="fromDate" label="Từ ngày">
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="toDate" label="Đến ngày">
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>
          <Form.Item name="allocationPercent" label="% Phân bổ kế hoạch">
            <Input type="number" min={0} max={100} suffix="%" placeholder="VD: 30" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
