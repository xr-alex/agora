import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

interface Props {
  onDebateCreated: (debateId: string, question: string) => void
}

export default function DebateForm({ onDebateCreated }: Props) {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_URL}/debates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const { debate_id } = await res.json()
      onDebateCreated(debate_id, question.trim())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold text-gray-800 mb-1">Start a Debate</h2>
      <p className="text-sm text-gray-500 mb-6">
        Two AI agents will argue for and against your proposition in parallel, then a judge will evaluate both sides.
      </p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-1">
            Proposition
          </label>
          <input
            id="question"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Should I use TypeScript for my project?"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={loading}
          />
        </div>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="w-full py-3 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Starting debate…' : 'Start Debate'}
        </button>
      </form>
    </div>
  )
}
