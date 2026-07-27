import React from 'react'

interface ProgressBarProps {
  value: number // 0 to 100
  color?: 'green' | 'cyan' | 'pink'
  showText?: boolean
  size?: 'sm' | 'md'
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  color = 'green',
  showText = false,
  size = 'md'
}) => {
  const percentage = Math.max(0, Math.min(100, value))

  const colors = {
    green: 'bg-neon-green shadow-[0_0_8px_rgba(57,255,20,0.5)]',
    cyan: 'bg-neon-cyan shadow-[0_0_8px_rgba(0,243,255,0.5)]',
    pink: 'bg-neon-pink shadow-[0_0_8px_rgba(255,0,85,0.5)]'
  }

  const sizes = {
    sm: 'h-1.5',
    md: 'h-3'
  }

  return (
    <div className="w-full flex items-center gap-3 select-none">
      <div
        className={`flex-1 bg-cyber-bg border border-cyber-border rounded-full overflow-hidden ${sizes[size]}`}
      >
        <div
          className={`h-full rounded-full transition-all duration-300 ease-out ${colors[color]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showText && (
        <span className="text-xs font-mono font-bold text-white shrink-0 min-w-[2.5rem] text-right">
          {Math.round(percentage)}%
        </span>
      )}
    </div>
  )
}
