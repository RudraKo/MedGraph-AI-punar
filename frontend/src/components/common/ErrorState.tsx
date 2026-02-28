interface ErrorStateProps {
  message: string
}

export const ErrorState = ({ message }: ErrorStateProps) => {
  return (
    <div className="glass-card border-rose-200 bg-rose-50/70">
      <p className="text-sm font-semibold text-rose-700">Request failed</p>
      <p className="mt-1 text-sm text-rose-600">{message}</p>
    </div>
  )
}
