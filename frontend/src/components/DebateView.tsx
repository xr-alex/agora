import { useEffect, useState } from 'react'
import AgentCard from './AgentCard'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

type Role = 'pro' | 'con' | 'judge'
type Status = 'running' | 'completed' | 'failed'

interface Props {
  debateId: string
  question: string
  onReset: () => void
}

export default function DebateView({ debateId, question, onReset }: Props) {
  const [content, setContent] = useState<Record<Role, string>>({ pro: '', con: '', judge: '' })
  const [status, setStatus] = useState<Status>('running')

  useEffect(() => {
    const es = new EventSource(`${API_URL}/debates/${debateId}/stream`)

    es.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'token' || data.type === 'full_turn') {
        setContent((prev) => ({
          ...prev,
          [data.role]: prev[data.role as Role] + data.content,
        }))
      } else if (data.type === 'debate_done') {
        setStatus('completed')
        es.close()
      } else if (data.type === 'error') {
        setStatus('failed')
        es.close()
      }
    }

    es.onerror = () => {
      setStatus('failed')
      es.close()
    }

    return () => es.close()
  }, [debateId])

  const isRunning = status === 'running'

  const statusColors: Record<Status, string> = {
    running: 'bg-yellow-100 text-yellow-700',
    completed: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs text-gray-400 mb-1 uppercase tracking-wide">Proposition</p>
          <p className="text-gray-800 font-medium">{question}</p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${statusColors[status]}`}>
            {status}
          </span>
          <button onClick={onReset} className="text-sm text-gray-400 hover:text-gray-600 underline">
            New debate
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AgentCard role="pro" content={content.pro || null} isLoading={isRunning && !content.pro} />
        <AgentCard role="con" content={content.con || null} isLoading={isRunning && !content.con} />
      </div>

      <AgentCard role="judge" content={content.judge || null} isLoading={isRunning && !content.judge} />
    </div>
  )
}
