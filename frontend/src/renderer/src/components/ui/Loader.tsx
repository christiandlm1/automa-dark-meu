import React from 'react'

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg'
  color?: 'green' | 'cyan' | 'pink'
  text?: string
}

export const Loader: React.FC<LoaderProps> = ({ size = 'md', color = 'green', text }) => {
  const sizes = {
    sm: 'w-6 h-6 border-2',
    md: 'w-10 h-10 border-3',
    lg: 'w-16 h-16 border-4'
  }

  const colors = {
    green:
      'border-t-neon-green border-r-neon-green/20 border-b-neon-green/20 border-l-neon-green/20',
    cyan: 'border-t-neon-cyan border-r-neon-cyan/20 border-b-neon-cyan/20 border-l-neon-cyan/20',
    pink: 'border-t-neon-pink border-r-neon-pink/20 border-b-neon-pink/20 border-l-neon-pink/20'
  }

  return (
    <div className="flex flex-col items-center justify-center gap-3 p-6 select-none">
      <div className={`animate-spin rounded-full ${sizes[size]} ${colors[color]} border-solid`} />
      {text && (
        <span className="text-xs font-mono font-bold tracking-widest text-gray-400 uppercase animate-pulse">
          {text}
        </span>
      )}
    </div>
  )
}
