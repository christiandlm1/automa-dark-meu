import React from 'react'

interface AutomaLogoProps {
  className?: string
  glow?: boolean
}

export const AutomaLogo: React.FC<AutomaLogoProps> = ({ className = 'w-12 h-12', glow = true }) => {
  return (
    <div className={`relative flex items-center justify-center ${className}`}>
      {/* Outer Glowing Ring */}
      {glow && (
        <div className="absolute inset-0 rounded-xl bg-neon-green/20 blur-md animate-pulse pointer-events-none" />
      )}

      {/* SVG Graphics */}
      <svg
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full drop-shadow-[0_0_8px_rgba(57,255,20,0.6)]"
      >
        {/* Hexagonal Outer Frame */}
        <polygon
          points="50,5 90,28 90,72 50,95 10,72 10,28"
          stroke="#39ff14"
          strokeWidth="3"
          strokeLinejoin="round"
          className="stroke-neon-green"
        />

        {/* Decorative inner cuts */}
        <path
          d="M 25 35 L 50 20 L 75 35"
          stroke="#00f3ff"
          strokeWidth="2"
          strokeLinecap="round"
          className="stroke-neon-cyan"
        />
        <path
          d="M 25 65 L 50 80 L 75 65"
          stroke="#00f3ff"
          strokeWidth="2"
          strokeLinecap="round"
          className="stroke-neon-cyan"
        />

        {/* The 'A' letter stylized like a media controller/play symbol */}
        <path
          d="M 35 70 L 50 30 L 65 70"
          stroke="#39ff14"
          strokeWidth="6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path d="M 40 55 L 60 55" stroke="#39ff14" strokeWidth="4" strokeLinecap="round" />

        {/* Cyberpunk Dots/Nodes */}
        <circle cx="50" cy="30" r="3" fill="#ff0055" />
        <circle cx="35" cy="70" r="3" fill="#ff0055" />
        <circle cx="65" cy="70" r="3" fill="#ff0055" />
      </svg>
    </div>
  )
}
