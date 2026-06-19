---
name: cnki-download
description: Download a paper PDF/CAJ from CNKI. Requires user to be logged in. Use when user wants to download a specific paper.
argument-hint: "[paper URL or blank if already on detail page]"
---

# CNKI Paper Download (文献下载)

> **RC browser tool**: navigate with `browser action=open url="..."`; run the JS in each step via `browser action=act kind=evaluate fn="<the async function shown>"` (the whole function body goes into `fn`). Never pass a `profile` — RC uses its default managed Chrome (CDP 18800).

## Prerequisites

User **must be logged in** to CNKI with download permissions.

## Arguments

`$ARGUMENTS` is optionally a paper detail URL. If blank, uses current page.

## Steps

### 1. Navigate (if URL provided)

If URL provided: use `browser action=open` to go to the URL directly (no wait_for needed — Step 2 handles waiting).

**Important**: Always use `browser action=open` instead of clicking links on the search results page. Clicking opens a new tab and wastes 3 extra tool calls (`browser action=tabs` + `browser action=focus` + `browser action=snapshot`).

### 2. Check status and download (single async browser act kind=evaluate)

Replace `FORMAT` with `"pdf"` or `"caj"`:

```javascript
async () => {
  // Wait for page load
  await new Promise((r, j) => {
    let n = 0;
    const c = () => {
      if (document.querySelector('.brief h1')) r();
      else if (++n > 30) j('timeout');
      else setTimeout(c, 500);
    };
    c();
  });

  // Captcha check
  const cap = document.querySelector('#tcaptcha_transform_dy');
  if (cap && cap.getBoundingClientRect().top >= 0) {
    return { error: 'captcha', message: 'CNKI 正在显示滑块验证码。请在 Chrome 中手动完成拼图验证。' };
  }

  const format = "FORMAT"; // "pdf" or "caj"

  // Check download links
  const pdfLink = document.querySelector('#pdfDown') || document.querySelector('.btn-dlpdf a');
  const cajLink = document.querySelector('#cajDown') || document.querySelector('.btn-dlcaj a');

  // Check login status. The download links (#pdfDown/#cajDown) are ALWAYS present
  // even when logged out — clicking them just opens a login/order page — so their
  // presence is NOT a login signal. The reliable signal is the page header: when
  // logged out it shows the "机构登录 / 个人登录" CTAs and the personal-name slot is
  // empty; once logged in the CTA text is replaced by the user's name.
  const loginArea = document.querySelector('.ecp_header_login_area, .ecp_header_login_status');
  const loginAreaText = loginArea?.innerText?.replace(/\s+/g, ' ').trim() || '';
  const personalName = document.querySelector('.ecp_header_personalName_loginbg')?.innerText?.trim() || '';
  const notLogged = !personalName && /个人登录/.test(loginAreaText);
  if (notLogged) {
    return { error: 'not_logged_in', message: '下载需要登录。请先在 Chrome 中登录知网账号。' };
  }

  const title = document.querySelector('.brief h1')?.innerText?.trim()?.replace(/\s*网络首发\s*$/, '') || '';

  if (format === 'pdf' && pdfLink) {
    pdfLink.click();
    return { status: 'downloading', format: 'PDF', title };
  } else if (format === 'caj' && cajLink) {
    cajLink.click();
    return { status: 'downloading', format: 'CAJ', title };
  } else if (pdfLink) {
    pdfLink.click();
    return { status: 'downloading', format: 'PDF', title };
  } else if (cajLink) {
    cajLink.click();
    return { status: 'downloading', format: 'CAJ', title };
  }

  return { error: 'no_download', message: '未找到下载链接', hasPDF: !!pdfLink, hasCAJ: !!cajLink };
}
```

### 3. Report

Based on JS result:
- `status: downloading` → "PDF 下载已触发：{title}。请在 Chrome 下载管理器中查看。"
- `error: not_logged_in` → tell user to log in
- `error: captcha` → tell user to solve captcha

## Tool calls: 1–2 (browser action=open if URL + browser act kind=evaluate)

## Verified selectors

| Element | Selector | Notes |
|---------|----------|-------|
| PDF download | `#pdfDown` | `<a>` inside `li.btn-dlpdf` |
| CAJ download | `#cajDown` | `<a>` inside `li.btn-dlcaj` |
| Download area | `.download-btns` | parent `<div>` |
| Login status | `.ecp_header_login_area` / `.ecp_header_personalName_loginbg` | logged-out shows "机构登录 / 个人登录" CTA + empty name slot; logged-in shows username. `#pdfDown`/`#cajDown` exist in BOTH states — do NOT treat their presence as login |
| Title | `.brief h1` | strip trailing "网络首发" |

## Captcha detection

Check `#tcaptcha_transform_dy` element's `getBoundingClientRect().top >= 0`.
Only active when `top >= 0` (visible). Pre-loaded SDK sits at `top: -1000000px`.
