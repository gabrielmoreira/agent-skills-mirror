const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'jobs.db');
const db = new Database(dbPath);

db.exec(`
  CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT UNIQUE NOT NULL,
    company_slug TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_slug) REFERENCES companies(slug)
  );
`);

function insertCompany(slug, name) {
  try {
    const stmt = db.prepare('INSERT OR IGNORE INTO companies (slug, name) VALUES (?, ?)');
    const info = stmt.run(slug, name);
    return info.changes > 0;
  } catch (err) {
    console.error(`Error inserting company ${slug}:`, err);
    return false;
  }
}

function insertJob(jobId, companySlug, title, location) {
  try {
    const stmt = db.prepare('INSERT OR IGNORE INTO jobs (job_id, company_slug, title, location) VALUES (?, ?, ?, ?)');
    const info = stmt.run(jobId, companySlug, title, location);
    return info.changes > 0;
  } catch (err) {
    console.error(`Error inserting job ${jobId}:`, err);
    return false;
  }
}

function getCompany(slug) {
  return db.prepare('SELECT * FROM companies WHERE slug = ?').get(slug);
}

function getJob(jobId) {
  return db.prepare('SELECT * FROM jobs WHERE job_id = ?').get(jobId);
}

module.exports = {
  db,
  insertCompany,
  insertJob,
  getCompany,
  getJob
};
