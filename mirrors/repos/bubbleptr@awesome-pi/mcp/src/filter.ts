export type Searchable = { searchText: string; categories: string[]; kind: string };
export type Filters = { q: string; category: string };

/** Same AND match as the Pi Index directory (`site/src/lib/filter.ts` `matchesResource`). */
export function matchesResource(resource: Searchable, filters: Filters): boolean {
  if (filters.category !== 'all' && resource.kind !== filters.category && !resource.categories.includes(filters.category)) return false;
  const haystack = resource.searchText.normalize('NFKC').toLowerCase();
  return filters.q.normalize('NFKC').trim().toLowerCase().split(/\s+/).every(term => haystack.includes(term));
}

/** Same query string the directory copies into the address bar. */
export function directoryLink(q = '', category = 'all'): string {
  const params = new URLSearchParams();
  if (q.trim()) params.set('q', q.trim());
  if (category !== 'all') params.set('category', category);
  const query = params.toString();
  return query ? `https://piindex.dev/?${query}` : 'https://piindex.dev/';
}
