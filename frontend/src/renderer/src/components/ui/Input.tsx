import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export const Input: React.FC<InputProps> = ({ label, error, className = '', id, ...props }) => {
  const inputId = id || Math.random().toString(36).substring(2, 9)

  return (
    <div className="flex flex-col gap-1.5 w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono"
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`w-full bg-cyber-bg border ${
          error
            ? 'border-neon-pink focus:ring-neon-pink'
            : 'border-cyber-border focus:border-neon-green/60'
        } focus:ring-1 focus:ring-neon-green/40 rounded px-3 py-2 text-sm text-white placeholder-gray-600 outline-none transition-all duration-200 font-cyber ${className}`}
        {...props}
      />
      {error && (
        <span className="text-[10px] font-semibold text-neon-pink uppercase tracking-wide font-mono">
          {error}
        </span>
      )}
    </div>
  )
}
