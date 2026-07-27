import React, { useState } from 'react'

interface TooltipProps {
  content: string
  children: React.ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
}

export const Tooltip: React.FC<TooltipProps> = ({ content, children, position = 'top' }) => {
  const [visible, setVisible] = useState(false)

  const positions = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2'
  }

  const arrows = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-cyber-border border-x-transparent border-b-transparent',
    bottom:
      'bottom-full left-1/2 -translate-x-1/2 border-b-cyber-border border-x-transparent border-t-transparent',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-cyber-border border-y-transparent border-r-transparent',
    right:
      'right-full top-1/2 -translate-y-1/2 border-r-cyber-border border-y-transparent border-l-transparent'
  }

  return (
    <div
      className="relative flex items-center w-max"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && (
        <div
          className={`absolute z-50 px-2.5 py-1.5 text-[10px] font-mono font-semibold uppercase tracking-wider text-white bg-cyber-panel border border-cyber-border rounded shadow-lg pointer-events-none whitespace-nowrap animate-fade-in ${positions[position]}`}
        >
          {content}
          <div className={`absolute border-4 ${arrows[position]}`} />
        </div>
      )}
    </div>
  )
}
