interface LoadingStateProps {
  label?: string
}

export const LoadingState = ({ label = 'Loading clinical data...' }: LoadingStateProps) => {
  return (
    <div className="bg-surface-light border border-brand-blue/20 rounded-xl p-4 shadow-card flex items-center gap-4 animate-pulse-slow">
      <div className="relative flex h-6 w-6">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-blue opacity-20" />
        <span className="relative inline-flex h-6 w-6 rounded-full bg-brand-blue/10 border-2 border-brand-blue border-t-transparent animate-spin" />
      </div>
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-brand-blue mb-0.5">AI Processing</p>
        <p className="text-sm font-medium text-brand-navy">{label}</p>
      </div>
    </div>
  )
}
