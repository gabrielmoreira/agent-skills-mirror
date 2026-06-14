import { describe, expect, test } from 'vitest'

import { formatResultRows, formatSection, markdownTable } from '../scripts/output'

describe('session-reflect output helpers', () => {
  test('formats markdown tables safely', () => {
    expect(markdownTable([{ name: 'a|b', text: 'one\ntwo' }])).toBe(
      '| name | text |\n| --- | --- |\n| a\\|b | one two |'
    )
  })

  test('formats empty markdown tables', () => {
    expect(markdownTable([])).toBe('_No rows._')
  })

  test('prepares rows for console tables', () => {
    const [row] = formatResultRows([{ text: 'x'.repeat(130) }], 'table') as Array<{
      text: string
    }>
    expect(row).toBeDefined()
    expect(row!.text).toHaveLength(120)
    expect(row!.text.endsWith('…')).toBe(true)
  })

  test('formats sections by output mode', () => {
    expect(formatSection('Title', 'markdown')).toBe('\n## Title\n')
    expect(formatSection('Title', 'table')).toBe('\nTitle')
  })
})
