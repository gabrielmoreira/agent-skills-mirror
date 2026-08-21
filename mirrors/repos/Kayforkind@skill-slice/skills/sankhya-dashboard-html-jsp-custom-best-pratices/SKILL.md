---
name: sankhya-dashboard-html-jsp-custom-best-pratices
description: "Packages Sankhya HTML5/JSP dashboards and gadgets: snk:query row iteration, URL-parameter hardening, openLevel drill-down, TGFCAB/TGFITE SQL, and BI zip layout. Trigger on Sankhya dashboard, gadget, or boas práticas do Sankhya. Not for generic React SPAs or non-Sankhya BI tools. Do not use for native ERP Java screens outside the JSP/HTML5 gadget path."
version: 1.0.1
category: code
risk: safe
source: community
tags: [sankhya, dashboard, jsp, html, sql, best-practices, bi]
date_added: "2026-03-10"
---

# Sankhya Dashboard — HTML/JSP/Java/SQL Best Practices

## Overview

Consolidated guide of patterns and best practices for creating and maintaining dashboards, SQL queries, BI parameterization, and UI/UX within the Sankhya ecosystem (JSP/HTML/Java). Covers code generation, visual consistency, database exploration, and BI construction flow.

> Table and field names below are representative and may vary per instance implementation. Always verify against the target instance's data dictionary.

## When to Use

Use this skill when:

- The user asks about "boas práticas do Sankhya" or "Sankhya best practices".
- The user mentions "dashboard Sankhya" or is working on a Sankhya BI dashboard.
- The user asks for anything related to the word "Sankhya".
- The user wants to create or modify code files (JSP, HTML, JS, SQL) for Sankhya dashboards or gadgets.
- The user needs patterns for `snk:query`, `openLevel`, drill-down, or BI HTML5 component packaging.

## Prerequisites

- Access to a Sankhya instance (application server + Oracle/SQL Server backend).
- DBExplorer available for table/field inspection.
- Familiarity with JSP/JSTL, HTML5, JavaScript, and SQL.
- Windows host (PowerShell) is the primary development environment.

## Procedure

### 1. Code Best Practices (JSP/JSTL)

Apply JSP/JSTL patterns and server-side organization to reduce compilation errors, rendering failures, and regressions.

**Implementation guidelines:**

1. Declare JSP directives and mandatory taglibs at the top of the file.
2. Force `isELIgnored="false"` to enable `${...}` at render time.
3. Prefer `core_rt` for JSTL core in the Sankhya ecosystem.
4. Avoid Java scriptlets in JSP; use JSTL (`c:if`, `c:choose`, `c:forEach`).
5. Modularize business logic (layers/services); avoid single-file coupling.
6. Never hardcode credentials, sensitive URLs, or tokens.
7. Model global UI state (data, filters, sorting, active tab) and reset state before new load.
8. Persist view preferences in `localStorage` (column order and sorting).
9. Implement lazy-load for heavy tabs/modals to reduce initial load time.
10. **Parameter hardening**: Always define a fallback default for URL parameters via `c:set` to avoid HTTP 500 on the Sankhya Java server.
11. **Layer separation (JSP vs JS)**: Do not inject JSP tags directly inside `<script>` blocks. Use hidden HTML containers to pass data to JavaScript, preserving IDE linting health.

**Mandatory JSP header:**

```jsp
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" isELIgnored="false" %>
<%@ taglib prefix="snk" uri="/WEB-INF/tld/sankhyaUtil.tld" %>
<%@ taglib uri="http://java.sun.com/jstl/core_rt" prefix="c" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/functions" prefix="fn" %>
<snk:load />
```

**Asset loading in dashboard/gadget:**

- Reference files with `contextPath` + `BASE_FOLDER`.
- In secondary levels (`openLevel`), use absolute paths to avoid resolution breakage.

```html
<script src="${pageContext.request.contextPath}/${BASE_FOLDER}/js/app.js"></script>
<link rel="stylesheet" href="${pageContext.request.contextPath}/${BASE_FOLDER}/css/style.css" />
```

**Safe `snk:query` consumption:**

- Iterate over `query.rows` (not the root object).
- Test empty with `empty query.rows`.

```jsp
<snk:query var="qDados">
    SELECT CAB.NUNOTA, CAB.CODPARC
      FROM TGFCAB CAB
</snk:query>

<c:choose>
    <c:when test="${empty qDados.rows}">
        <span>Sem resultados</span>
    </c:when>
    <c:otherwise>
        <c:forEach var="linha" items="${qDados.rows}">
            ${linha.NUNOTA}
        </c:forEach>
    </c:otherwise>
</c:choose>
```

**Parameter sanitization before SQL:**

1. Normalize input value.
2. Remove quotes (`"` and `&quot;`) before injecting into query.
3. Define safe fallback to avoid invalid SQL.

```jsp
<c:set var="raw_codusu" value="${empty param.P_CODUSU ? '0' : param.P_CODUSU}" />
<c:set var="codusu_limpo" value="${fn:replace(raw_codusu, '\"', '')}" />
<c:set var="codusu_limpo" value="${fn:replace(codusu_limpo, '&quot;', '')}" />
<c:set var="codusu_seguro" value="${empty codusu_limpo ? '0' : codusu_limpo}" />

<snk:query var="qAcessos">
    SELECT CODUSU, NOMEUSU
      FROM TSIUSU
     WHERE CODUSU = :codusu_seguro
</snk:query>
```

**Screen state and lazy-load in single dashboard:**

- Define global lists for reuse across KPI, chart, table, and modals.
- Store per-tab load flag to avoid unnecessary re-queries.
- Reload data and reopen context (product/tab) after transactional update.

```js
var dadosGlobais = [];
var produtoAtual = null;
var abaCarregada = {};

function abrirDetalhe(dado) {
  produtoAtual = dado;
  abaCarregada = {};
  trocarAba("estoque");
}

function trocarAba(aba) {
  if (aba === "estoque" && !abaCarregada.estoque) carregarAbaEstoque(produtoAtual.CODPROD);
  if (aba === "pedidos" && !abaCarregada.pedidos) carregarAbaPedidos(produtoAtual.CODPROD);
  if (aba === "parceiros" && !abaCarregada.parceiros) carregarAbaParceiros(produtoAtual.CODPROD);
}
```

**Example: parameter hardening + layer separation:**

```jsp
<%-- 1. Hardening at top of file --%>
<c:set var="v_salesagent" value="${empty param.SALESAGENT ? '0' : param.SALESAGENT}" />

<%-- 2. Hidden container for data (JSP vs JS separation) --%>
<div id="data-container" style="display:none;">
    [
    <c:forEach var="row" items="${qDados.rows}" varStatus="loop">
        { "id": ${row.ID}, "nome": "${fn:replace(row.NOME, '"', '\\"')}" }${!loop.last ? ',' : ''}
    </c:forEach>
    ]
</div>

<script>
    // 3. JS only reads data from container
    const rawData = document.getElementById('data-container').textContent.trim();
    const myData = rawData ? JSON.parse(rawData) : [];
</script>
```

### 2. Visual Identity (Colors)

Standardize visual identity in BI components for consistency across HTML5 gadgets, tables, and indicators.

**UI/UX guidelines:**

1. Define palette via tokens (`--color-*`) to avoid scattered values.
2. Prioritize minimum contrast between text/background (operational legibility).
3. Maintain consistent visual semantics: success, warning, error, neutral.
4. Allow override by SQL-driven data (`BKCOLOR`, `FGCOLOR`) when needed.
5. Use sticky header and fixed columns for wide, high-volume tables.
6. Differentiate row status via CSS classes (approved, partial, historical, critical) for fast operational reading.

```html
<style>
  :root {
    --color-bg: #F5F7FA;
    --color-surface: #FFFFFF;
    --color-text: #1F2937;
    --color-success: #1A7F37;
    --color-warning: #B26A00;
    --color-danger: #B42318;
    --color-accent: #0E5A8A;
  }

  .card {
    background: var(--color-surface);
    color: var(--color-text);
    border-radius: 8px;
    padding: 12px;
  }
</style>
```

**SQL-driven color:**

```sql
SELECT
    V.CODMETA,
    V.VALOR_ATUAL,
    V.VALOR_META,
    CASE WHEN V.VALOR_ATUAL >= V.VALOR_META THEN '#1A7F37' ELSE '#B42318' END AS BKCOLOR,
    '#FFFFFF' AS FGCOLOR
FROM AD_DADOS_VENDA V
```

**Sticky header and fixed columns:**

```html
<style>
  #tblDados thead th { position: sticky; top: 0; z-index: 4; }
  #tblDados .col-fixa-1 { position: sticky; left: 0; z-index: 3; }
  #tblDados .col-fixa-2 { position: sticky; left: var(--fix-col-1-width); z-index: 2; }
  .row-aprovacao td { background: #ffe8cc; color: #7a3a00; }
  .row-parcial td { background: #fff4c4; color: #5e4c00; }
</style>
```

### 3. Database Exploration and Queries

Structure data exploration with focus on performance, legibility, and correct Sankhya entity mapping.

**DBExplorer best practices:**

1. Use DBExplorer to inspect tables, fields, indexes, views, and procedures.
2. Respect configured return limit (e.g., `DBEXPMAXROW`) to avoid excessive load.
3. Avoid `SELECT *` on tables with voluminous fields (BLOB/CLOB).

**Essential ecosystem maps:**

- **Dictionary:** `TDDTAB`, `TDDCAM`, `TDDOPC`, `TDDINS`, `TDDLIG`.
- **Commercial/financial:** `TGFCAB`, `TGFITE`, `TGFTOP`, `TGFPAR`, `TGFPRO`, `TGFEST`, `TGFVAR`.
- **Security/access:** `TSIUSU`, `TSIGRU`, `TSIACI`, `TSIIMP`.

**Recommended SQL patterns:**

1. In versioned TOP, relate `CODTIPOPER` + alteration date (`DHTIPOPER`/`DHALTER`).
2. For optional filters, use pattern `(... = :P_PARAM OR :P_PARAM IS NULL)`.
3. Always parameterize (avoid user literals).

```sql
SELECT
    CAB.NUNOTA,
    CAB.CODPARC,
    CAB.DTNEG,
    ITE.SEQUENCIA,
    ITE.CODPROD,
    (ITE.VLRTOT - ITE.VLRDESC) AS VLR_LIQUIDO
FROM TGFCAB CAB
JOIN TGFITE ITE
  ON ITE.NUNOTA = CAB.NUNOTA
JOIN TGFTOP TOP
  ON TOP.CODTIPOPER = CAB.CODTIPOPER
 AND TOP.DHALTER   = CAB.DHTIPOPER
WHERE (CAB.CODPARC = :P_CODPARC OR :P_CODPARC IS NULL)
  AND (CAB.CODVEND = :P_CODVEND OR :P_CODVEND IS NULL)
```

**User access map query:**

```sql
SELECT
    U.CODUSU,
    U.NOMEUSU,
    G.NOMEGRUPO,
    A.CODREL,
    I.NOME AS DESCRICAO_RECURSO,
    A.CONS,
    A.ALTERA
FROM TSIUSU U
JOIN TSIGRU G ON G.CODGRUPO = U.CODGRUPO
JOIN TSIACI A ON A.CODGRUPO = U.CODGRUPO
JOIN TSIIMP I ON I.CODREL = A.CODREL
WHERE U.CODUSU = :P_CODUSU
ORDER BY I.NOME
```

### 4. BI Builder Guide

Apply HTML5 component development flow in BI to ensure rendering, reactivity, and navigation between levels.

**Structure and publication:**

1. Package component in `.zip` with `index.html` as main entry.
2. Organize static resources in `assets/` (CSS, JS, libs, images).
3. Use XML/design as needed; consider entry JSP when server-side preprocessing is required.

**Data flow and parameters:**

1. Define SQL or BeanShell variables per complexity.
2. Use parameter translation prefixes:
   - `:` for standard bind.
   - `:#` for literal substitution (use with caution and validation).
   - `:@` for text literal in scenarios like `LIKE`.
3. For extensive multi-list parameters, use `/*inCollection*/`.

```sql
SELECT
    C.CODCID,
    C.NOMECID,
    C.UF
FROM AD_TABELA_EXEMPLO C
WHERE /*inCollection*/ C.CODCID IN :P_CODCID /*inCollection*/
```

**Reactivity and lifecycle:**

1. Program re-render when global filters change.
2. Avoid exclusive dependency on `DOMContentLoaded` for injected content.
3. Apply async initialization to ensure elements are available.

```html
<script>
  function renderizarComponente(dados) {
    // Update DOM, charts, and KPIs with received data
  }

  function iniciar() {
    const dadosIniciais = window.snkBIData || [];
    renderizarComponente(dadosIniciais);
  }

  setTimeout(iniciar, 300);
</script>
```

**Drill-down and events:**

1. Model independent levels (macro → micro) with explicit arguments.
2. Avoid empty container in subsequent levels.
3. Use context inheritance between levels to preserve filters and navigation.
4. Implement click actions to update details and open native screens with context key.

**Multi-level navigation (openLevel and context contract):**

1. Define level constants in configuration (`NIVEL_RESUMO`, `NIVEL_DETALHE`, `NIVEL_ITEM`) to avoid loose-string coupling.
2. Encapsulate `openLevel` in dedicated functions per navigation route.
3. Pass context parameters between levels with explicit contract (`ARG_*` for keys, `P_*` for filters/period).
4. Validate `openLevel` availability and mandatory parameters before navigating.
5. Apply error fallback in console/UI when context does not allow level opening.

```js
var cfg = window.DASH_CONFIG || {};
var NIVEL_DETALHE = cfg.NIVEL_DETALHE || "NIVEL_B";
var NIVEL_ITEM = cfg.NIVEL_ITEM || "NIVEL_C";

function abrirNivelDetalhe(codigoEntidade) {
  if (!codigoEntidade || typeof openLevel !== "function") return;
  openLevel(NIVEL_DETALHE, {
    ARG_CODENT: parseInt(codigoEntidade, 10),
    P_PERIODO_INI: cfg.P_PERIODO_INI || "",
    P_PERIODO_FIN: cfg.P_PERIODO_FIN || "",
    P_CODMETA: cfg.P_CODMETA || ""
  });
}

function abrirNivelItem(codigoEntidadeFilha) {
  if (!codigoEntidadeFilha || typeof openLevel !== "function") return;
  openLevel(NIVEL_ITEM, {
    ARG_CODENT_FILHA: parseInt(codigoEntidadeFilha, 10),
    P_PERIODO_INI: cfg.P_PERIODO_INI || "",
    P_PERIODO_FIN: cfg.P_PERIODO_FIN || "",
    P_CODMETA: cfg.P_CODMETA || ""
  });
}
```

**Security and scope-based access blocking:**

1. Restrict any level query by user-meta/scope relationship before aggregating data.
2. Centralize security predicate in a `WHERE` builder function for reuse across KPIs, grids, and charts.
3. Prefer session variables (`CODUSU_LOG` or equivalent logged-user function) to avoid user parameter spoofing.
4. Block load when critical parameters are missing (e.g., period, meta, drill-down entity).

```sql
SELECT
    M.CODMETA,
    M.CODENTIDADE,
    SUM(M.VLRPREV) AS VLR_PREV,
    SUM(M.VLRREAL) AS VLR_REAL
FROM AD_DADOS_META M
WHERE M.CODMETA = :P_CODMETA
  AND M.DTREF BETWEEN TO_DATE(:P_PERIODO_INI, 'DD/MM/YYYY')
                  AND TO_DATE(:P_PERIODO_FIN, 'DD/MM/YYYY')
  AND EXISTS (
      SELECT 1
      FROM AD_META_USUARIO_LIB L
      WHERE L.CODMETA = M.CODMETA
        AND L.CODUSU = STP_GET_CODUSULOGADO
  )
GROUP BY M.CODMETA, M.CODENTIDADE
```

**Hierarchical grid with expand/collapse:**

1. Structure `filhosPorPai` map and `nosExpandidos` state for incremental tree rendering.
2. Initialize non-analytical top-level nodes as expanded for better initial reading.
3. In collapsed nodes, display descendant aggregates to maintain context without opening full tree.
4. Provide "Expand all" and "Collapse all" quick actions in header.
5. In text filters, include ancestors of found nodes to preserve hierarchical traceability.

```js
var filhosPorPai = {};
var nosExpandidos = {};

function alternarNo(codNo) {
  var id = String(codNo);
  nosExpandidos[id] = !nosExpandidos[id];
  renderizarGrid();
}

function obterVisiveis(raiz) {
  var lista = [];
  function visitar(pai) {
    (filhosPorPai[pai] || []).forEach(function (no) {
      lista.push(no);
      if (nosExpandidos[String(no.CODNO)]) visitar(String(no.CODNO));
    });
  }
  visitar(String(raiz || ""));
  return lista;
}
```

**Load resilience:**

1. Separate main load from complementary load (e.g., monthly actuals); do not block primary view on secondary failure.
2. Handle per-component data absence (`vazio`) without dropping entire layout.
3. Destroy chart instances before recreating to avoid leakage and visual overlap.
4. Load secondary panels only when opening corresponding tab/view (on-demand).

**Intra-level navigation (single JSP):**

1. Treat single JSP as navigation shell: main table + detail modal + internal tabs + auxiliary modals.
2. Chain clicks without switching Sankhya level: KPI → modal list, chart → table filter, table row → detail.
3. Apply action shortcuts in detail to open native registration in primary key context.
4. Close modal by overlay click to reduce usage friction.

```js
function abrirTelaNativa(resourceIdBase64, pkObj) {
  var pk = btoa(JSON.stringify(pkObj));
  top.location.href = "/mge/system.jsp#app/" + resourceIdBase64 + "/" + pk + "&pk-refresh=" + Date.now();
}

function onKpiClick(lista) {
  abrirModalLista("Itens selecionados", "Navegação por atalho", lista);
}

function onGraficoClick(grupo) {
  filtrarTabelaPorGrupo(grupo);
}
```

**Operational UI feedback:**

1. Display explicit loading, empty, and error states in each panel.
2. On update actions, disable confirm button until `executeQuery` returns.
3. After success, reload data and restore previous context (product and active tab).

**Internal security variables:**

- Leverage session variables for row-level security (`CODUSU_LOG`, `CODGRU_LOG`, `CODVEN_LOG`).
- Restrict data by user context before building visualizations.

## Pitfalls

- **Missing parameter fallback → HTTP 500**: Always use `c:set` with a default value for URL parameters before passing to `snk:query`. Missing parameters cause server-side null errors.
- **JSP tags inside `<script>` blocks**: Breaks IDE linting and can cause rendering issues. Use hidden HTML containers to pass server-side data to JavaScript.
- **Iterating root query object instead of `.rows`**: `snk:query` returns an object with a `rows` property. Iterating the root object yields nothing or errors.
- **`SELECT *` on BLOB/CLOB tables**: Causes excessive memory consumption in DBExplorer and dashboards. Always select explicit columns.
- **Loose-string level names in `openLevel`**: Hardcoded level strings break when configuration changes. Use constants from `DASH_CONFIG`.
- **Chart recreation without destroying**: Causes visual overlap and memory leaks. Always destroy previous chart instance before re-creating.
- **User parameter spoofing**: Never trust `P_CODUSU` from URL for security. Use session variable `CODUSU_LOG` or `STP_GET_CODUSULOGADO`.
- **Blocking primary view on secondary load failure**: Complementary data failure should not prevent main dashboard rendering. Separate load paths.
- **`DOMContentLoaded` only for injected content**: Content injected after DOM ready will not trigger it. Use `setTimeout` or MutationObserver.
- **Relative paths in `openLevel` secondary levels**: Break asset resolution. Use absolute paths with `contextPath` + `BASE_FOLDER`.

## Verification

1. **JSP compiles without errors**: Deploy the JSP file and access it via browser. Confirm no HTTP 500 or compilation error in server logs.
2. **Parameter hardening check**: Access the dashboard URL without expected parameters (e.g., omit `P_CODUSU`). Verify fallback value is used and no 500 error occurs.
3. **Empty query handling**: Run `snk:query` against a condition that returns zero rows. Confirm the `c:when test="${empty qDados.rows}"` branch renders the "Sem resultados" message.
4. **Layer separation**: Open the JSP in an IDE with JS linting. Confirm no JSP tags appear inside `<script>` blocks and JS reads from hidden containers.
5. **DBExplorer query**: Run exploration SQL in DBExplorer. Confirm it respects `DBEXPMAXROW` and returns expected columns without BLOB/CLOB overflow.
6. **openLevel navigation**: Click a drill-down element. Confirm the next level opens with correct `ARG_*` and `P_*` context parameters.
7. **Security predicate**: Run the security query with a user who has no meta assignment. Confirm zero rows returned (access blocked).
8. **Chart destroy/recreate**: Trigger a re-render of a chart panel. Confirm no visual overlap or canvas duplication.
9. **Lazy-load tabs**: Open the dashboard and confirm secondary tabs do not fire queries until clicked. Check network tab or server logs.
10. **Sticky header**: Scroll a wide table vertically and horizontally. Confirm header stays pinned and fixed columns remain visible.

## Limitations

- Use this skill only when the task clearly matches the Sankhya dashboard/JSP/BI scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Table and field names are representative; always verify against the target instance's data dictionary (`TDDTAB`, `TDDCAM`).
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
