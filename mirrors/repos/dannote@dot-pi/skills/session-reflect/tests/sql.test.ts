import { describe, expect, test } from 'vitest'

import { PRESETS, interventionCandidatesSql, sqlString } from '../scripts/sql'

describe('session-reflect SQL helpers', () => {
  test('escapes SQL strings', () => {
    expect(sqlString("user's text")).toBe("'user''s text'")
  })

  test('exports named presets', () => {
    expect(PRESETS.overview?.sql).toContain('from sessions')
    expect(PRESETS.tools?.sql).toContain('from tool_calls')
  })

  test('builds intervention candidate filters', () => {
    const sql = interventionCandidatesSql({
      limit: 5,
      maxLen: 1000,
      minScore: 2,
      sort: 'recent',
      signals: ['quality_disgust'],
      project: 'dot-pi',
      since: '2026-01-01',
      until: '2026-02-01',
      pasted: 'exclude'
    })

    expect(sql).toContain('quality_disgust = true')
    expect(sql).toContain("project_key ilike '%dot-pi%'")
    expect(sql).toContain("timestamp >= '2026-01-01'")
    expect(sql).toContain('paste_score < 3')
    expect(sql).toContain('order by timestamp desc, score desc')
  })
})
