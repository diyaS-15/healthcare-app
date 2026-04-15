/**
 * Auth Store - Zustand State Management
 * Manages authentication state and user data
 */
import { create } from 'zustand'
import { auth, supabase } from '../lib/supabase'

export const useAuthStore = create((set, get) => ({
  // State
  user: null,
  session: null,
  loading: true,
  error: null,

  // Actions
  setUser: (user) => set({ user }),
  setSession: (session) => set({ session }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Auth Methods
  initialize: async () => {
    try {
      set({ loading: true })
      const session = await auth.getSession()
      
      if (session) {
        const user = await auth.getCurrentUser()
        set({ user, session, loading: false })
      } else {
        set({ user: null, session: null, loading: false })
      }
    } catch (error) {
      console.error('Auth initialization failed:', error)
      set({ error: error.message, loading: false })
    }
  },

  signup: async (email, password, fullName) => {
    try {
      set({ loading: true, error: null })
      
      // Signup via Supabase
      const data = await auth.signup(email, password, fullName)
      
      // Auto-login
      const loginData = await auth.login(email, password)
      set({ 
        session: loginData.session,
        user: loginData.user,
        loading: false 
      })
      
      return loginData.user
    } catch (error) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  login: async (email, password) => {
    try {
      set({ loading: true, error: null })
      const data = await auth.login(email, password)
      set({ 
        session: data.session,
        user: data.user,
        loading: false 
      })
      return data.user
    } catch (error) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  logout: async () => {
    try {
      set({ loading: true, error: null })
      await auth.logout()
      set({ user: null, session: null, loading: false })
    } catch (error) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  // Real-time subscription to auth changes
  subscribeToAuth: () => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (session) {
          set({ session, user: session.user })
        } else {
          set({ session: null, user: null })
        }
      }
    )
    
    return () => subscription.unsubscribe()
  },

  isAuthenticated: () => !!get().session,
}))
