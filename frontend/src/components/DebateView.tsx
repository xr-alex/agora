import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import AgentCard from './AgentCard'

interface DebateTurn {
  id: string
  debate_id: string
  role: 'pro' | 'con' | 'judge'
  content: string
  created_at: string
}

interface Props {
  debateId: string
  question: string
  onReset: () => void
}

export default function DebateView({ debateId, question, onReset }: Props) {
  const [turns, setTurns] = useState<DebateTurn[]>([])
  const [status, setStatus] = useState<'running' | 'completed' | 'failed'>('running')

  useEffect(() => {
    // Load any turns that already exist (handles page refresh mid-debate)
    supabase
      .from('debate_turns')
      .select('*')
      .eq('debate_id', debateId)
      .order('created_at')
      .then(({ data }) => { if (data) setTurns(data as DebateTurn[]) })

    // Live: new turns arriving
    const turnsChannel = supabase
      .channel(`turns:${debateId}`)
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'debate_turns',
        filter: `debate_id=eq.${debateId}`,
      }, (payload) => {
        setTurns((prev) => [...prev, payload.new as DebateTurn])
      })
      .subscribe()

    // Live: debate status updates (running → completed/failed)
    const statusChannel = supabase
      .channel(`debate:${debateId}`)
      .on('postgres_changes', {
        event: 'UPDATE',
        schema: 'public',
        table: 'debates',
        filter: `id=eq.${debateId}`,
      }, (payload) => {
        setStatus(payload.new.status)
      })
      .subscribe()

    return () => {
      supabase.removeChannel(turnsChannel)
      supabase.removeChannel(statusChannel)
    }
  }, [debateId])

  const pro = turns.find((t) => t.role === 'pro') ?? null
  const con = turns.find((t) => t.role === 'con') ?? null
  const judge = turns.find((t) => t.role === 'judge') ?? null

  const statusColors = {
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
        <AgentCard role="pro" content={pro?.content ?? null} isLoading={!pro && status === 'running'} />
        <AgentCard role="con" content={con?.content ?? null} isLoading={!con && status === 'running'} />
      </div>

      <AgentCard role="judge" content={judge?.content ?? null} isLoading={!judge && status === 'running'} />
    </div>
  )
}
