import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/apiClient'

export const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('access_token'))

  useEffect(() => {
    if (token) {
      // Verify token and fetch user
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data.user)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      const { access_token, user: userData } = response.data
      
      console.log('[AuthContext] Login success, storing token')
      localStorage.setItem('access_token', access_token)
      setToken(access_token)
      setUser(userData)
      
      return { success: true, user: userData }
    } catch (error) {
      console.error('[AuthContext] Login failed:', error.response?.data)
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed'
      }
    }
  }

  const signup = async (userData) => {
    try {
      // Supporter deux formats d'appel:
      // signup({ email, password, username }) ou signup(username, email, password)
      let payload = userData;
      if (typeof userData === 'string') {
        // Format: signup(username, email, password)
        const [username, email, password] = arguments;
        payload = { username, email, password };
      }
      
      const response = await api.post('/auth/register', payload)
      const { access_token, user: newUser } = response.data
      
      console.log('[AuthContext] Signup success, storing token')
      localStorage.setItem('access_token', access_token)
      setToken(access_token)
      setUser(newUser)
      
      return { success: true, user: newUser }
    } catch (error) {
      console.error('[AuthContext] Signup failed:', error.response?.data)
      return {
        success: false,
        error: error.response?.data?.error || 'Signup failed'
      }
    }
  }

  const logout = () => {
    console.log('[AuthContext] Logout, clearing token')
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  const updateUser = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const value = {
    user,
    loading,
    login,
    signup,
    register: signup, // Alias pour compatibilité
    logout,
    updateUser,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin' || user?.is_admin === true
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
