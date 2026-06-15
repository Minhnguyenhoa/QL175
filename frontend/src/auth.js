const TOKEN_KEY = 'qt175_token'
const USER_KEY = 'qt175_user'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const getUser = () => {
  const u = localStorage.getItem(USER_KEY)
  return u ? JSON.parse(u) : null
}
export const setAuth = (token, user) => {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}
export const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}
export const isAuthenticated = () => !!getToken()
