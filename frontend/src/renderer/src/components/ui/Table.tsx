import React from 'react'

interface TableProps extends React.TableHTMLAttributes<HTMLTableElement> {
  headers: string[]
}

export const Table: React.FC<TableProps> = ({ headers, children, className = '', ...props }) => {
  return (
    <div className="w-full overflow-x-auto border border-cyber-border rounded-lg bg-cyber-panel/40">
      <table className={`w-full text-left border-collapse text-sm ${className}`} {...props}>
        <thead>
          <tr className="border-b border-cyber-border bg-cyber-bg/60 select-none">
            {headers.map((header, index) => (
              <th
                key={index}
                className="py-3.5 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider font-mono"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-cyber-border/40">{children}</tbody>
      </table>
    </div>
  )
}

export const TableRow: React.FC<React.HTMLAttributes<HTMLTableRowElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <tr
    className={`hover:bg-cyber-surface/30 transition-colors duration-150 group ${className}`}
    {...props}
  >
    {children}
  </tr>
)

export const TableCell: React.FC<React.TdHTMLAttributes<HTMLTableCellElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <td className={`py-3 px-4 font-cyber text-gray-300 ${className}`} {...props}>
    {children}
  </td>
)
