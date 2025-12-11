'use client'

import { useState, useEffect } from 'react'

interface LogEntry {
  id: string
  message: string
  timestamp: string
  level?: string
}

interface LogsClientProps {}

export default function LogsClient({}: LogsClientProps) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(5) // seconds

  const fetchLogs = async () => {
    try {
      setError(null)
      const response = await fetch('/api/railway/logs?limit=200')
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || `Failed to fetch logs: ${response.status}`)
      }

      setLogs(data.logs || [])
    } catch (err: any) {
      setError(err.message || 'Failed to fetch logs')
      console.error('Error fetching logs:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()

    if (autoRefresh) {
      const interval = setInterval(fetchLogs, refreshInterval * 1000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval])

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

  const getLogLevelColor = (level?: string) => {
    if (!level) return 'text-gray-600'
    switch (level.toLowerCase()) {
      case 'error':
        return 'text-red-600'
      case 'warn':
      case 'warning':
        return 'text-yellow-600'
      case 'info':
        return 'text-blue-600'
      case 'debug':
        return 'text-gray-500'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Railway Logs</h1>
          <p className="text-gray-600 mt-1">Live logs van je Railway service</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Auto-refresh:</label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
          </div>
          {autoRefresh && (
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600">Interval:</label>
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                className="border border-gray-300 rounded px-2 py-1 text-sm"
              >
                <option value={3}>3s</option>
                <option value={5}>5s</option>
                <option value={10}>10s</option>
                <option value={30}>30s</option>
              </select>
            </div>
          )}
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            {loading ? 'Laden...' : 'Ververs'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800">Fout bij ophalen logs</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
              {error.includes('not configured') && (
                <div className="mt-3 text-sm text-red-600">
                  <p className="font-medium">Zorg dat de volgende environment variables zijn ingesteld in Vercel:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li><code>RAILWAY_API_TOKEN</code> - Je Railway API token</li>
                    <li><code>RAILWAY_SERVICE_ID</code> - Je Railway Service ID</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Logs ({logs.length})
            </h2>
            {autoRefresh && (
              <span className="text-xs text-gray-500 flex items-center gap-1">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                Auto-refresh actief ({refreshInterval}s)
              </span>
            )}
          </div>
        </div>
        
        <div className="overflow-x-auto">
          {loading && logs.length === 0 ? (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              <p className="mt-4 text-gray-600">Logs laden...</p>
            </div>
          ) : logs.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <p>Geen logs gevonden</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className="px-6 py-3 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-32 text-xs text-gray-500 font-mono">
                      {formatTimestamp(log.timestamp)}
                    </div>
                    {log.level && (
                      <div className={`flex-shrink-0 w-20 text-xs font-medium ${getLogLevelColor(log.level)}`}>
                        {log.level.toUpperCase()}
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <pre className="text-sm text-gray-900 whitespace-pre-wrap break-words font-mono">
                        {log.message}
                      </pre>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
