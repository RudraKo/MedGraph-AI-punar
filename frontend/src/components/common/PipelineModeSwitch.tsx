interface PipelineModeSwitchProps {
  mode: 'sync' | 'queued'
  onChange: (mode: 'sync' | 'queued') => void
}

export const PipelineModeSwitch = ({ mode, onChange }: PipelineModeSwitchProps) => {
  return (
    <div className="rounded-xl border border-surface-border bg-surface-muted p-1 inline-flex w-full">
      <div className="grid grid-cols-2 gap-1 w-full">
        <button
          type="button"
          onClick={() => onChange('sync')}
          className={`rounded-lg px-4 py-2.5 text-xs font-bold uppercase tracking-wider transition-all sm:text-sm ${mode === 'sync' ? 'bg-white text-brand-navy shadow-sm border border-surface-border' : 'text-gray-500 hover:text-brand-navy hover:bg-white/50 border border-transparent'
            }`}
        >
          Synchronous API
        </button>
        <button
          type="button"
          onClick={() => onChange('queued')}
          className={`rounded-lg px-4 py-2.5 text-xs font-bold uppercase tracking-wider transition-all sm:text-sm ${mode === 'queued' ? 'bg-white text-brand-navy shadow-sm border border-surface-border' : 'text-gray-500 hover:text-brand-navy hover:bg-white/50 border border-transparent'
            }`}
        >
          Queued Workers
        </button>
      </div>
    </div>
  )
}
