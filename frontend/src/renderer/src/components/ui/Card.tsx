import React from 'react'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean
  glowColor?: 'green' | 'cyan' | 'pink' | 'none'
}

export const Card: React.FC<CardProps> = ({
  children,
  hoverable = false,
  glowColor = 'none',
  className = '',
  ...props
}) => {
  const baseStyle = 'cyber-panel rounded-lg p-6 overflow-hidden relative'

  const glowStyles = {
    green: 'border-l-4 border-l-neon-green hover:shadow-[0_0_15px_rgba(57,255,20,0.1)]',
    cyan: 'border-l-4 border-l-neon-cyan hover:shadow-[0_0_15px_rgba(0,243,255,0.1)]',
    pink: 'border-l-4 border-l-neon-pink hover:shadow-[0_0_15px_rgba(255,0,85,0.1)]',
    none: ''
  }

  const hoverStyle = hoverable
    ? 'hover:border-gray-700 hover:-translate-y-0.5 transition-all duration-300 ease-in-out cursor-pointer'
    : ''

  return (
    <div className={`${baseStyle} ${glowStyles[glowColor]} ${hoverStyle} ${className}`} {...props}>
      {children}
    </div>
  )
}

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <div
    className={`mb-4 pb-4 border-b border-cyber-border flex items-center justify-between ${className}`}
    {...props}
  >
    {children}
  </div>
)

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <h3
    className={`text-base font-bold text-white tracking-wider font-cyber ${className}`}
    {...props}
  >
    {children}
  </h3>
)

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <div className={`${className}`} {...props}>
    {children}
  </div>
)
