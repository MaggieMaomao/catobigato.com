import { createContext, useContext, useEffect, useRef, useState } from 'react'
import keycloak from './keycloak'

interface AuthContextValue {
  isAuthenticated: boolean
  token: string | undefined
  username: string | undefined
  displayName: string | undefined
  avatar: string | undefined
  login: () => void
  register: () => void
  logout: () => void
}

function buildDisplayName(
  tokenParsed: Record<string, unknown> | undefined,
  username: string | undefined,
): string | undefined {
  const first = (tokenParsed?.['given_name'] as string | undefined)?.trim()
  const last = (tokenParsed?.['family_name'] as string | undefined)?.trim()
  const fullName = [first, last].filter(Boolean).join(' ')
  return fullName || username
}

function resolveAvatarUrl(raw: string | undefined): string | undefined {
  if (!raw) return undefined
  if (raw.startsWith('data:')) return raw
  if (raw.startsWith('http://') || raw.startsWith('https://')) return raw
  const base = (keycloak.authServerUrl ?? '').replace(/\/+$/, '')
  return base ? `${base}${raw.startsWith('/') ? '' : '/'}${raw}` : undefined
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(keycloak.authenticated ?? false)
  const [token, setToken] = useState<string | undefined>(keycloak.token)
  const [username, setUsername] = useState<string | undefined>(
    keycloak.tokenParsed?.['preferred_username'] as string | undefined,
  )
  const [displayName, setDisplayName] = useState<string | undefined>(() =>
    buildDisplayName(
      keycloak.tokenParsed as Record<string, unknown> | undefined,
      keycloak.tokenParsed?.['preferred_username'] as string | undefined,
    ),
  )
  const [avatar, setAvatar] = useState<string | undefined>(
    resolveAvatarUrl(keycloak.tokenParsed?.['picture'] as string | undefined),
  )
  const refreshTimer = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!keycloak.authenticated) return

    // Proactive token refresh every 60 s, refreshing when < 30 s remaining
    refreshTimer.current = setInterval(async () => {
      try {
        const refreshed = await keycloak.updateToken(30)
        if (refreshed) {
          const newUsername = keycloak.tokenParsed?.['preferred_username'] as string | undefined
          setToken(keycloak.token)
          setUsername(newUsername)
          setDisplayName(buildDisplayName(keycloak.tokenParsed as Record<string, unknown> | undefined, newUsername))
          setAvatar(resolveAvatarUrl(keycloak.tokenParsed?.['picture'] as string | undefined))
        }
      } catch {
        // Refresh failed — clear state, user must re-login
        setIsAuthenticated(false)
        setToken(undefined)
        setUsername(undefined)
        setDisplayName(undefined)
        setAvatar(undefined)
        if (refreshTimer.current) clearInterval(refreshTimer.current)
      }
    }, 60_000)

    return () => {
      if (refreshTimer.current) clearInterval(refreshTimer.current)
    }
  }, [])

  const login = () => keycloak.login({ redirectUri: window.location.origin })
  const register = () => keycloak.register({ redirectUri: window.location.origin })
  const logout = () => keycloak.logout({ redirectUri: window.location.origin })

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, token, username, displayName, avatar, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
