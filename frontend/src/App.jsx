import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation, useNavigate } from 'react-router-dom'
import { Layout, Menu, Typography, Avatar, Space, Button, Popconfirm, Select, Tag } from 'antd'
import { LogoutOutlined, ProjectOutlined as ProjIcon } from '@ant-design/icons'
import { isAuthenticated, clearAuth, getUser } from './auth'
import { ProjectProvider, useProject } from './contexts/ProjectContext'
import { productApi } from './services/api'
import LoginPage from './pages/LoginPage'
import {
  DashboardOutlined, ProjectOutlined, TeamOutlined, ScheduleOutlined,
  DeploymentUnitOutlined, UserOutlined, AppstoreOutlined,
  ApartmentOutlined, SettingOutlined, BarChartOutlined,
  CalendarOutlined, UnorderedListOutlined, HistoryOutlined, FileTextOutlined,
} from '@ant-design/icons'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Employees from './pages/Employees'
import Allocations from './pages/Allocations'
import Milestones from './pages/Milestones'
import Customers from './pages/Customers'
import Departments from './pages/Departments'
import Phases from './pages/Phases'
import MasterSchedule from './pages/MasterSchedule'
import ResourceSummary from './pages/ResourceSummary'
import TimelineSummary from './pages/TimelineSummary'
import AllocationHistoryPage from './pages/AllocationHistoryPage'
import ResourceSummaryOld from './pages/ResourceSummaryOld'
import ReportPage from './pages/ReportPage'
import PersonalView from './pages/PersonalView'

const { Sider, Content, Header } = Layout
const { Title, Text } = Typography

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: <Link to="/">Tổng quan</Link>, title: 'Tổng quan' },
  {
    key: 'projects-group', label: 'Quản lý Dự án', icon: <ProjectOutlined />,
    children: [
      { key: '/projects', icon: <ProjectOutlined />, label: <Link to="/projects">DS Dự án & Sản phẩm</Link>, title: 'DS Dự án' },
      { key: '/customers', icon: <AppstoreOutlined />, label: <Link to="/customers">Khách hàng</Link>, title: 'Khách hàng' },
      { key: '/master-schedule', icon: <UnorderedListOutlined />, label: <Link to="/master-schedule">Master Schedule</Link>, title: 'Master Schedule' },
    ]
  },
  {
    key: 'hr-group', label: 'Nhân sự & Nguồn lực', icon: <TeamOutlined />,
    children: [
      { key: '/employees', icon: <TeamOutlined />, label: <Link to="/employees">Nhân sự</Link>, title: 'Nhân sự' },
      { key: '/departments', icon: <ApartmentOutlined />, label: <Link to="/departments">Tổ chức phòng ban</Link>, title: 'Phòng ban' },
      { key: '/allocations', icon: <DeploymentUnitOutlined />, label: <Link to="/allocations">Phân bổ nguồn lực</Link>, title: 'Phân bổ NL' },
      { key: '/personal-view', icon: <UserOutlined />, label: <Link to="/personal-view">View cá nhân</Link>, title: 'View cá nhân' },
      { key: '/resource-summary', icon: <BarChartOutlined />, label: <Link to="/resource-summary">Resource Summary</Link>, title: 'Resource Summary' },
    ]
  },
  {
    key: 'history-group', label: 'Dữ liệu lịch sử', icon: <HistoryOutlined />,
    children: [
      { key: '/allocation-history', icon: <HistoryOutlined />, label: <Link to="/allocation-history">Phân bổ NL (Cũ)</Link>, title: 'Phân bổ NL Cũ' },
      { key: '/resource-summary-old', icon: <BarChartOutlined />, label: <Link to="/resource-summary-old">Resource Summary (Cũ)</Link>, title: 'Resource Summary Cũ' },
    ]
  },
  {
    key: 'timeline-group', label: 'Tiến độ', icon: <ScheduleOutlined />,
    children: [
      { key: '/milestones', icon: <ScheduleOutlined />, label: <Link to="/milestones">Deliverable List</Link>, title: 'Milestones' },
      { key: '/timeline', icon: <CalendarOutlined />, label: <Link to="/timeline">Timeline Summary</Link>, title: 'Timeline Summary' },
    ]
  },
  { key: '/report', icon: <FileTextOutlined />, label: <Link to="/report">Báo cáo dự án</Link>, title: 'Báo cáo dự án' },
  { key: '/phases', icon: <SettingOutlined />, label: <Link to="/phases">Cấu hình Giai đoạn</Link>, title: 'Cấu hình' },
]

const flatMenu = menuItems.flatMap(m => m.children ? m.children : [m])

function PrivateRoute({ children }) {
  return isAuthenticated() ? children : <Navigate to="/login" replace />
}

// Màu badge cho từng mã dự án
const PROJ_COLORS = {
  HIS: 'blue', LIS: 'cyan', EMR: 'purple',
  KSK: 'orange', QLTTDL: 'green', THDB: 'red',
}

function ProjectSelector() {
  const [products, setProducts] = useState([])
  const { selectedProject, setSelectedProject } = useProject()

  useEffect(() => {
    productApi.getAll().then(setProducts).catch(() => {})
  }, [])

  const options = [
    { value: '__all__', label: <Text style={{ color: '#1677ff', fontWeight: 600 }}>Tất cả dự án</Text> },
    ...products.map(p => ({
      value: String(p.id),
      label: (
        <Space size={4}>
          <Tag color={PROJ_COLORS[p.code] || 'default'} style={{ margin: 0, fontSize: 11 }}>{p.code}</Tag>
          <span style={{ fontSize: 12 }}>{p.name}</span>
        </Space>
      ),
    }))
  ]

  return (
    <Select
      value={selectedProject ? String(selectedProject.id) : '__all__'}
      onChange={val => {
        if (val === '__all__') { setSelectedProject(null); return }
        const p = products.find(p => String(p.id) === val)
        if (p) setSelectedProject(p)
      }}
      options={options}
      style={{ minWidth: 180 }}
      size="small"
      variant="outlined"
      popupMatchSelectWidth={false}
      suffixIcon={<ProjIcon style={{ color: '#1677ff' }} />}
    />
  )
}

function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const user = getUser()

  const currentTitle = flatMenu.find(m => m.key === location.pathname)?.title || 'Quản trị Dự án'
  const openKeys = menuItems.filter(m => m.children?.some(c => c.key === location.pathname)).map(m => m.key)

  const handleLogout = () => {
    clearAuth()
    navigate('/login', { replace: true })
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} theme="dark" width={240}
        style={{ boxShadow: '2px 0 8px rgba(0,0,0,0.15)' }}>
        <div style={{
          height: 56, display: 'flex', alignItems: 'center', justifyContent: 'center',
          padding: '0 16px', borderBottom: '1px solid rgba(255,255,255,0.1)'
        }}>
          {!collapsed
            ? <Title level={5} style={{ color: '#fff', margin: 0, fontSize: 13 }}>Quản trị Dự án</Title>
            : <ProjectOutlined style={{ color: '#fff', fontSize: 18 }} />}
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[location.pathname]}
          defaultOpenKeys={openKeys} items={menuItems} style={{ marginTop: 4 }} />
      </Sider>
      <Layout>
        <Header style={{
          background: '#fff', padding: '0 24px', display: 'flex',
          alignItems: 'center', justifyContent: 'space-between',
          boxShadow: '0 1px 4px rgba(0,0,0,0.1)', zIndex: 1, height: 52
        }}>
          <Text style={{ fontSize: 15, fontWeight: 600 }}>{currentTitle}</Text>
          <Space>
            <ProjectSelector />
            <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1677ff' }} size={32} />
            <Text style={{ fontSize: 13 }}>{user?.fullName || 'Admin'}</Text>
            <Popconfirm title="Đăng xuất?" onConfirm={handleLogout} okText="Đăng xuất" cancelText="Huỷ">
              <Button icon={<LogoutOutlined />} size="small" type="text" />
            </Popconfirm>
          </Space>
        </Header>
        <Content style={{ margin: 20, minHeight: 'calc(100vh - 92px)' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/departments" element={<Departments />} />
            <Route path="/allocations" element={<Allocations />} />
            <Route path="/personal-view" element={<PersonalView />} />
            <Route path="/resource-summary" element={<ResourceSummary />} />
            <Route path="/milestones" element={<Milestones />} />
            <Route path="/timeline" element={<TimelineSummary />} />
            <Route path="/master-schedule" element={<MasterSchedule />} />
            <Route path="/phases" element={<Phases />} />
            <Route path="/allocation-history" element={<AllocationHistoryPage />} />
            <Route path="/resource-summary-old" element={<ResourceSummaryOld />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={<PrivateRoute><ProjectProvider><AppLayout /></ProjectProvider></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}
