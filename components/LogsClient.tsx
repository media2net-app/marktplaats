'use client'

import { useState, useEffect, useRef } from 'react'

interface LogEntry {
  timestamp: string
  message: string
  level?: string
}

export default function LogsClient() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [services, setServices] = useState<any[]>([])
  const logsEndRef = useRef<HTMLDivElement>(null)

  const fetchServices = async () => {
    try {
      const response = await fetch('/api/railway/services')
      if (response.ok) {
        const data = await response.json()
        setServices(data.services || [])
      }
    } catch (err) {
      // Ignore errors
    }
  }

  const fetchLogs = async () => {
    try {
      setIsRefreshing(true)
      const response = await fetch('/api/railway/logs?limit=200')
      
      if (!response.ok) {
        const data = await response.json().catch(() => ({ error: `HTTP ${response.status}` }))
        const errorMsg = data.error || data.details || `HTTP ${response.status}: ${response.statusText}`
        const error = new Error(errorMsg) as any
        error.details = data.details
        error.debug = data.debug
        error.hint = data.hint
        error.missing = data.missing
        throw error
      }

      const data = await response.json()
      setLogs(data.logs || [])
      setError(null)
    } catch (err: any) {
      // Try to get error details from response if available
      let errorMsg = 'Failed to load logs'
      let errorDetails = null
      
      if (err.message) {
        errorMsg = err.message
      }
      
      // If it's a network error, provide more context
      if (err.message?.includes('fetch') || err.name === 'TypeError') {
        errorMsg = 'Network error: Could not connect to server'
        errorDetails = 'Check if the server is running and your internet connection is working.'
      } else if (err.hint) {
        errorDetails = err.hint
      } else if (err.details) {
        errorDetails = err.details
      }
      
      // Show debug info if available
      if (err.debug) {
        console.error('Railway API Debug Info:', err.debug)
        if (err.debug.hint) {
          errorDetails = err.debug.hint
        }
      }
      
      // Show missing variables if available
      if (err.missing && err.missing.length > 0) {
        errorMsg = `Missing environment variables: ${err.missing.join(', ')}`
        errorDetails = 'Please set these in Vercel: Settings → Environment Variables → Add'
      }
      
      setError(errorMsg + (errorDetails ? `\n\n${errorDetails}` : ''))
      console.error('Error fetching logs:', {
        message: err.message,
        details: err.details,
        debug: err.debug,
        hint: err.hint,
        missing: err.missing,
        status: err.status,
        type: err.type,
        name: err.name,
        fullError: err,
      })
    } finally {
      setLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    fetchLogs()
    fetchServices()
  }, [])

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchLogs()
      }, 5000) // Refresh every 5 seconds

      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs])

  const getLogLevelColor = (level?: string) => {
    switch (level?.toLowerCase()) {
      case 'error':
      case 'err':
        return 'text-red-600'
      case 'warn':
      case 'warning':
        return 'text-yellow-600'
      case 'info':
      case 'inf':
        return 'text-blue-600'
      default:
        return 'text-gray-700'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleString('nl-NL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })
    } catch {
      return timestamp
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Railway Logs</h2>
          <p className="text-sm sm:text-base text-gray-600 mt-1">Real-time logs van de Marktplaats worker</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg font-medium text-sm ${
              autoRefresh
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {autoRefresh ? '🔄 Auto-refresh Aan' : '⏸️ Auto-refresh Uit'}
          </button>
          <button
            onClick={fetchLogs}
            disabled={isRefreshing}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium text-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRefreshing ? 'Verversen...' : '🔄 Verversen'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-red-800 text-sm whitespace-pre-line">
            <strong>❌ Error:</strong>
            <div className="mt-2 font-mono text-xs bg-red-100 p-2 rounded">
              {error}
            </div>
          </div>
          {error.includes('not configured') && (
            <div className="mt-2 text-red-700 text-xs space-y-2">
              <p>Configureer de volgende environment variables in Vercel:</p>
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li><code>RAILWAY_API_TOKEN</code></li>
                <li><code>RAILWAY_PROJECT_ID</code></li>
                <li><code>RAILWAY_SERVICE_ID</code></li>
              </ul>
              {services.length > 0 && (
                <div className="mt-3 pt-3 border-t border-red-200">
                  <p className="font-semibold mb-2">Gevonden services in je project:</p>
                  <div className="space-y-1">
                    {services.map((service) => (
                      <div key={service.id} className="bg-white p-2 rounded border border-red-200">
                        <p className="font-medium text-gray-900">{service.name}</p>
                        <p className="text-xs text-gray-600 font-mono break-all">Service ID: {service.id}</p>
                        <p className="text-xs text-gray-500 mt-1">Kopieer deze Service ID en voeg toe als RAILWAY_SERVICE_ID in Vercel</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
            <span className="text-sm text-gray-600">
              {loading ? 'Laden...' : `${logs.length} log entries`}
            </span>
          </div>
          {autoRefresh && (
            <span className="text-xs text-gray-500">Auto-refresh elke 5 seconden</span>
          )}
        </div>
        
        <div className="h-[600px] overflow-y-auto bg-gray-900 text-gray-100 font-mono text-sm p-4">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-400">Logs laden...</div>
            </div>
          ) : logs.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-400">Geen logs gevonden</div>
            </div>
          ) : (
            <div className="space-y-1">
              {logs.map((log, index) => (
                <div key={index} className="flex gap-3 hover:bg-gray-800 px-2 py-1 rounded">
                  <span className="text-gray-500 text-xs whitespace-nowrap flex-shrink-0">
                    {formatTimestamp(log.timestamp)}
                  </span>
                  <span className={`flex-shrink-0 w-12 ${getLogLevelColor(log.level)}`}>
                    [{log.level?.toUpperCase() || 'INFO'}]
                  </span>
                  <span className="text-gray-300 flex-1 break-words">
                    {log.message}
                  </span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          )}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>💡 Tip:</strong> Logs worden automatisch ververst elke 5 seconden wanneer auto-refresh aan staat.
          Je kunt ook handmatig verversen met de knop hierboven.
        </p>
      </div>
    </div>
  )
}

