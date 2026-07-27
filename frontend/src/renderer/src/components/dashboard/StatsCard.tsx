import React from 'react'
import { Card, CardContent } from '../ui/Card'
import { LucideIcon } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  color?: 'green' | 'cyan' | 'pink'
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  description,
  icon: Icon,
  color = 'green'
}) => {
  const iconColors = {
    green: 'text-neon-green bg-neon-green/10 border-neon-green/30',
    cyan: 'text-neon-cyan bg-neon-cyan/10 border-neon-cyan/30',
    pink: 'text-neon-pink bg-neon-pink/10 border-neon-pink/30'
  }

  return (
    <Card glowColor={color} className="cyber-panel-interactive">
      <CardContent className="flex items-center justify-between">
        <div className="space-y-1">
          <span className="text-[10px] uppercase font-mono font-bold tracking-wider text-gray-500 block">
            {title}
          </span>
          <span className="text-2xl font-bold font-cyber text-white block">{value}</span>
          {description && (
            <span className="text-[10px] font-mono text-gray-400 block pt-0.5">{description}</span>
          )}
        </div>
        <div
          className={`p-3 rounded-lg border flex items-center justify-center shrink-0 ${iconColors[color]}`}
        >
          <Icon className="w-6 h-6" />
        </div>
      </CardContent>
    </Card>
  )
}
