const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, 'jobs.db');
const db = new Database(dbPath);

const query = `
  SELECT 
    c.name as company_name,
    c.slug as company_slug,
    GROUP_CONCAT(j.title, ' | ') as matching_roles
  FROM jobs j 
  JOIN companies c ON j.company_slug = c.slug 
  WHERE 
    j.title LIKE '%GTM%' OR 
    j.title LIKE '%DevRel%' OR 
    j.title LIKE '%Growth%' OR 
    j.title LIKE '%Content%' OR 
    j.title LIKE '%Marketing%' OR
    j.title LIKE '%Developer Advocate%' OR
    j.title LIKE '%Community%'
  GROUP BY c.slug, c.name
`;

const rows = db.prepare(query).all();

const candidates = rows.map(row => ({
  company_name: row.company_name,
  company_slug: row.company_slug,
  yc_url: `https://www.ycombinator.com/companies/${row.company_slug}`,
  matching_roles: row.matching_roles
}));

fs.writeFileSync(
  path.join(__dirname, 'radar_candidates.json'), 
  JSON.stringify(candidates, null, 2)
);

console.log(`Found ${candidates.length} unique candidate companies hiring for target roles! Saved to radar_candidates.json`);
