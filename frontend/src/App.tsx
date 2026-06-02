import { useState } from 'react'
import DebateForm from './components/DebateForm'
import DebateView from './components/DebateView'

interface ActiveDebate {
  id: string
  question: string
}

export default function App() {
  const [debate, setDebate] = useState<ActiveDebate | null>(null)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">Agora</h1>
        <p className="text-sm text-gray-400">Multi-agent debate engine</p>
      </header>
      <main className="max-w-4xl mx-auto px-6 py-10">
        {debate ? (
          <DebateView
            debateId={debate.id}
            question={debate.question}
            onReset={() => setDebate(null)}
          />
        ) : (
          <DebateForm
            onDebateCreated={(id, question) => setDebate({ id, question })}
          />
        )}
      </main>
    </div>
  )
}
