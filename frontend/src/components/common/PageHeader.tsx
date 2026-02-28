import type { ReactNode } from 'react'

interface PageHeaderProps {
  title: string
  subtitle: string
  eyebrow?: string
  actions?: ReactNode
  className?: string
}

export const PageHeader = ({ title, subtitle, eyebrow, actions, className = '' }: PageHeaderProps) => {
  return (
    <div className={`mb-8 flex flex-wrap items-end justify-between gap-6 ${className}`}>
      <div className="flex flex-col gap-1">
        {eyebrow ? (
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-brand-blue mb-1">{eyebrow}</p>
        ) : null}
        <h1 className="text-3xl font-extrabold tracking-tight text-brand-navy sm:text-4xl">{title}</h1>
        <p className="mt-1 max-w-3xl text-sm text-gray-500 sm:text-base leading-relaxed">{subtitle}</p>
      </div>
      {actions ? <div className="flex-shrink-0">{actions}</div> : null}
    </div>
  )
}
