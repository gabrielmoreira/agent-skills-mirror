/**
 * Accessible-name derivation for MediaRenderer (FRAMEWORK-AGNOSTIC). Shared by the
 * React and Angular renderers so the document-download label and the audio
 * fallback label are computed identically regardless of framework.
 *
 * The CMS media body/ref (`CmsMediaField`/`CmsExternalRef`) carries no filename
 * field and no captions-track field — only `url`. These helpers derive a label
 * from real, already-present data (the URL itself) rather than fabricating text
 * that isn't there.
 */

/** Last path segment of `url`, URL-decoded, kept only when it looks like a filename
 *  (has an extension). Returns `undefined` when `url` is absent or unparsable, or
 *  when the last segment has no extension to trust as a filename. */
function deriveFilenameFromUrl(url: string | undefined): string | undefined {
  if (!url) return undefined;
  let pathname: string;
  try {
    pathname = url.includes('://') ? new URL(url).pathname : url.split(/[?#]/)[0];
  } catch {
    return undefined;
  }
  const lastSegment = pathname.split('/').filter(Boolean).pop();
  if (!lastSegment) return undefined;
  let decoded: string;
  try {
    decoded = decodeURIComponent(lastSegment);
  } catch {
    decoded = lastSegment;
  }
  return /\.[a-zA-Z0-9]+$/.test(decoded) ? decoded : undefined;
}

/**
 * Accessible name for the document download link (WCAG 2.4.4) — identifies WHAT
 * downloads instead of a bare, ambiguous "Download". Prefers `altText`/`title`
 * when present; otherwise derives the real filename off the URL; otherwise falls
 * back to the still-more-specific-than-bare-"Download" literal `'Download file'`.
 */
export function deriveDownloadLabel(
  url: string | undefined,
  altText?: string,
  title?: string,
): string {
  if (altText) return altText;
  if (title) return title;
  const filename = deriveFilenameFromUrl(url);
  return filename ? `Download ${filename}` : 'Download file';
}

/**
 * Accessible name for an `<audio>` element when `altText` is absent. Angular's
 * `[attr.aria-label]="alt || null"` REMOVES the attribute when `alt` is falsy
 * (unlike a JSX `undefined` prop, which is the same removal but explicitly
 * intended there); this default keeps the attribute present so the control
 * always has an accessible name.
 */
export function effectiveAudioLabel(altText: string | undefined, url?: string): string {
  if (altText) return altText;
  const filename = deriveFilenameFromUrl(url);
  return filename ? `Audio: ${filename}` : 'Audio';
}
