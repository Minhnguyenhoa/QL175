import axios from 'axios'
import { getToken, clearAuth } from '../auth'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use(config => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      clearAuth()
      window.location.href = '/login'
    }
    const msg = err.response?.data?.message || err.message || 'Có lỗi xảy ra'
    return Promise.reject(new Error(msg))
  }
)

export const customerApi = {
  getAll: () => api.get('/customers'),
  getById: id => api.get(`/customers/${id}`),
  create: data => api.post('/customers', data),
  update: (id, data) => api.put(`/customers/${id}`, data),
  delete: id => api.delete(`/customers/${id}`),
}

export const projectGroupApi = {
  getAll: () => api.get('/project-groups'),
  getById: id => api.get(`/project-groups/${id}`),
  create: data => api.post('/project-groups', data),
  update: (id, data) => api.put(`/project-groups/${id}`, data),
  delete: id => api.delete(`/project-groups/${id}`),
}

export const productApi = {
  getAll: () => api.get('/products'),
  getById: id => api.get(`/products/${id}`),
  getByProjectGroup: pgId => api.get(`/products/project-group/${pgId}`),
  create: data => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: id => api.delete(`/products/${id}`),
}

export const employeeApi = {
  getAll: () => api.get('/employees'),
  getById: id => api.get(`/employees/${id}`),
  create: data => api.post('/employees', data),
  update: (id, data) => api.put(`/employees/${id}`, data),
  delete: id => api.delete(`/employees/${id}`),
}

export const allocationApi = {
  getAll: () => api.get('/allocations'),
  getById: id => api.get(`/allocations/${id}`),
  getByProduct: productId => api.get(`/allocations/product/${productId}`),
  getByEmployee: employeeId => api.get(`/allocations/employee/${employeeId}`),
  create: data => api.post('/allocations', data),
  update: (id, data) => api.put(`/allocations/${id}`, data),
  delete: id => api.delete(`/allocations/${id}`),
}

export const milestoneApi = {
  getAll: () => api.get('/milestones'),
  getById: id => api.get(`/milestones/${id}`),
  getByProduct: productId => api.get(`/milestones/product/${productId}`),
  getOverdueUpcoming: () => api.get('/milestones/overdue-upcoming'),
  create: data => api.post('/milestones', data),
  update: (id, data) => api.put(`/milestones/${id}`, data),
  delete: id => api.delete(`/milestones/${id}`),
}

export const dashboardApi = {
  get: (productId) => api.get('/dashboard', { params: productId ? { productId } : {} }),
}

export const departmentApi = {
  getAll: () => api.get('/departments'),
  getById: id => api.get(`/departments/${id}`),
  create: data => api.post('/departments', data),
  update: (id, data) => api.put(`/departments/${id}`, data),
  delete: id => api.delete(`/departments/${id}`),
}

export const phaseApi = {
  getAll: () => api.get('/phases'),
  getById: id => api.get(`/phases/${id}`),
  create: data => api.post('/phases', data),
  update: (id, data) => api.put(`/phases/${id}`, data),
  delete: id => api.delete(`/phases/${id}`),
}

export const taskApi = {
  getAll: () => api.get('/tasks'),
  getById: id => api.get(`/tasks/${id}`),
  getByProduct: productId => api.get(`/tasks/product/${productId}`),
  create: data => api.post('/tasks', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: id => api.delete(`/tasks/${id}`),
}

export const resourceSummaryApi = {
  getSummary: () => api.get('/resource-summary'),
  getByEmployee: id => api.get(`/resource-summary/employee/${id}`),
  getMonths: () => api.get('/resource-summary/months'),
}

export const allocationHistoryApi = {
  getAll: () => api.get('/allocation-history'),
  getById: id => api.get(`/allocation-history/${id}`),
  create: data => api.post('/allocation-history', data),
  update: (id, data) => api.put(`/allocation-history/${id}`, data),
  delete: id => api.delete(`/allocation-history/${id}`),
}

export default api
