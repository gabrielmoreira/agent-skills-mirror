import { queryExecutionClient } from '@dynatrace-sdk/client-query';

// ── Suppressed DQL Warning Patterns ──────────────────────────────
const SUPPRESSED_WARNING_PATTERNS = [
  /The expression [`'"]"" == ""[`'"] is always true/,
  /The filter condition evaluates to a constant value/,
  /^SCAN_LIMIT_GBYTES$/,
  /Your result has been limited to \d+/,
];

function extractQueryWarnings(resultData) {
  const notifications = resultData?.metadata?.grail?.notifications;
  if (!Array.isArray(notifications) || notifications.length === 0) return [];

  return notifications
    .filter(n => (n.severity === 'WARNING' || n.severity === 'WARN') && n.message)
    .filter(n => !SUPPRESSED_WARNING_PATTERNS.some(pattern =>
      pattern.test(n.message) || pattern.test(n.notificationType || '')
    ))
    .map(n => n.message);
}

async function executeQuery(query, maxRecords = 100, pastMinutes = 7 * 24 * 60) {
  const now = new Date();
  const timeframeStart = new Date(now.getTime() - pastMinutes * 60 * 1000);

  const execution = await queryExecutionClient.queryExecute({
    body: {
      query,
      maxResultRecords: maxRecords,
      defaultTimeframeStart: timeframeStart.toISOString(),
      defaultTimeframeEnd: now.toISOString(),
    }
  });

  const requestToken = execution.requestToken;

  while (true) {
    const result = await queryExecutionClient.queryPoll({ requestToken });

    if (result.state === 'SUCCEEDED') {
      return { success: true, data: result.result, warnings: extractQueryWarnings(result.result) };
    } else if (result.state === 'FAILED') {
      return { success: false, error: 'Query failed', details: result };
    }

    await new Promise(resolve => setTimeout(resolve, 500));
  }
}

// ── Visualization Type Requirements ──────────────────────────────
// Notebook-available visualizations only (no maps, heatmap, scatterplot, meterBar, gauge).
const VISUALIZATION_REQUIREMENTS = {
  lineChart: [
    { name: 'Time', types: ['timestamp', 'timeframe'], count: 'one' },
    { name: 'Interval', types: ['duration'], count: 'one', required: false, requiredWith: ['Values', 'numericArray'] },
    { name: 'Values', types: ['long', 'double', 'duration', 'numericArray'], count: 'oneOrMore' },
    { name: 'Names', types: 'any', count: 'oneOrMore', required: false },
  ],
  areaChart: [
    { name: 'Time', types: ['timestamp', 'timeframe'], count: 'one' },
    { name: 'Interval', types: ['duration'], count: 'one', required: false, requiredWith: ['Values', 'numericArray'] },
    { name: 'Values', types: ['long', 'double', 'duration', 'numericArray'], count: 'oneOrMore' },
    { name: 'Names', types: 'any', count: 'oneOrMore', required: false },
  ],
  barChart: [
    { name: 'Time', types: ['timestamp', 'timeframe'], count: 'one' },
    { name: 'Interval', types: ['duration'], count: 'one', required: false, requiredWith: ['Values', 'numericArray'] },
    { name: 'Values', types: ['long', 'double', 'duration', 'numericArray'], count: 'oneOrMore' },
    { name: 'Names', types: 'any', count: 'oneOrMore', required: false },
  ],
  bandChart: [
    { name: 'Time', types: ['timestamp', 'timeframe'], count: 'one' },
    { name: 'Interval', types: ['duration'], count: 'one', required: false, requiredWith: ['Values', 'numericArray'] },
    { name: 'Values', types: ['long', 'double', 'duration', 'numericArray'], count: 'oneOrMore' },
    { name: 'Names', types: 'any', count: 'oneOrMore', required: false },
    { name: 'Band min values', types: ['numericArray'], count: 'one' },
    { name: 'Band max values', types: ['numericArray'], count: 'one' },
  ],
  categoricalBarChart: [
    { name: 'Values', types: ['long', 'double', 'duration'], count: 'oneOrMore' },
    { name: 'Categories', types: 'any', count: 'oneOrMore' },
  ],
  pieChart: [
    { name: 'Values', types: ['long', 'double', 'duration'], count: 'oneOrMore' },
    { name: 'Categories', types: 'any', count: 'oneOrMore' },
  ],
  donutChart: [
    { name: 'Values', types: ['long', 'double', 'duration'], count: 'oneOrMore' },
    { name: 'Categories', types: 'any', count: 'oneOrMore' },
  ],
  singleValue: [
    { name: 'Single value', types: 'any', count: 'one' },
    { name: 'Sparkline', types: ['numericArray'], count: 'one', required: false },
  ],
  histogram: [
    { name: 'Range', types: ['range'], count: 'one' },
    { name: 'Values', types: ['long', 'double', 'duration'], count: 'one' },
    { name: 'Names', types: 'any', count: 'oneOrMore', required: false },
  ],
  honeycomb: [
    { name: 'Values', types: ['long', 'double', 'duration'], count: 'one' },
    { name: 'Names', types: 'any', count: 'oneOrMore', required: false },
  ],
};

function extractFieldTypes(resultData) {
  const fieldTypes = {};
  const typesArray = resultData?.types;

  if (!Array.isArray(typesArray) || typesArray.length === 0) return fieldTypes;

  const mappings = typesArray[0]?.mappings || {};

  for (const [field, descriptor] of Object.entries(mappings)) {
    if (!descriptor || !descriptor.type) continue;

    if (descriptor.type === 'array') {
      const nestedTypes = descriptor.types;
      if (Array.isArray(nestedTypes) && nestedTypes.length > 0) {
        const elementType = nestedTypes[0]?.mappings?.element?.type;
        if (elementType === 'long' || elementType === 'double') {
          fieldTypes[field] = 'numericArray';
        } else {
          fieldTypes[field] = 'array';
        }
      } else {
        fieldTypes[field] = 'array';
      }
    } else {
      fieldTypes[field] = descriptor.type;
    }
  }

  const records = resultData?.records;
  if (Array.isArray(records) && records.length > 0) {
    const firstRecord = records[0];
    for (const [field, value] of Object.entries(firstRecord || {})) {
      if (value && typeof value === 'object' && !Array.isArray(value)
          && 'start' in value && 'end' in value
          && !fieldTypes[field]) {
        fieldTypes[field] = 'range';
      }
    }
  }

  return fieldTypes;
}

function checkVisualizationCompatibility(visualization, resultData) {
  const requirements = VISUALIZATION_REQUIREMENTS[visualization];
  if (!requirements) return [];

  const fieldTypes = extractFieldTypes(resultData);
  const fieldEntries = Object.entries(fieldTypes);
  const availableStr = () => fieldEntries.map(([f, t]) => `${f} (${t})`).join(', ') || 'none';

  const unconditionalRequired = requirements.filter(s => !s.requiredWith && s.required !== false);
  const conditional = requirements.filter(s => s.requiredWith);
  const allSlots = [...unconditionalRequired, ...conditional];

  function candidates(slot, claimed) {
    return fieldEntries
      .filter(([f, t]) => !claimed.has(f) && (slot.types === 'any' || slot.types.includes(t)))
      .map(([f]) => f);
  }

  function solve(slots, idx, claimed, assignment) {
    if (idx >= slots.length) return assignment;
    const slot = slots[idx];

    if (slot.requiredWith) {
      const [targetName, targetType] = slot.requiredWith;
      if (fieldTypes[assignment[targetName]] !== targetType)
        return solve(slots, idx + 1, claimed, assignment);
    }

    for (const field of candidates(slot, claimed)) {
      const result = solve(slots, idx + 1, new Set([...claimed, field]),
                           { ...assignment, [slot.name]: field });
      if (result) return result;
    }
    return null;
  }

  if (solve(allSlots, 0, new Set(), {})) return [];

  const errors = [];

  for (const slot of unconditionalRequired) {
    if (candidates(slot, new Set()).length === 0) {
      const typeLabel = slot.types === 'any' ? 'any type' : slot.types.join(' | ');
      errors.push(
        `${slot.name}: requires a field of type [${typeLabel}], but none found in query result. Available fields: ${availableStr()}`
      );
    }
  }

  if (errors.length === 0 && conditional.length > 0 &&
      solve(unconditionalRequired, 0, new Set(), {})) {
    for (const slot of conditional) {
      if (candidates(slot, new Set()).every(f => !slot.types.includes(fieldTypes[f])) ||
          candidates(slot, new Set()).length === 0) {
        const typeLabel = slot.types === 'any' ? 'any type' : slot.types.join(' | ');
        const [targetName, targetType] = slot.requiredWith;
        errors.push(
          `${slot.name}: required when ${targetName} uses ${targetType}. Needs a field of type [${typeLabel}], but none found. Available fields: ${availableStr()}`
        );
      }
    }
  }

  if (errors.length === 0) {
    errors.push(
      `Field conflict: not enough distinct fields to satisfy all required slots (${allSlots.map(s => s.name).join(', ')}). Available fields: ${availableStr()}`
    );
  }

  return errors;
}

// ── Section Extraction ───────────────────────────────────────────

function extractSectionQueries(notebook) {
  const queries = [];
  const sections = notebook.content?.sections;
  if (!Array.isArray(sections)) return queries;

  for (const section of sections) {
    if (section.type === 'dql' && section.state?.input?.value) {
      queries.push({
        sectionId: section.id,
        title: section.title || `Section ${section.id}`,
        query: section.state.input.value,
        visualization: section.state?.visualization || 'table',
      });
    }
  }
  return queries;
}

// ── Section Validation ───────────────────────────────────────────

async function validateSection(sectionQuery) {
  const queryEvaluationSettings = [
    { maxRecords: 10, pastMinutes: 7 * 24 * 60 },
    { maxRecords: 100, pastMinutes: 7 * 24 * 60 },
    { maxRecords: 10000, pastMinutes: 30 },
  ];

  const baseResult = {
    sectionId: sectionQuery.sectionId,
    title: sectionQuery.title,
    visualization: sectionQuery.visualization,
    query: sectionQuery.query,
    visualizationErrors: [],
  };

  try {
    let selectedResult = null;

    for (const setting of queryEvaluationSettings) {
      const result = await executeQuery(sectionQuery.query, setting.maxRecords, setting.pastMinutes);

      const attemptResult = {
        ...baseResult,
        success: result.success,
        recordCount: result.success ? result.data?.records?.length || 0 : 0,
        error: result.success ? null : result.error,
        queryWarnings: result.warnings || [],
      };
      attemptResult.empty = attemptResult.success && attemptResult.recordCount === 0;

      if (result.success && result.data) {
        attemptResult.visualizationErrors = checkVisualizationCompatibility(
          sectionQuery.visualization, result.data
        );
      }

      selectedResult = attemptResult;

      if (!attemptResult.success) break;
      if (attemptResult.success && !attemptResult.empty && attemptResult.visualizationErrors.length === 0) break;
    }

    return selectedResult;
  } catch (error) {
    return { ...baseResult, success: false, recordCount: 0, empty: false, error: error.message };
  }
}

// ── Helpers ──────────────────────────────────────────────────────

function truncateForReport(value, maxLength = 200) {
  const text = String(value ?? '');
  return text.length > maxLength ? `${text.substring(0, maxLength)}…` : text;
}

// ── Main ─────────────────────────────────────────────────────────

export default async function(event) {
  // ── Step 1: Obtain notebook JSON ─────────────────────────────────
  let notebookJson = event?.notebook;
  const notebookId = event?.notebookId;

  if (!notebookJson && notebookId) {
    try {
      const response = await fetch(`/platform/document/v1/documents/${notebookId}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      notebookJson = await response.json();
    } catch (error) {
      return { error: `Failed to fetch notebook: ${notebookId}`, details: error.message };
    }
  }
  if (!notebookJson) {
    return {
      error: 'No notebook provided',
      usage: 'Pass either: {"notebookId": "notebook-id"} or {"notebook": {...}}'
    };
  }

  // ── Step 2: Schema validation ────────────────────────────────────
  const schemaErrors = [];
  if (!notebookJson.name) schemaErrors.push('Missing top-level "name"');
  if (!notebookJson.type) schemaErrors.push('Missing top-level "type"');
  if (!notebookJson.content) schemaErrors.push('Missing top-level "content"');

  if (notebookJson.content) {
    if (notebookJson.content.version === undefined) schemaErrors.push('Missing "content.version"');
    if (!Array.isArray(notebookJson.content.sections)) {
      schemaErrors.push('"content.sections" must be an array');
    } else if (notebookJson.content.sections.length === 0) {
      schemaErrors.push('"content.sections" is empty — notebook has no sections');
    } else {
      const seenIds = new Set();
      for (const [idx, section] of notebookJson.content.sections.entries()) {
        const label = section.id ? `"${section.id}"` : `index ${idx}`;
        if (!section.id) {
          schemaErrors.push(`Section ${label}: missing "id"`);
        } else if (seenIds.has(section.id)) {
          schemaErrors.push(`Section ${label}: duplicate id`);
        } else {
          seenIds.add(section.id);
        }
        if (!section.type) {
          schemaErrors.push(`Section ${label}: missing "type" (must be "markdown", "dql", or "function")`);
        } else if (!['markdown', 'dql', 'function'].includes(section.type)) {
          schemaErrors.push(`Section ${label}: invalid type "${section.type}" (must be "markdown", "dql", or "function")`);
        } else if (section.type === 'markdown') {
          if (section.markdown === undefined || section.markdown === null || section.markdown === '') {
            schemaErrors.push(`Section ${label}: markdown section missing "markdown" content`);
          }
        } else if (section.type === 'dql') {
          if (!section.state?.input?.value) {
            schemaErrors.push(`Section ${label}: DQL section missing query at "state.input.value"`);
          }
        }
      }
    }
  }

  if (schemaErrors.length > 0) {
    const lines = [];
    lines.push(`Notebook: ${notebookJson.name || 'Unknown'}`);
    lines.push('');
    lines.push('── Schema Errors ──────────────────────────');
    lines.push('  Required notebook structure:');
    lines.push('    Top-level: name, type, content');
    lines.push('    content:   version, sections (array)');
    lines.push('');
    for (const err of schemaErrors) {
      lines.push(`    ✗ ${err}`);
    }
    lines.push('');
    lines.push('');
    lines.push('══════════════════════════════════════════');
    lines.push('  ✗ VALIDATION FAILED');
    lines.push('  Fix the schema errors above before deployment');
    lines.push('══════════════════════════════════════════');
    return lines.join('\n');
  }

  // ── Step 3: Extract and validate DQL sections ────────────────────
  const sectionQueries = extractSectionQueries(notebookJson);
  const results = await Promise.all(
    sectionQueries.map(q => validateSection(q))
  );

  // ── Step 4: Collect diagnostics ──────────────────────────────────
  const dqlQueryWarnings = [];
  for (const r of results) {
    if (Array.isArray(r.queryWarnings)) {
      for (const msg of r.queryWarnings) {
        dqlQueryWarnings.push({ id: r.sectionId, label: r.title, message: msg });
      }
    }
  }

  const sectionOk = results.filter(r => r.success);
  const sectionFailed = results.filter(r => !r.success);
  const sectionEmpty = results.filter(r => r.empty);
  const sectionVizErrors = results.filter(r => r.success && r.visualizationErrors?.length > 0);

  const hasErrors = sectionFailed.length > 0 || sectionVizErrors.length > 0;
  const hasWarnings = dqlQueryWarnings.length > 0 || sectionEmpty.length > 0;

  // ── Step 5: Build report ─────────────────────────────────────────
  const lines = [];
  lines.push(`Notebook: ${notebookJson.name || 'Unknown'}`);
  lines.push('');

  // ── Warnings ──
  if (hasWarnings) {
    lines.push('── Warnings ─────────────────────────────────');
    lines.push('');

    if (sectionEmpty.length > 0) {
      lines.push('  Queries returning no data (0 records within the last 7 days):');
      lines.push('');
      for (const r of sectionEmpty) {
        lines.push(`    ⚠ [${r.sectionId}] ${r.title}`);
        lines.push(`      query: ${truncateForReport(r.query.trim().replace(/\s+/g, ' '))}`);
        lines.push('');
      }
    }

    if (dqlQueryWarnings.length > 0) {
      lines.push('  DQL query warnings (reported by the query engine):');
      lines.push('');
      for (const w of dqlQueryWarnings) {
        lines.push(`    ⚠ [${w.id}] ${w.label}`);
        lines.push(`      ${w.message}`);
        lines.push('');
      }
    }
  }

  // ── Errors ──
  if (hasErrors) {
    lines.push('── Errors ─────────────────────────────────');
    lines.push('');

    if (sectionFailed.length > 0) {
      lines.push('  Query errors:');
      lines.push('');
      for (const r of sectionFailed) {
        lines.push(`    ✗ [${r.sectionId}] ${r.title}`);
        lines.push(`      query: ${truncateForReport(r.query.trim().replace(/\s+/g, ' '))}`);
        if (r.error) {
          lines.push(`      error: ${r.error.replace(/\s+/g, ' ').substring(0, 120)}`);
        }
        lines.push('');
      }
    }

    if (sectionVizErrors.length > 0) {
      lines.push('  Visualization type errors (query result fields incompatible with visualization):');
      lines.push('');
      for (const r of sectionVizErrors) {
        lines.push(`    ✗ [${r.sectionId}] ${r.title}  (${r.visualization})`);
        for (const vizErr of r.visualizationErrors) {
          lines.push(`      → ${vizErr}`);
        }
        lines.push('');
      }
    }
  }

  // ── Sections Summary ──
  lines.push('── Sections ──────────────────────────────');
  lines.push(`  Total DQL: ${results.length}    Successful: ${sectionOk.length}    Failed: ${sectionFailed.length}${sectionEmpty.length > 0 ? `    Empty: ${sectionEmpty.length}` : ''}${sectionVizErrors.length > 0 ? `    Viz errors: ${sectionVizErrors.length}` : ''}`);
  lines.push('');
  for (const r of results) {
    const name = r.title || `Section ${r.sectionId}`;
    const truncatedName = name.length > 35 ? name.substring(0, 32) + '…' : name;
    const queryStatus = r.success ? '✓' : '✗';
    const dataStatus = r.success ? (r.empty ? '⚠' : '✓') : '-';
    const vizStatus = r.success ? (r.visualizationErrors?.length > 0 ? '✗' : '✓') : '-';
    const overall = !r.success || r.visualizationErrors?.length > 0 ? '✗' : r.empty ? '⚠' : '✓';
    lines.push(`  ${overall} ${truncatedName.padEnd(36)} query=${queryStatus}  data=${dataStatus}  viz=${vizStatus}`);
  }
  lines.push('');

  // ── Verdict ──
  lines.push('');
  if (hasErrors) {
    lines.push('══════════════════════════════════════════');
    lines.push('  ✗ VALIDATION FAILED');
    lines.push('  Fix all errors before deployment');
    lines.push('══════════════════════════════════════════');
  } else if (hasWarnings) {
    lines.push('══════════════════════════════════════════');
    lines.push('  ✓ VALIDATION SUCCEEDED (WITH WARNINGS)');
    lines.push('  Review warnings above before deployment');
    lines.push('══════════════════════════════════════════');
  } else {
    lines.push('══════════════════════════════════════════');
    lines.push('  ✓ VALIDATION SUCCEEDED');
    lines.push('  Notebook is ready for deployment');
    lines.push('══════════════════════════════════════════');
  }

  return lines.join('\n');
}
