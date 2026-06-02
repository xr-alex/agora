interface Props {
  role: 'pro' | 'con' | 'judge'
  content: string | null
  isLoading: boolean
}

const config = {
  pro: {
    label: 'For',
    bg: 'bg-green-50',
    border: 'border-green-200',
    header: 'bg-green-100 text-green-800',
  },
  con: {
    label: 'Against',
    bg: 'bg-red-50',
    border: 'border-red-200',
    header: 'bg-red-100 text-red-800',
  },
  judge: {
    label: 'Judge',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    header: 'bg-blue-100 text-blue-800',
  },
}

export default function AgentCard({ role, content, isLoading }: Props) {
  const c = config[role]

  return (
    <div className={`rounded-lg border ${c.border} ${c.bg} overflow-hidden`}>
      <div className={`px-4 py-2 text-sm font-semibold ${c.header}`}>
        {c.label}
      </div>
      <div className="px-4 py-4 min-h-[120px]">
        {isLoading ? (
          <div className="space-y-2 animate-pulse">
            <div className="h-3 bg-gray-200 rounded w-3/4" />
            <div className="h-3 bg-gray-200 rounded w-full" />
            <div className="h-3 bg-gray-200 rounded w-5/6" />
            <div className="h-3 bg-gray-200 rounded w-2/3" />
          </div>
        ) : content ? (
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{content}</p>
        ) : (
          <p className="text-sm text-gray-400 italic">Waiting...</p>
        )}
      </div>
    </div>
  )
}
