export type Json = Record<string, unknown>
export type OutputFormat = 'table' | 'json' | 'markdown'

export function formatResultRows(resultRows: Json[], format: OutputFormat): Json[] | string {
  if (format === 'json') return JSON.stringify(resultRows, null, 2)
  if (format === 'markdown') return markdownTable(resultRows)
  return resultRows.map((row) =>
    Object.fromEntries(Object.entries(row).map(([key, value]) => [key, truncate(value)]))
  )
}

export function formatSection(title: string, format: OutputFormat): string {
  return format === 'markdown' ? `\n## ${title}\n` : `\n${title}`
}

export function markdownTable(resultRows: Json[]) {
  if (resultRows.length === 0) return '_No rows._'
  const headers = Object.keys(resultRows[0]!)
  const escape = (value: unknown) =>
    String(truncate(value)).replace(/\|/g, '\\|').replace(/\n/g, ' ')
  return [
    `| ${headers.map(escape).join(' | ')} |`,
    `| ${headers.map(() => '---').join(' | ')} |`,
    ...resultRows.map((row) => `| ${headers.map((header) => escape(row[header])).join(' | ')} |`)
  ].join('\n')
}

export function truncate(value: unknown) {
  if (typeof value === 'string' && value.length > 120) return ellipsize(value, 120)
  return value
}

export function ellipsize(value: string, maxChars: number) {
  if (value.length <= maxChars) return value
  return `${value.slice(0, maxChars - 1)}…`
}
