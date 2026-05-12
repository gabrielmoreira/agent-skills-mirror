import { queryExecutionClient } from '@dynatrace-sdk/client-query';

// ── Helpers ──────────────────────────────────────────────────────────

// ── Suppressed DQL Warning Patterns ──────────────────────────────────
// Regex patterns for benign DQL warnings to suppress.
// Patterns can match either message text or notificationType.
const SUPPRESSED_WARNING_PATTERNS = [
  // Expected side effect of empty text-variable substitution.
  /The expression [`'"]"" == ""[`'"] is always true/,
  // Companion warning for the same pattern in `filter`.
  /The filter condition evaluates to a constant value/,
  // Suppress scan-limit warning by notificationType.
  /^SCAN_LIMIT_GBYTES$/,
  // Suppress limit-truncation warning.
  /Your result has been limited to \d+/,
];

/**
 * Extract warning messages from `result.metadata.grail.notifications[]`
 * and drop entries matching SUPPRESSED_WARNING_PATTERNS.
 *
 * @param {Object} resultData QueryResult from poll response
 * @returns {string[]} Non-suppressed warning messages
 */
function extractQueryWarnings(resultData) {
  const notifications = resultData?.metadata?.grail?.notifications;
  if (!Array.isArray(notifications) || notifications.length === 0) return [];

  return notifications
    // Keep warning-level notifications only.
    .filter(n => (n.severity === 'WARNING' || n.severity === 'WARN') && n.message)
    // Suppression can match message or notificationType.
    .filter(n => !SUPPRESSED_WARNING_PATTERNS.some(pattern => 
      pattern.test(n.message) || pattern.test(n.notificationType || '')
    ))
    .map(n => n.message);
}

/**
 * Executes a DQL query against the Dynatrace Grail data lakehouse using the
 * async query API (submit → poll loop).
 *
 * Flow:
 *   1. Submit the query via queryExecute → receives a requestToken
 *   2. Poll queryPoll every 500ms until state is SUCCEEDED or FAILED
 *      (no explicit timeout/cancel handling in this helper)
 *   3. Return { success, data, warnings } on success or { success, error } on failure
 *
 * A default timeframe of the last 7 days is always applied via
 * defaultTimeframeStart / defaultTimeframeEnd. If the query itself
 * contains an explicit timeframe (e.g. `from:`, `timeframe:`), the
 * query-level timeframe takes precedence per DQL API semantics.
 *
 * @param {string}  query      - The DQL query string (already fully substituted)
 * @param {number}  maxRecords - Cap on returned records (default 100; variable queries use 1000; tile queries use 10)
 * @param {number}  pastMinutes - Default timeframe length in minutes (default 7 days)
 * @returns {{ success: boolean, data?: object, warnings?: string[], error?: string }}
 */
async function executeQuery(query, maxRecords = 100, pastMinutes = 7 * 24 * 60) {
  // Build a default timeframe (end = now, start = now - pastMinutes).
  // The DQL API only uses these when the query itself has no explicit timeframe.
  const now = new Date();
  const timeframeStart = new Date(now.getTime() - pastMinutes * 60 * 1000);
  const defaultTimeframeEnd = now.toISOString();
  const defaultTimeframeStart = timeframeStart.toISOString();

  // Step 1: Submit the query – this is non-blocking and returns immediately
  // with a requestToken that we use to poll for results
  const execution = await queryExecutionClient.queryExecute({
    body: {
      query: query,
      maxResultRecords: maxRecords,
      defaultTimeframeStart,
      defaultTimeframeEnd,
    }
  });

  const requestToken = execution.requestToken;

  // Step 2: Poll loop – keep checking until the query completes or fails
  while (true) {
    const result = await queryExecutionClient.queryPoll({
      requestToken: requestToken
    });

    if (result.state === 'SUCCEEDED') {
      // Warnings are in result.result.metadata.grail.notifications[]
      // (confirmed via Grail API; each has severity, message, notificationType)
      const warnings = extractQueryWarnings(result.result);
      return { success: true, data: result.result, warnings };
    } else if (result.state === 'FAILED') {
      return { success: false, error: 'Query failed', details: result };
    }

    // Query still running – wait 500ms before next poll
    await new Promise(resolve => setTimeout(resolve, 500));
  }
}

// ── Variable Resolution ──────────────────────────────────────────────

/**
 * Returns synthetic values for the built-in Dynatrace timeframe variables.
 *
 * In the real dashboard UI these are supplied by the time picker. Since
 * this validator runs outside the UI, we fabricate a 2-hour window ending
 * at "now" so that queries referencing $dt_timeframe_from / $dt_timeframe_to
 * have valid ISO-8601 timestamps.
 *
 * @returns {{ dt_timeframe_from: string, dt_timeframe_to: string }}
 */
function getBuiltinVariables() {
  const now = new Date().toISOString();
  return {
    dt_timeframe_from: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    dt_timeframe_to: now
  };
}

/**
 * Scans a variable's `input` (DQL query string) for references to variables,
 * expressed as $VarName. This is used to determine dependency
 * order: a variable that references $Cluster must be resolved AFTER Cluster.
 *
 * Detection pattern: /\$([A-Za-z_][A-Za-z0-9_]*)/g
 *   - Matches a '$' followed by a valid identifier (letters, digits, underscores)
 *   - Example: "fetch ... | filter belongs_to == $Cluster" → ["Cluster"]
 *
 * Built-in timeframe variables ($dt_timeframe_from, $dt_timeframe_to) are
 * excluded because they are always pre-resolved and should not affect ordering.
 *
 * @param {string} variableInput - The DQL query string from a variable definition
 * @returns {string[]} - Array of variable keys that this input depends on
 */
function findVariableDependencies(variableInput) {
  // Match all $VarName patterns in the input string
  const matches = variableInput.match(/\$([A-Za-z_][A-Za-z0-9_]*)/g) || [];
  return [...new Set(matches
    .map(m => m.slice(1))                                  // strip the leading '$'
    .filter(name => !name.startsWith('dt_timeframe')) )];  // ignore built-in timeframe vars
}

/**
 * Topologically sorts variables by dependency and reports explicit dependency
 * errors. This guarantees layered resolution order for valid DAGs and produces
 * deterministic diagnostics for invalid graphs.
 *
 * Error types reported:
 *   - Unknown dependency: query references $Var that is not defined
 *   - Cyclic dependency:  one or more variables form a dependency loop
 *   - Cycle-blocked var:  variable depends (transitively) on a cyclic variable
 *   - Duplicate key:      same variable key appears more than once
 *
 * @param {Array} varDefs - Raw dashboard variable definitions
 * @returns {{ sorted: Array, blockedKeys: Set<string>, dependencyErrors: Array }}
 */
function topologicallySortVariables(varDefs) {
  const byKey = new Map();
  const keyOrder = new Map();
  const dependencyMap = new Map();   // key -> Set(dependencyKeys)
  const dependentsMap = new Map();   // key -> Set(keysThatDependOnKey)
  const blockedKeys = new Set();
  const dependencyErrors = [];

  // First pass: index variables by key and initialize graph containers.
  for (const variable of varDefs) {
    const key = variable?.key;
    if (!key) continue;

    if (byKey.has(key)) {
      blockedKeys.add(key);
      dependencyErrors.push({
        key,
        type: variable?.type || byKey.get(key)?.type || 'query',
        values: [],
        source: 'dependency-error',
        error: `Duplicate variable key "${key}" detected. Variable keys must be unique.`
      });
      continue;
    }

    byKey.set(key, variable);
    keyOrder.set(key, keyOrder.size);
    dependencyMap.set(key, new Set());
    dependentsMap.set(key, new Set());
  }

  // Second pass: extract query dependencies and detect unknown references.
  for (const [key, variable] of byKey.entries()) {
    if (blockedKeys.has(key)) continue;
    if (variable?.type !== 'query') continue;

    const deps = findVariableDependencies(variable.input || '');
    const unknownDeps = deps.filter(dep => !byKey.has(dep));

    if (unknownDeps.length > 0) {
      blockedKeys.add(key);
      dependencyErrors.push({
        key,
        type: variable.type,
        values: [],
        source: 'dependency-error',
        error: `Unknown variable dependency${unknownDeps.length > 1 ? 'ies' : ''}: ${unknownDeps.map(dep => `$${dep}`).join(', ')}`
      });
    }

    for (const dep of deps) {
      if (!byKey.has(dep)) continue;
      dependencyMap.get(key).add(dep);
      dependentsMap.get(dep).add(key);
    }
  }

  // Find cyclic variables in the subgraph that is not already blocked.
  const cycleCandidates = [...byKey.keys()].filter(key => !blockedKeys.has(key));
  const cycleCandidateSet = new Set(cycleCandidates);
  const visitState = new Map(); // 0/undefined = unvisited, 1 = visiting, 2 = visited
  const visitStack = [];
  const cycleKeys = new Set();

  const dfs = (key) => {
    visitState.set(key, 1);
    visitStack.push(key);

    for (const dep of dependencyMap.get(key) || []) {
      if (!cycleCandidateSet.has(dep)) continue;

      const depState = visitState.get(dep) || 0;
      if (depState === 0) {
        dfs(dep);
      } else if (depState === 1) {
        const cycleStart = visitStack.lastIndexOf(dep);
        for (let i = cycleStart; i < visitStack.length; i++) {
          cycleKeys.add(visitStack[i]);
        }
      }
    }

    visitStack.pop();
    visitState.set(key, 2);
  };

  for (const key of cycleCandidates) {
    if ((visitState.get(key) || 0) === 0) {
      dfs(key);
    }
  }

  if (cycleKeys.size > 0) {
    for (const key of cycleKeys) {
      blockedKeys.add(key);
      const cycleDeps = [...(dependencyMap.get(key) || [])].filter(dep => cycleKeys.has(dep));
      dependencyErrors.push({
        key,
        type: byKey.get(key)?.type || 'query',
        values: [],
        source: 'dependency-error',
        error: `Cyclic dependency detected involving $${key}${cycleDeps.length > 0 ? ` (depends on ${cycleDeps.map(dep => `$${dep}`).join(', ')})` : ''}`
      });
    }

    // Variables depending on cycles are blocked as well, with explicit errors.
    const cycleBlocked = new Set(cycleKeys);
    const queue = [...cycleKeys];

    while (queue.length > 0) {
      const current = queue.shift();
      for (const dependent of dependentsMap.get(current) || []) {
        if (!cycleCandidateSet.has(dependent)) continue;
        if (cycleBlocked.has(dependent)) continue;
        cycleBlocked.add(dependent);
        queue.push(dependent);
      }
    }

    for (const key of cycleBlocked) {
      if (cycleKeys.has(key)) continue;
      blockedKeys.add(key);
      const cycleDeps = [...(dependencyMap.get(key) || [])].filter(dep => cycleBlocked.has(dep));
      dependencyErrors.push({
        key,
        type: byKey.get(key)?.type || 'query',
        values: [],
        source: 'dependency-error',
        error: `Cannot resolve because it depends on variable(s) involved in a dependency cycle: ${cycleDeps.map(dep => `$${dep}`).join(', ')}`
      });
    }
  }

  // Kahn topological sort on variables that are not blocked.
  const sortableKeys = [...byKey.keys()].filter(key => !blockedKeys.has(key));
  const sortableKeySet = new Set(sortableKeys);
  const indegree = new Map();

  for (const key of sortableKeys) {
    const depCount = [...(dependencyMap.get(key) || [])].filter(dep => sortableKeySet.has(dep)).length;
    indegree.set(key, depCount);
  }

  const ready = sortableKeys
    .filter(key => indegree.get(key) === 0)
    .sort((a, b) => keyOrder.get(a) - keyOrder.get(b));

  const sortedKeys = [];
  while (ready.length > 0) {
    const current = ready.shift();
    sortedKeys.push(current);

    for (const dependent of dependentsMap.get(current) || []) {
      if (!sortableKeySet.has(dependent)) continue;

      indegree.set(dependent, indegree.get(dependent) - 1);
      if (indegree.get(dependent) === 0) {
        ready.push(dependent);
        ready.sort((a, b) => keyOrder.get(a) - keyOrder.get(b));
      }
    }
  }

  // Defensive fallback: if something still could not be sorted, report explicitly.
  if (sortedKeys.length !== sortableKeys.length) {
    const sortedKeySet = new Set(sortedKeys);
    const unresolved = sortableKeys.filter(key => !sortedKeySet.has(key));
    for (const key of unresolved) {
      blockedKeys.add(key);
      dependencyErrors.push({
        key,
        type: byKey.get(key)?.type || 'query',
        values: [],
        source: 'dependency-error',
        error: 'Unresolvable dependency chain detected while sorting variables.'
      });
    }
  }

  return {
    sorted: sortedKeys.map(key => byKey.get(key)),
    blockedKeys,
    dependencyErrors
  };
}

/**
 * Escapes regex metacharacters in a literal string so it can be embedded
 * safely in a RegExp pattern.
 *
 * @param {string} value - Raw literal value to escape
 * @returns {string} - Regex-safe literal string
 */
function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Applies the requested replacement strategy to a single variable value.
 *
 * Supported strategies:
 *   - default:     wrap in double quotes
 *   - noquote:     emit raw value as-is
 *   - backtick:    wrap in backticks
 *   - triplequote: wrap in triple quotes
 *
 * @param {*} value - Value to format for query substitution
 * @param {'default'|'noquote'|'backtick'|'triplequote'} [strategy='default']
 * @returns {string}
 */
function applyReplacementStrategy(value, strategy = 'default') {
  const asString = value == null ? '' : String(value);
  switch (strategy) {
    case 'noquote':
      return asString;
    case 'backtick':
      return `\`${asString}\``;
    case 'triplequote':
      return `"""${asString}"""`;
    case 'default':
    default:
      return `"${asString}"`;
  }
}

/**
 * Normalizes a variable defaultValue into a trimmed string array.
 * Accepts either a string (comma-separated) or an array.
 *
 * @param {string|string[]|undefined|null} defaultValue
 * @returns {string[]}
 */
function normalizeDefaultValues(defaultValue) {
  if (Array.isArray(defaultValue)) {
    return defaultValue
      .map(v => String(v).trim())
      .filter(Boolean);
  }
  if (typeof defaultValue === 'string') {
    return defaultValue
      .split(',')
      .map(v => v.trim())
      .filter(Boolean);
  }
  return [];
}

/**
 * Replaces variable placeholders ($VarName) in a DQL query string with their
 * resolved concrete values. Handles two query placeholder patterns, with
 * behavior determined by the resolved value type:
 *
 * ┌───────────────────┬──────────────────────┬──────────────────────────────────────────────┐
 * │ Pattern in query  │ Resolved value type  │ What gets substituted                       │
 * ├───────────────────┼──────────────────────┼──────────────────────────────────────────────┤
 * │ array($Var)       │ string[]             │ All values, each double-quoted, comma-sep.  │
 * │                   │                      │ e.g. "val1", "val2", "val3"                 │
 * ├───────────────────┼──────────────────────┼──────────────────────────────────────────────┤
 * │ $Var (bare)       │ string[]             │ ALL values, each double-quoted, comma-sep.  │
 * │                   │                      │ e.g. "val1", "val2", "val3"                 │
 * ├───────────────────┼──────────────────────┼──────────────────────────────────────────────┤
 * │ $Var (bare)       │ string               │ The string value, double-quoted             │
 * │                   │                      │ e.g. "some text"                            │
 * └───────────────────┴──────────────────────┴──────────────────────────────────────────────┘
 *
 * Substitution order matters for array values:
 *   1. FIRST: Replace array($Var) patterns
 *   2. THEN:  Replace bare $Var patterns
 *   This ordering prevents bare $Var from being replaced inside array($Var)
 *   before the array() pattern gets a chance to expand.
 *
 * Supported replacement suffixes:
 *   - $Var:noquote
 *   - $Var:backtick
 *   - $Var:triplequote
 *   - array($Var:noquote|backtick|triplequote)
 *
 * Empty arrays: Both patterns are replaced with "" (empty quoted string) to
 * keep the query syntactically valid even when no values are available.
 *
 * @param {string} query        - DQL query with $VarName placeholders
 * @param {Object} resolvedVars - Map of variable key → resolved value(s)
 *                                 Values are either string or string[]
 * @returns {string} - Query with all variables substituted
 */
function substituteVariables(query, resolvedVars) {
  let result = query;
  for (const [key, values] of Object.entries(resolvedVars)) {
    const escapedKey = escapeRegExp(key);

    if (Array.isArray(values)) {
      // ── Array value (from csv or query variables with multiple values) ──
      if (values.length > 0) {
        const expandArrayValues = (strategy = 'default') => values
          .map(v => applyReplacementStrategy(v, strategy))
          .join(', ');

        // IMPORTANT: Replace array($Var) FIRST, before bare $Var,
        // so that array($Var) gets expanded before bare replacement.
        result = result.replace(
          new RegExp(`array\\(\\$${escapedKey}(?::(noquote|backtick|triplequote))?\\)`, 'g'),
          (_match, strategy = 'default') => expandArrayValues(strategy)
        );
        result = result.replace(
          new RegExp(`\\$${escapedKey}(?::(noquote|backtick|triplequote))?(?![A-Za-z0-9_])`, 'g'),
          (_match, strategy = 'default') => expandArrayValues(strategy)
        );
      } else {
        // Empty array: replace with empty quoted string to avoid DQL syntax errors
        result = result.replace(
          new RegExp(`array\\(\\$${escapedKey}(?::(noquote|backtick|triplequote))?\\)`, 'g'),
          '""'
        );
        result = result.replace(
          new RegExp(`\\$${escapedKey}(?::(noquote|backtick|triplequote))?(?![A-Za-z0-9_])`, 'g'),
          '""'
        );
      }
    } else if (typeof values === 'string') {
      // ── String value (from text variables or built-in timeframe vars) ──
      result = result.replace(
        new RegExp(`\\$${escapedKey}(?::(noquote|backtick|triplequote))?(?![A-Za-z0-9_])`, 'g'),
        (_match, strategy = 'default') => applyReplacementStrategy(values, strategy)
      );
    }
  }
  return result;
}

/**
 * Resolves ALL dashboard variables in dependency order, producing a map of
 * key → concrete value(s) that can be substituted into tile queries.
 *
 * Overall flow:
 *   1. Seed the resolved map with built-in timeframe variables
 *   2. Sort user-defined variables by dependency order (variables with no
 *      dependencies are resolved first, so dependents can reference them)
 *   3. Iterate through sorted variables and resolve each by type:
 *      - csv:   Parse the comma-separated input or defaultValue
 *      - text:  Use the defaultValue string directly
 *      - query: Substitute already-resolved vars into the DQL input, execute
 *               the query, and extract values from the first result column
 *      - other: Flag as unknown type (error)
 *   4. Return the resolved map AND a diagnostic array for reporting
 *
 * Special handling:
 *   - Selection by `multiple` flag:
 *       - multiple: true  -> use ALL available values
 *       - multiple: false -> use defaultValue (if present), otherwise first available value
 *   - For csv variables, available values come from `input`
 *   - For query variables, available values come from query result rows
 *   - Query failures, missing query `input`, or empty query results resolve to
 *     defaultValue (single-select only) or [] if no default is available
 *
 * @param {Array} variables - The variables array from dashboard.content.variables
 * @returns {{ resolved: Object, variableResults: Array }}
 *   - resolved:        Map of variableKey → value (string) or values (string[])
 *   - variableResults: Diagnostic array with resolution details per variable
 */
async function resolveVariables(variables) {
  // Step 1: Seed with built-in timeframe variables so they are available
  // immediately for any variable or tile query that references them
  const resolved = { ...getBuiltinVariables() };
  const varDefs = variables || [];

  // Step 2: Topologically sort variables and collect explicit dependency errors.
  const { sorted, blockedKeys, dependencyErrors } = topologicallySortVariables(varDefs);

  // Diagnostic array – each entry records how a variable was resolved
  const variableResults = [...dependencyErrors];

  // Seed blocked variables with empty arrays so tile substitution does not leave
  // unresolved placeholders in downstream queries.
  for (const key of blockedKeys) {
    if (!(key in resolved)) {
      resolved[key] = [];
    }
  }

  // Step 3: Resolve each variable sequentially (order matters for dependencies)
  for (const variable of sorted) {
    const { key, type, input, defaultValue } = variable;

    if (type === 'csv') {
      // ── CSV Variable ──────────────────────────────────────────────
      // Selection is driven by `multiple`.
      // - multiple: true  -> all values from csv input
      // - multiple: false -> defaultValue (if present), otherwise first value
      const allValues = input
        ? input.split(',').map(v => v.trim()).filter(Boolean)
        : [];
      const defaultValues = normalizeDefaultValues(defaultValue);
      const selectedValues = variable.multiple === true
        ? allValues
        : (defaultValues.length > 0 ? [defaultValues[0]] : allValues.slice(0, 1));
      resolved[key] = selectedValues;
      variableResults.push({
        key,
        type,
        values: resolved[key],
        selectedValues,
        possibleValues: allValues,
        source: selectedValues.length === 0 ? 'csv-empty' : 'csv',
        selectionMode: variable.multiple === true ? 'multiple-all' : 'single-first'
      });
    } else if (type === 'text') {
      // ── Text Variable ─────────────────────────────────────────────
      // Simple scalar string. Use defaultValue or empty string.
      // Stored as a string (not array), so substituteVariables() will
      // use the string branch and wrap it in double quotes.
      //
      // Pre-check: '*' is invalid as a text variable default. Text
      // variables are free-text filters — '*' would be passed literally
      // into the query. The correct default is an empty string or a
      // specific value.
      if (defaultValue === '*') {
        resolved[key] = '';
        variableResults.push({
          key,
          type,
          values: '',
          source: 'text-wildcard-default',
          error: `Invalid defaultValue "*" on text variable. ` +
            `Text variables are free-text filters — "*" is passed literally into the query. ` +
            `Use an empty string or a specific default value.`
        });
        continue;
      }
      resolved[key] = defaultValue || '';
      variableResults.push({
        key,
        type,
        values: resolved[key],
        source: 'text'
      });
    } else if (type !== 'query') {
      // ── Unknown Type ──────────────────────────────────────────────
      // Not csv, text, or query – flag as error so the agent can fix it.
      resolved[key] = [];
      variableResults.push({
        key,
        type,
        values: [],
        source: 'unknown-type',
        error: `Unknown variable type "${type}". Valid types: query, csv, text`
      });
    } else if (type === 'query') {
      // ── Query Variable ────────────────────────────────────────────
      // Dynamic variable: execute a DQL query to get possible values.

      // Steps:
      //   0. Require non-empty `input`; if missing, emit query-error and fallback.
      //   a. Substitute already-resolved variables into the input DQL
      //      (this is why dependency ordering matters!)
      //   b. Execute the substituted query
      //   c. Extract values from the FIRST column of results
      //   d. Apply `multiple` selection:
      //        - multiple: true  -> all query values
      //        - multiple: false -> defaultValue (if present), otherwise first query value
      //   e. On failure or empty results, resolve to defaultValue (single-select only)
      //      or []
      const defaultValues = normalizeDefaultValues(defaultValue);
      if (!input) {
        const fallback = variable.multiple === true
          ? []
          : (defaultValues.length > 0 ? [defaultValues[0]] : []);
        resolved[key] = fallback;
        variableResults.push({
          key,
          type,
          values: resolved[key],
          source: 'query-error',
          error: 'Missing required `input` DQL for query variable.'
        });
        continue;
      }

      const substituted = substituteVariables(input, resolved);
      try {
        const result = await executeQuery(substituted, 1000, 7 * 24 * 60);
        if (result.success && result.data.records?.length > 0) {
          // Extract values from the first (and ideally only) column.
          // Dashboard variable queries MUST return exactly one field;
          // we take whatever the first field is.
          const records = result.data.records;
          const firstField = Object.keys(records[0])[0];
          const values = [...new Set(records.map(r => r[firstField]).filter(Boolean))];
          const selectedValues = variable.multiple === true
            ? values
            : (defaultValues.length > 0 ? [defaultValues[0]] : values.slice(0, 1));
          resolved[key] = selectedValues;
          variableResults.push({
            key,
            type,
            values: selectedValues.slice(0, 5),
            possibleValues: values.slice(0, 5),
            totalValues: selectedValues.length,
            availableValues: values.length,
            source: 'query',
            selectionMode: variable.multiple === true ? 'multiple-all' : 'single-first',
            query: substituted,
            queryWarnings: result.warnings || [],
          });
        } else {
          // Query succeeded but returned no records.
          const fallback = variable.multiple === true
            ? []
            : (defaultValues.length > 0 ? [defaultValues[0]] : []);
          resolved[key] = fallback;
          variableResults.push({
            key,
            type,
            values: resolved[key],
            source: 'query-empty',
            error: 'No values returned - the query needs to be changed. Check whether related fields exist in the data and are non-empty! ',
            query: substituted,
            queryWarnings: result.warnings || [],
          });
        }
      } catch (error) {
        // Query execution failed.
        const fallback = variable.multiple === true
          ? []
          : (defaultValues.length > 0 ? [defaultValues[0]] : []);
        resolved[key] = fallback;
        variableResults.push({
          key,
          type,
          values: resolved[key],
          source: 'query-error',
          error: error.message,
          query: substituted
        });
      }
    }
  }

  return { resolved, variableResults };
}

// ── Visualization Type Requirements ──────────────────────────────────

/**
 * Defines the minimum field-type requirements for each visualization type.
 *
 * Each entry lists one or more "slots" that the query result must satisfy.
 * A slot has:
 *   - name:     human-readable label shown in error messages
 *   - types:    array of acceptable DQL column types for this slot
 *   - count:    minimum number of fields that must match ('one' or 'oneOrMore')
 *   - required: whether the slot is mandatory (default true)
 *   - requiredWith: optional 2-element array [slotName, typeName] indicating
 *                   this slot is conditionally required when the named slot
 *                   has claimed a field of the specified type. For example,
 *                   ['Values', 'numericArray'] means "required when Values
 *                   was satisfied by a numericArray field".
 *
 * Type categories used:
 *   - numeric:   'long', 'double', 'duration'
 *   - timestamp: 'timestamp'
 *   - timeframe: 'timeframe'
 *   - any:       any column type satisfies this slot
 *   - array:     'array' (nested array, e.g. timeseries metric columns)
 *   - numericArray: 'array' whose nested element type is numeric
 *   - range:     object/record containing 'start' and 'end' (detected from records)
 *
 * Type preference ordering:
 *   When a slot accepts multiple types (e.g. Values accepts both scalar
 *   numerics and numericArray), fields are matched in the order the types
 *   are listed. Scalar types ('long', 'double', 'duration') are listed
 *   before 'numericArray' so that scalar fields are claimed preferentially,
 *   and numericArray is only used when no scalar match is available.
 *
 * Visualizations not listed here (table, raw, recordList, unknown) have
 * no field-type requirements and always pass this check.
 */
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
  meterBar: [
    { name: 'Meter value', types: ['long', 'double', 'duration'], count: 'one' },
  ],
  gauge: [
    { name: 'Gauge value', types: ['long', 'double', 'duration'], count: 'one' },
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
  choroplethMap: [
    { name: 'Country/subdivision code', types: ['string'], count: 'one' },
    { name: 'Color value', types: ['long', 'double', 'duration', 'string'], count: 'one' },
  ],
  dotMap: [
    { name: 'Latitude', types: ['long', 'double', 'duration'], count: 'one' },
    { name: 'Longitude', types: ['long', 'double', 'duration'], count: 'one' },
    { name: 'Color value', types: ['long', 'double', 'duration', 'string'], count: 'one', required: false },
  ],
  connectionMap: [
    { name: 'Latitude', types: ['long', 'double', 'duration'], count: 'one' },
    { name: 'Longitude', types: ['long', 'double', 'duration'], count: 'one' },
    { name: 'Color value', types: ['long', 'double', 'duration', 'string'], count: 'one', required: false },
  ],
  bubbleMap: [
    { name: 'Latitude', types: ['long', 'double', 'duration'], count: 'one' },
    { name: 'Longitude', types: ['long', 'double', 'duration'], count: 'one' },
    { name: 'Radius value', types: ['long', 'double', 'duration'], count: 'one' },
    { name: 'Color value', types: ['long', 'double', 'duration', 'string'], count: 'one', required: false },
  ],
  heatmap: [
    { name: 'X-axis', types: ['timeframe', 'range', 'string'], count: 'one' },
    { name: 'Y-axis', types: ['timeframe', 'range', 'string'], count: 'one' },
    { name: 'Values', types: ['long', 'double', 'duration', 'string'], count: 'one' },
  ],
  scatterplot: [
    { name: 'X-axis', types: ['timeframe', 'long', 'double', 'duration', 'string'], count: 'one' },
    { name: 'Y-axis', types: ['long', 'double', 'duration', 'string'], count: 'one' },
    { name: 'Names', types: 'any', count: 'oneOrMore', required: false },
  ],
};

/**
 * Extracts a flat field-name → type-string mapping from the `types` array
 * returned by a DQL query result. When multiple type blocks exist (different
 * indexRange entries), the first block's mappings are used because all rows
 * typically share the same schema.
 *
 * Special handling:
 *   - "numericArray": an `array` column whose nested element type is numeric
 *     (long or double). This is the pattern produced by `timeseries` queries.
 *   - "range": detected from *records* when a field value is an object with
 *     `start` and `end` keys (used by histogram bin fields).
 *
 * @param {Object} resultData - The `result.data` object from executeQuery
 * @returns {Object} - Map of fieldName → resolved type string
 */
function extractFieldTypes(resultData) {
  const fieldTypes = {};
  const typesArray = resultData?.types;

  if (!Array.isArray(typesArray) || typesArray.length === 0) return fieldTypes;

  // Use the first type block (covers all rows in the vast majority of queries)
  const mappings = typesArray[0]?.mappings || {};

  for (const [field, descriptor] of Object.entries(mappings)) {
    if (!descriptor || !descriptor.type) continue;

    if (descriptor.type === 'array') {
      // Check nested element type for numeric arrays
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

  // Detect "range" fields from record values (object with start + end).
  // Only apply when the types array did not already assign a known type
  // (e.g. timeframe fields have start/end in their value but should keep
  // their 'timeframe' type from the schema).
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

/**
 * Checks whether the query result fields satisfy the visualization's
 * field-type requirements. Returns an array of human-readable error strings
 * (empty if all requirements are met).
 *
 * Uses a recursive backtracking solver to assign query result fields to
 * visualization slots without greedy-stealing conflicts. Slots are processed
 * in two groups: unconditional required first, then conditional (requiredWith)
 * last so their conditions can be evaluated against the partial assignment.
 * Optional slots are excluded — they never cause failures.
 *
 * @param {string} visualization - The visualization type (e.g. 'lineChart')
 * @param {Object} resultData   - The full result.data from executeQuery
 * @returns {string[]} - Array of error messages (empty = compatible)
 */
function checkVisualizationCompatibility(visualization, resultData) {
  const requirements = VISUALIZATION_REQUIREMENTS[visualization];
  if (!requirements) return [];

  const fieldTypes = extractFieldTypes(resultData);
  const fieldEntries = Object.entries(fieldTypes);
  const availableStr = () => fieldEntries.map(([f, t]) => `${f} (${t})`).join(', ') || 'none';

  const unconditionalRequired = requirements.filter(s => !s.requiredWith && s.required !== false);
  const conditional = requirements.filter(s => s.requiredWith);
  const allSlots = [...unconditionalRequired, ...conditional];

  // Returns unclaimed fields whose type matches the slot.
  function candidates(slot, claimed) {
    return fieldEntries
      .filter(([f, t]) => !claimed.has(f) && (slot.types === 'any' || slot.types.includes(t)))
      .map(([f]) => f);
  }

  // Backtracking solver over `slots`. Returns assignment map or null.
  function solve(slots, idx, claimed, assignment) {
    if (idx >= slots.length) return assignment;
    const slot = slots[idx];

    if (slot.requiredWith) {
      const [targetName, targetType] = slot.requiredWith;
      if (fieldTypes[assignment[targetName]] !== targetType)
        return solve(slots, idx + 1, claimed, assignment); // condition not met — skip
    }

    for (const field of candidates(slot, claimed)) {
      const result = solve(slots, idx + 1, new Set([...claimed, field]),
                           { ...assignment, [slot.name]: field });
      if (result) return result;
    }
    return null; // required slot unsatisfied
  }

  if (solve(allSlots, 0, new Set(), {})) return []; // success — no errors

  // ── Diagnostics ───────────────────────────────────────────────────
  const errors = [];

  // 1. Unconditional required slots with zero candidates in isolation.
  for (const slot of unconditionalRequired) {
    if (candidates(slot, new Set()).length === 0) {
      const typeLabel = slot.types === 'any' ? 'any type' : slot.types.join(' | ');
      errors.push(
        `${slot.name}: requires a field of type [${typeLabel}], but none found in query result. Available fields: ${availableStr()}`
      );
    }
  }

  // 2. Conditional slot is bottleneck: unconditional-only solve succeeds
  //    but full solve fails → the conditional slot consumed a needed field.
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

  // 3. Field conflict among unconditional slots (catch-all).
  if (errors.length === 0) {
    errors.push(
      `Field conflict: not enough distinct fields to satisfy all required slots (${allSlots.map(s => s.name).join(', ')}). Available fields: ${availableStr()}`
    );
  }

  return errors;
}

// ── Tile Validation ─────────────────────────────────────────────────

/**
 * Validates a single data tile by executing its query (with variable
 * substitution) and then checking the result against the visualization's
 * field-type requirements.
 *
 * Validation steps performed per tile:
 *   1. Substitute variable placeholders with resolved values
 *   2. Execute the substituted DQL query with progressive settings
 *      until the first success with non-empty data and no visualization errors
 *   3. If all settings fail, keep the last attempt result
 *
 * This function is designed to be called via Promise.all for parallel
 * tile validation, and is extensible — new validation checks can be
 * added as additional steps after the query execution.
 *
 * @param {Object} tileQuery     - Tile query descriptor from extractTileQueries
 * @param {Object} resolvedVars  - Resolved variable map from resolveVariables
 * @returns {Object} - Validation result with query outcome and any errors
 */
async function validateTile(tileQuery, resolvedVars) {
  const queryEvaluationSettings = [
    { maxRecords: 10, pastMinutes: 7 * 24 * 60, maxVarValues: 10 },
    { maxRecords: 100, pastMinutes: 7 * 24 * 60, maxVarValues: 100 },
    { maxRecords: 10000, pastMinutes: 30,         maxVarValues: 1000 },
  ];
  const baseResult = {
    tileId: tileQuery.tileId,
    title: tileQuery.title,
    visualization: tileQuery.visualization,
    usesVariables: tileQuery.usesVariables,
    variables: tileQuery.variables,
    originalQuery: tileQuery.query,
    substitutedQuery: null,
    visualizationErrors: [],
  };

  try {
    let selectedResult = null;

    for (const setting of queryEvaluationSettings) {
      // Slice array variable values to maxVarValues for this attempt.
      // This progressively widens the filter on each retry, keeping
      // early attempts fast while ensuring the final attempt uses all values.
      const slicedVars = Object.fromEntries(
        Object.entries(resolvedVars).map(([k, v]) =>
          [k, Array.isArray(v) ? v.slice(0, setting.maxVarValues) : v]
        )
      );
      const substitutedQuery = substituteVariables(tileQuery.query, slicedVars);
      const result = await executeQuery(substitutedQuery, setting.maxRecords, setting.pastMinutes);

      const attemptResult = {
        ...baseResult,
        substitutedQuery,
        success: result.success,
        recordCount: result.success ? result.data?.records?.length || 0 : 0,
        error: result.success ? null : result.error,
        queryWarnings: result.warnings || [],
      };
      attemptResult.empty = attemptResult.success && attemptResult.recordCount === 0;

      if (result.success && result.data) {
        attemptResult.visualizationErrors = checkVisualizationCompatibility(
          tileQuery.visualization,
          result.data
        );
      }

      selectedResult = attemptResult;

      // Query execution failure (e.g. invalid DQL) will not improve with
      // different maxRecords/timeframe settings, so stop early.
      if (!attemptResult.success) {
        break;
      }

      // If the query executed succesfuly, results are not empty and there 
      // are no visulaization errors, we do not need to try other settings.
      if (
        attemptResult.success
        && !attemptResult.empty
        && attemptResult.visualizationErrors.length === 0
      ) {
        break;
      }
    }

    return selectedResult;
  } catch (error) {
    return {
      ...baseResult,
      success: false,
      recordCount: 0,
      empty: false,
      error: error.message,
    };
  }
}

// ── Dashboard Parsing ────────────────────────────────────────────────

/**
 * Scans all tiles in the dashboard and extracts the DQL queries from "data"
 * tiles. For each query, it also detects which dashboard variables are
 * referenced (using the same $VarName regex pattern).
 *
 * Tile selection criteria:
 *   - tile.type === 'data'  (data tiles have DQL queries; other tile types
 *     like "markdown", "section", etc. are skipped)
 *   - tile.query exists (some data tiles might theoretically lack a query)
 *
 * Variable detection in tile queries uses the same regex as dependency
 * detection: /\$([A-Za-z_][A-Za-z0-9_]*)/g
 *   - Matches: $Host, $ServiceFilter, $dt_timeframe_from
 *   - Does NOT distinguish between bare $Var and array($Var) – just collects
 *     which variable names are referenced (for the "unreferenced variables"
 *     diagnostic later)
 *
 * @param {Object} dashboard - The full dashboard JSON object
 * @returns {Array} - Array of { tileId, title, query, visualization,
 *                     usesVariables, variables } objects
 */
function extractTileQueries(dashboard) {
  const queries = [];
  // Same variable detection pattern used throughout the script
  const varPattern = /\$([A-Za-z_][A-Za-z0-9_]*)/g;

  if (!dashboard.content || !dashboard.content.tiles) {
    return queries;
  }

  // Tiles are stored as an object map { tileId: tileConfig, ... }
  for (const [tileId, tile] of Object.entries(dashboard.content.tiles)) {
    // Only process "data" tiles that have a query – skip markdown, sections, etc.
    if (tile.type === 'data' && tile.query) {
      // Detect all $VarName references in this tile's query
      const varMatches = tile.query.match(varPattern) || [];
      // De-duplicate (a query might reference $Host multiple times)
      const usedVars = [...new Set(varMatches.map(m => m.slice(1)))];
      queries.push({
        tileId: tileId,
        title: tile.title || `Tile ${tileId}`,
        query: tile.query,
        visualization: tile.visualization || 'unknown',
        usesVariables: usedVars.length > 0,
        variables: usedVars
      });
    }
  }

  return queries;
}

/**
 * Scans query strings for hardcoded time-range filters that would override
 * the dashboard UI time-frame picker.
 *
 * Detected patterns (case-insensitive):
 *   - filter timestamp > now() - ...
 *   - filter timestamp >= now() - ...
 *   - filter timestamp < now() - ...
 *   - filter timestamp <= now() - ...
 *   - filter timestamp > $dt_timeframe_from (or _to)
 *   - filter timestamp >= $dt_timeframe_from (or _to)
 *   - filter timestamp > "YYYY-..." (explicit timestamp literal)
 *   - timeframe: "now..."
 *   - from: now(...)
 *   - to: now(...)
 *
 * @param {Array} queries - Array of objects containing at least `query`
 * @param {Object} options
 * @param {string} options.idKey - Field name to use as identifier in warnings
 * @param {string} options.labelKey - Field name to use as title/label in warnings
 * @returns {Array} - Array of { id, label, query, pattern } warning objects
 */
function detectTimeFilters(queries, { idKey, labelKey }) {
  const timePatterns = [
    /\bfilter\s+timestamp\s*[><=!]+\s*now\s*\(/i,
    /\bfilter\s+timestamp\s*[><=!]+\s*\$dt_timeframe/i,
    /\bfilter\s+timestamp\s*[><=!]+\s*"\d{4}-/i,
    /\btimeframe\s*:\s*"now/i,
    /\bfrom\s*:\s*now\s*\(/i,
    /\bto\s*:\s*now\s*\(/i,
  ];
  const warnings = [];
  for (const q of queries) {
    if (!q?.query) continue;
    for (const pattern of timePatterns) {
      if (pattern.test(q.query)) {
        warnings.push({
          id: q[idKey],
          label: q[labelKey],
          query: q.query,
          pattern: pattern.source
        });
        break;
      }
    }
  }
  return warnings;
}

/**
 * Truncates report strings to a maximum length and appends an ellipsis when
 * truncation occurs.
 *
 * @param {string} value
 * @param {number} [maxLength=200]
 * @returns {string}
 */
function truncateForReport(value, maxLength = 200) {
  const text = String(value ?? '');
  return text.length > maxLength
    ? `${text.substring(0, maxLength)}…`
    : text;
}

// ── Main ─────────────────────────────────────────────────────────────

/**
 * Entry point – orchestrates the full dashboard validation flow:
 *
 *   ┌─────────────────────────────────────────────────────────────┐
 *   │  1. OBTAIN dashboard JSON (inline or fetch by ID)          │
 *   │  2. RESOLVE all variables (dependency-ordered, sequential)  │
 *   │  3. EXTRACT tile queries from data tiles                   │
 *   │  4. VALIDATE all tiles in parallel (via validateTile):     │
 *   │     a. Substitute variables into tile query                │
 *   │     b. Execute the DQL query                               │
 *   │     c. Check visualization field-type compatibility        │
 *   │  5. BUILD diagnostic report (summary + errors + verdict)   │
 *   └─────────────────────────────────────────────────────────────┘
 *
 * Input (event object): Either provide the full dashboard JSON directly,
 * or a dashboardId to fetch it from the Dynatrace Document API.
 *   - { dashboard: { ... } }          – inline dashboard JSON
 *   - { dashboardId: "abc-123-..." }  – fetch from Document API
 *
 * Output: A multi-line string report containing:
 *   - Variable resolution summary (csv/text/query counts, errors)
 *   - Tile query execution summary (success/failure counts)
 *   - Detailed error section (variable errors, tile errors, unreferenced vars)
 *   - Warnings section (e.g. hardcoded time-range filters)
 *   - Final verdict: "VALIDATION SUCCEEDED", "...WITH WARNINGS", or "FAILED"
 *
 * The verdict string is checked by deploy_dashboard.sh to gate deployment.
 */
export default async function(event) {
  // ── Step 1: Obtain the dashboard JSON ────────────────────────────
  // Accept either an inline dashboard object or a dashboardId to fetch
  let dashboardJson = event?.dashboard;
  const dashboardId = event?.dashboardId;

  // If no inline dashboard was provided but we have an ID, fetch it
  // from the Dynatrace Document API (platform/document/v1)
  if (!dashboardJson && dashboardId) {
    try {
      const response = await fetch(`/platform/document/v1/documents/${dashboardId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      dashboardJson = await response.json();
    } catch (error) {
      return {
        error: `Failed to fetch dashboard with ID: ${dashboardId}`,
        details: error.message
      };
    }
  }
   
  if (!dashboardJson) {
    return {
      error: 'No dashboard provided',
      usage: 'Pass either: {"dashboardId": "dashboard-id"} or {"dashboard": {...}}'
    };
  }

  // ── Step 1b: Validate dashboard structure ─────────────────────────
  // Check required top-level keys (name, type, content) and required
  // content keys (version, variables, tiles, layouts). This replaces the manual
  // jq-based schema check — all structural validation is now here.
  const schemaErrors = [];
  if (!dashboardJson.name) schemaErrors.push('Missing top-level "name"');
  if (!dashboardJson.type) schemaErrors.push('Missing top-level "type"');
  if (!dashboardJson.content) schemaErrors.push('Missing top-level "content"');
  if (dashboardJson.content) {
    if (dashboardJson.content.version === undefined) schemaErrors.push('Missing "content.version"');
    if (!dashboardJson.content.tiles) schemaErrors.push('Missing "content.tiles"');
    if (!dashboardJson.content.layouts) schemaErrors.push('Missing "content.layouts"');

    // ── Tile-level structural validation ──────────────────────────────
    const tiles = dashboardJson.content.tiles;
    if (tiles) {
      if (typeof tiles !== 'object' || Array.isArray(tiles)) {
        schemaErrors.push('"content.tiles" must be a non-empty object map (not an array)');
      } else if (Object.keys(tiles).length === 0) {
        schemaErrors.push('"content.tiles" is empty — dashboard has no tiles');
      } else {
        for (const [tileId, tile] of Object.entries(tiles)) {
          if (typeof tile !== 'object' || tile === null || Array.isArray(tile)) {
            schemaErrors.push(`Tile "${tileId}": value must be an object`);
            continue;
          }
          if (!tile.type) {
            schemaErrors.push(`Tile "${tileId}": missing required "type" (must be "markdown" or "data")`);
          } else if (tile.type !== 'markdown' && tile.type !== 'data') {
            schemaErrors.push(`Tile "${tileId}": invalid type "${tile.type}" (must be "markdown" or "data")`);
          } else if (tile.type === 'markdown') {
            if (tile.content === undefined || tile.content === null || tile.content === '') {
              schemaErrors.push(`Tile "${tileId}": markdown tile is missing "content" (the markdown text)`);
            }
          } else if (tile.type === 'data') {
            if (!tile.query) {
              schemaErrors.push(`Tile "${tileId}": data tile is missing "query" (the DQL query string)`);
            }
          }
        }
      }
    }
  }
  if (schemaErrors.length > 0) {
    const lines = [];
    lines.push(`Dashboard: ${dashboardJson.name || 'Unknown'} (${dashboardJson.id || 'Unknown'})`);
    lines.push('');
    lines.push('── Schema Errors ──────────────────────────');
    lines.push('  Required dashboard structure:');
    lines.push('    Top-level: name, type, content');
    lines.push('    content:   version, variables, tiles, layouts');
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

  // ── Step 2: Resolve all variables (sequentially, respecting deps) ──
  // Variables must be resolved BEFORE tile queries because tile queries
  // reference variables. Query-type variables may also depend on each
  // other, so they are resolved in topological (dependency) order.
  const { resolved, variableResults } = await resolveVariables(
    dashboardJson.content?.variables
  );

  // ── Step 3: Extract tile queries from data tiles ──────────────────
  // Scan the dashboard for tiles of type "data" that contain DQL queries.
  // Also detect which variables each tile query references.
  const tileQueries = extractTileQueries(dashboardJson);

  // ── Step 4 & 5: Validate all tiles in parallel ──────────────────────
  // Each tile is validated independently via validateTile(), which:
  //   1. Substitutes variable placeholders with resolved values
  //   2. Executes the DQL query (capped at 10 records)
  //   3. Checks visualization field-type compatibility
  // All tiles run in parallel via Promise.all for maximum throughput.
  const results = await Promise.all(
    tileQueries.map(q => validateTile(q, resolved))
  );

  // ── Step 5b: Detect hardcoded time-range filters in tile & variable queries ─────
  const variableQueries = (dashboardJson.content?.variables || [])
    .filter(v => v?.type === 'query' && v?.input)
    .map(v => ({
      key: v.key,
      title: v.title || v.key,
      query: v.input
    }));
  const timeFilterWarnings = [
    ...detectTimeFilters(tileQueries, { idKey: 'tileId', labelKey: 'title' }).map(w => ({ ...w, kind: 'tile' })),
    ...detectTimeFilters(variableQueries, { idKey: 'key', labelKey: 'title' }).map(w => ({ ...w, kind: 'variable' }))
  ];

  // ── Step 6: Build diagnostic output report ─────────────────────────
  //
  // The report is a plain-text string with these sections:
  //   1. Errors (conditional)     – detailed error info for each failure
  //   2. Warnings (conditional)   – e.g. hardcoded time filters
  //   3. Variables summary        – counts by type, per-variable status rows
  //   4. Tiles summary            – counts + per-tile status rows
  //   5. Final Verdict            – "VALIDATION SUCCEEDED", "...WITH WARNINGS", or "FAILED"

  // Detect unreferenced variables: variables that are DEFINED in the dashboard
  // but never referenced by any tile query. These are likely dead code or
  // leftovers from a removed tile.
  const definedVarKeys = new Set((dashboardJson.content?.variables || []).map(v => v.key));
  const referencedVarKeys = new Set(tileQueries.flatMap(q => q.variables));
  const unreferencedVars = [...definedVarKeys].filter(k => !referencedVarKeys.has(k));

  // Detect query variables that use static `data` records (no `fetch`) –
  // these behave identically to csv variables: values are hardcoded in the query.
  // We check the original variable definition `input` (the DQL string), not the result object.
  const varDefs = dashboardJson.content?.variables || [];
  const staticDataQueryVarKeys = new Set(
    varDefs
      .filter(v => {
        if (v.type !== 'query' || !v.input) return false;
        const q = v.input.replace(/\/\/.*/g, '').replace(/\/\*[\s\S]*?\*\//g, '');
        return /\bdata\b/.test(q) && !/\bfetch\b/.test(q);
      })
      .map(v => v.key)
  );

  // Categorize variables by type and resolution outcome
  const csvVars = variableResults.filter(v => (v.type === 'csv' || staticDataQueryVarKeys.has(v.key)) && v.source !== 'csv-empty');
  const textVars = variableResults.filter(v => v.type === 'text');
  const queryVars = variableResults.filter(v => v.type === 'query');
  const dependencyVarsError = variableResults.filter(v => v.source === 'dependency-error');
  const queryVarsNoDependencyError = queryVars.filter(v => v.source !== 'dependency-error');
  const unknownTypeVars = variableResults.filter(v => v.source === 'unknown-type');
  const queryVarsOk = queryVarsNoDependencyError.filter(v => v.source === 'query' && (v.totalValues || (Array.isArray(v.values) ? v.values.length : 0)) > 0);
  const queryVarsError = queryVarsNoDependencyError.filter(v => v.source === 'query-error');
  const queryVarsEmpty = queryVarsNoDependencyError.filter(v => v.source === 'query-empty' || (v.source === 'query' && (v.totalValues || (Array.isArray(v.values) ? v.values.length : 0)) === 0));
  const textVarsWildcard = variableResults.filter(v => v.source === 'text-wildcard-default');
  const csvVarsEmpty = variableResults.filter(v => v.source === 'csv-empty');
  const csvVarsOk = csvVars.filter(v => v.source === 'csv' && (Array.isArray(v.values) ? v.values.length : 0) > 0);

  // Categorize tiles
  const withVars = results.filter(r => r.usesVariables);
  const withoutVars = results.filter(r => !r.usesVariables);
  const tileOk = results.filter(r => r.success);
  const tileFailed = results.filter(r => !r.success);
  const tileEmpty = results.filter(r => r.empty);
  const tileVizErrors = results.filter(r => r.success && r.visualizationErrors?.length > 0);

  const hasVarErrors = dependencyVarsError.length > 0 || queryVarsError.length > 0 || queryVarsEmpty.length > 0 || unreferencedVars.length > 0 || unknownTypeVars.length > 0 || textVarsWildcard.length > 0 || csvVarsEmpty.length > 0;
  const hasTileErrors = tileFailed.length > 0;
  const hasTileEmpty = tileEmpty.length > 0;
  const hasVizErrors = tileVizErrors.length > 0;
  // Collect DQL query warnings from variable and tile query executions.
  // Each entry records the source (variable key or tile id/title) and the warning message.
  const dqlQueryWarnings = [];
  for (const v of variableResults) {
    if (Array.isArray(v.queryWarnings)) {
      for (const msg of v.queryWarnings) {
        dqlQueryWarnings.push({ kind: 'variable', id: v.key, label: v.key, message: msg });
      }
    }
  }
  for (const r of results) {
    if (Array.isArray(r.queryWarnings)) {
      for (const msg of r.queryWarnings) {
        dqlQueryWarnings.push({ kind: 'tile', id: r.tileId, label: r.title, message: msg });
      }
    }
  }

  const hasWarnings =
    timeFilterWarnings.length > 0 ||
    csvVars.length > 0 ||
    dqlQueryWarnings.length > 0;

  const lines = [];
  const issueSeparator = '';

  lines.push(`Dashboard: ${dashboardJson.name || 'Unknown'} (${dashboardJson.id || 'Unknown'})`);
  lines.push('');

  // ── Report Section 1: Warnings (only shown when warnings exist) ─────

  if (hasWarnings) {
    lines.push('── Warnings ─────────────────────────────────');
    lines.push('');
    if (csvVars.length > 0) {
      lines.push('  Hardcoded list variables detected:');
      lines.push('  CSV variables and Data-records query variables use hardcoded static values');
      lines.push('  that may not exist in the actual data, leading to empty dashboard tiles.');
      lines.push('  Double-check that the values match real data values in the environment.');
      lines.push('');
      for (const [idx, v] of csvVars.entries()) {
        const isStaticData = staticDataQueryVarKeys.has(v.key);
        const possibleRaw = isStaticData ? (v.possibleValues || v.values) : v.possibleValues;
        const selectedRaw = isStaticData ? v.values : v.selectedValues;
        const possible = Array.isArray(possibleRaw) ? possibleRaw.join(', ') : possibleRaw;
        const selected = Array.isArray(selectedRaw) ? selectedRaw.join(', ') : selectedRaw;
        lines.push(`    ⚠ $${v.key}${isStaticData ? '  (query with hardcoded data)' : '  (csv)'}`);
        lines.push(`      possible=[${possible}]`);
        lines.push(`      selected=[${selected}]`);
        if (idx < csvVars.length) lines.push(issueSeparator);
      }
    }

    if (dqlQueryWarnings.length > 0) {
      lines.push('');
      lines.push('  DQL query warnings (reported by the query engine):');
      lines.push('');
      for (const [idx, w] of dqlQueryWarnings.entries()) {
        const label = w.kind === 'variable' ? `    ⚠ $${w.id}` : `    ⚠ [${w.id}] ${w.label}`;
        lines.push(label);
        lines.push(`      ${w.message}`);
        if (idx < dqlQueryWarnings.length) lines.push(issueSeparator);
      }
    }

    if (timeFilterWarnings.length > 0) {
      lines.push('');
      lines.push('  CRITICAL WARNING: Hardcoded time-range filters detected in queries:');
      lines.push('  The dashboard UI has a built-in time-frame picker that controls');
      lines.push('  the query time range for all tiles. Hardcoded time filters override');
      lines.push('  this picker, preventing users from changing the time window!');
      lines.push('  DO NOT USE hardcoded time filters UNLESS EXPLICITLY REQUESTED BY THE USER!');
      lines.push('');
      for (const [idx, w] of timeFilterWarnings.entries()) {
        const q = w.query.trim().replace(/\s+/g, ' ');
        const label = w.kind === 'variable' ? `    ⚠ $${w.id} (${w.label})` : `    ⚠ [${w.id}] ${w.label}`;
        lines.push(label);
        lines.push(`      query: ${truncateForReport(q)}`);
        if (idx < timeFilterWarnings.length) lines.push(issueSeparator);
      }
    }

    lines.push('');
  }

  // ── Report Section 2: Errors (only shown when problems exist) ───────
  // Error conditions that trigger VALIDATION FAILED:
  //   - Variable dependency errors (unknown dependencies, cycles, blocked vars)
  //   - Variable query errors (query-error: execution or invalid configuration)
  //   - Variable queries returning zero results (query-empty)
  //   - Unreferenced variables (defined but unused in any tile)
  //   - Unknown variable types (not csv/text/query)
  //   - Wildcard '*' defaultValue on text variables
  //   - Any tile query execution failure
  //   - Tile queries returning no data (0 records)
  //   - Visualization field-type incompatibility (query returns wrong types)

  if (hasVarErrors || hasTileErrors || hasTileEmpty || hasVizErrors) {
    lines.push('── Errors ─────────────────────────────────');
    lines.push('');

    if (dependencyVarsError.length > 0) {
      lines.push('  Variable dependency errors:');
      lines.push('');
      for (const [idx, v] of dependencyVarsError.entries()) {
        lines.push(`    ✗ $${v.key}  →  ${v.error}`);
        if (idx < dependencyVarsError.length) lines.push(issueSeparator);
      }
    }

    if (unknownTypeVars.length > 0) {
      lines.push('  Invalid variable types (must be query, csv, or text):');
      lines.push('');
      for (const [idx, v] of unknownTypeVars.entries()) {
        lines.push(`    ✗ $${v.key}  type="${v.type}"  →  ${v.error}`);
        if (idx < unknownTypeVars.length) lines.push(issueSeparator);
      }
    }

    if (textVarsWildcard.length > 0) {
      lines.push('  Wildcard "*" defaultValue on text variables:');
      lines.push('');
      for (const [idx, v] of textVarsWildcard.entries()) {
        lines.push(`    ✗ $${v.key}  →  ${v.error}`);
        if (idx < textVarsWildcard.length) lines.push(issueSeparator);
      }
    }

    if (csvVarsEmpty.length > 0) {
      lines.push('  Empty CSV variables (no values to filter on — tile queries using these will return no data):');
      lines.push('');
      for (const [idx, v] of csvVarsEmpty.entries()) {
        lines.push(`    ✗ $${v.key}  →  CSV variable has no values. Add at least one value to the input list.`);
        if (idx < csvVarsEmpty.length) lines.push(issueSeparator);
      }
    }

    if (queryVarsError.length > 0) {
      lines.push('  Variable query errors:');
      lines.push('');
      for (const [idx, v] of queryVarsError.entries()) {
        const q = (v.query || '').trim().replace(/\s+/g, ' ');
        lines.push(`    ✗ $${v.key}`);
        lines.push(`      query: ${q.substring(0, 100)}${q.length > 100 ? '…' : ''}`);
        if (v.error) {
          const msg = v.error.replace(/\s+/g, ' ').substring(0, 120);
          lines.push(`      error: ${msg}`);
        }
        if (idx < queryVarsError.length) lines.push(issueSeparator);
      }
    }

    if (queryVarsEmpty.length > 0) {
      lines.push('  Variable queries returning no values:');
      lines.push('');
      for (const [idx, v] of queryVarsEmpty.entries()) {
        const q = (v.query || '').trim().replace(/\s+/g, ' ');
        lines.push(`    ✗ $${v.key}`);
        lines.push(`      query: ${q.substring(0, 100)}${q.length > 100 ? '…' : ''}`);
        if (v.error) {
          lines.push(`      instruction: ${v.error}`);
        }
        if (idx < queryVarsEmpty.length) lines.push(issueSeparator);
      }
    }

    if (unreferencedVars.length > 0) {
      lines.push('  Unreferenced variables (defined but not used in any tile query):');
      lines.push('');
      for (const [idx, key] of unreferencedVars.entries()) {
        lines.push(`    ✗ $${key}`);
        if (idx < unreferencedVars.length) lines.push(issueSeparator);
      }
    }

    if (tileFailed.length > 0) {
      lines.push('  Tile query errors:');
      lines.push('');
      for (const [idx, r] of tileFailed.entries()) {
        lines.push(`    ✗ [${r.tileId}] ${r.title}`);
        if (r.usesVariables) {
          const vars = `$${r.variables.join(', $')}`;
          lines.push(`      vars:        ${truncateForReport(vars)}`);
        }
        const orig = (r.originalQuery ?? '').trim().replace(/\s+/g, ' ');
        const sub  = (r.substitutedQuery ?? '').trim().replace(/\s+/g, ' ');
        lines.push(`      original:    ${truncateForReport(orig)}`);
        if (r.usesVariables) {
          lines.push(`      substituted: ${truncateForReport(sub)}`);
        }
        if (r.error) {
          const msg = r.error.replace(/\s+/g, ' ').substring(0, 120);
          lines.push(`      error: ${msg}`);
        }
        if (idx < tileFailed.length) lines.push(issueSeparator);
      }
    }

    if (tileEmpty.length > 0) {
      lines.push('  Tile queries returning no data (0 records within the last 7 days):');
      lines.push('');
      for (const [idx, r] of tileEmpty.entries()) {
        lines.push(`    ✗ [${r.tileId}] ${r.title}`);
        const sub = (r.substitutedQuery ?? '').trim().replace(/\s+/g, ' ');
        lines.push(`      query: ${truncateForReport(sub)}`);
        if (idx < tileEmpty.length) lines.push(issueSeparator);
      }
    }

    if (tileVizErrors.length > 0) {
      lines.push('  Visualization type errors (query result fields incompatible with visualization):');
      lines.push('');
      for (const [idx, r] of tileVizErrors.entries()) {
        lines.push(`    ✗ [${r.tileId}] ${r.title}  (${r.visualization})`);
        for (const vizErr of r.visualizationErrors) {
          lines.push(`      → ${vizErr}`);
        }
        if (idx < tileVizErrors.length) lines.push(issueSeparator);
      }
    }

    lines.push('');
  }

  // ── Report Section 3: Variables Summary ─────────────────────────────

  lines.push('── Variables ──────────────────────────────');
  const allCsvVars = variableResults.filter(v => v.type === 'csv' || staticDataQueryVarKeys.has(v.key));
  lines.push(`  csv:   ${allCsvVars.length}    text: ${textVars.length}    query: ${queryVars.length}${unknownTypeVars.length > 0 ? `    unknown: ${unknownTypeVars.length}` : ''}`);
  if (allCsvVars.length > 0) {
    lines.push(`  csv variables:   ${csvVarsOk.length} ok  |  ${csvVarsEmpty.length} no values`);
  }
  if (queryVars.length > 0) {
    lines.push(`  query results:  ${queryVarsOk.length} ok  |  ${queryVarsError.length} error  |  ${queryVarsEmpty.length} no values${dependencyVarsError.length > 0 ? `  |  ${dependencyVarsError.length} dependency error` : ''}`);
  }
  lines.push('');
  // Per-variable status line: ✓ for healthy, ✗ for any problem
  for (const v of variableResults) {
    const count = Array.isArray(v.values) ? v.values.length : (v.values ? 1 : 0);
    const totalCount = v.totalValues || count;
    let status = '✓';
    if (v.source === 'query-error' || v.source === 'unknown-type' || v.source === 'text-wildcard-default' || v.source === 'dependency-error' || v.source === 'csv-empty') status = '✗';
    else if (v.type === 'query' && totalCount === 0) status = '✗';
    if (unreferencedVars.includes(v.key)) status = '✗';
    lines.push(`  ${status} $${v.key.padEnd(20)} type=${v.type.padEnd(6)}  source=${v.source.padEnd(12)}  values=${totalCount}`);
  }
  lines.push('');

  // ── Report Section 4: Tiles Summary ─────────────────────────────────
  // Summary counters followed by per-tile status rows with 5 columns:
  //   tile name (truncated), has variables, query OK, has data, visualization OK

  const withVarsVizFail = withVars.filter(r => r.success && r.visualizationErrors?.length > 0);
  const withoutVarsVizFail = withoutVars.filter(r => r.success && r.visualizationErrors?.length > 0);
  const withVarsEmpty = withVars.filter(r => r.empty);
  const withoutVarsEmpty = withoutVars.filter(r => r.empty);

  lines.push('── Tiles ──────────────────────────────────');
  lines.push(`  Total: ${results.length}    Successful: ${tileOk.length}    Failed: ${tileFailed.length}${tileEmpty.length > 0 ? `    Empty: ${tileEmpty.length}` : ''}${tileVizErrors.length > 0 ? `    Viz errors: ${tileVizErrors.length}` : ''}`);
  lines.push(`  With variables:    ${withVars.length} total  |  ${withVars.filter(r => r.success).length} ok  |  ${withVars.filter(r => !r.success).length} failed  |  ${withVarsEmpty.length} empty  |  ${withVarsVizFail.length} viz errors`);
  lines.push(`  Without variables: ${withoutVars.length} total  |  ${withoutVars.filter(r => r.success).length} ok  |  ${withoutVars.filter(r => !r.success).length} failed  |  ${withoutVarsEmpty.length} empty  |  ${withoutVarsVizFail.length} viz errors`);
  lines.push('');
  // Per-tile status row
  for (const r of results) {
    const name = (r.title || `Tile ${r.tileId}`);
    const truncatedName = name.length > 35 ? name.substring(0, 32) + '…' : name;
    const queryStatus = r.success ? '✓' : '✗';
    const dataStatus = r.success
      ? (r.empty ? '✗' : '✓')
      : '-';
    const vizStatus = r.success
      ? (r.visualizationErrors?.length > 0 ? '✗' : '✓')
      : '-';
    const varsLabel = r.usesVariables ? 'yes' : 'no';
    const overallStatus = (r.success && !r.empty && !(r.visualizationErrors?.length > 0)) ? '✓' : '✗';
    lines.push(`  ${overallStatus} ${truncatedName.padEnd(36)} vars=${varsLabel.padEnd(4)} query=${queryStatus}  data=${dataStatus}  viz=${vizStatus}`);
  }
  lines.push('');

  // ── Report Section 5: Final Verdict ─────────────────────────────
  // The verdict string is the critical output – deploy_dashboard.sh grep's
  // for "VALIDATION SUCCEEDED" to decide whether to proceed with deployment.
  // "VALIDATION SUCCEEDED (WITH WARNINGS)" also matches that grep.

  lines.push('');
  if (hasVarErrors || hasTileErrors || hasTileEmpty || hasVizErrors) {
    lines.push('══════════════════════════════════════════');
    lines.push('  ✗ VALIDATION FAILED');
    lines.push('  DO NOT DEPLOY THE DASHBOARD UNTIL ALL ERRORS ARE FIXED!!!');
    lines.push('══════════════════════════════════════════');
  } else if (hasWarnings) {
    lines.push('══════════════════════════════════════════');
    lines.push('  ✓ VALIDATION SUCCEEDED (WITH WARNINGS)');
    lines.push('  Review the warnings above before deployment');
    lines.push('══════════════════════════════════════════');
  } else {
    lines.push('══════════════════════════════════════════');
    lines.push('  ✓ VALIDATION SUCCEEDED');
    lines.push('  Dashboard is ready for deployment');
    lines.push('══════════════════════════════════════════');
  }

  return lines.join('\n');
}
