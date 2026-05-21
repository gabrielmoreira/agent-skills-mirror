const { chromium } = require('playwright');
const fs = require('fs');
const db = require('./db');

const QUERY_URLS = [
  'https://www.workatastartup.com/companies?companySize=seed&demographic=any&hasEquity=any&hasSalary=any&industry=B2B%20Software%20and%20Services&interviewProcess=any&jobType=fulltime&layout=list-compact&query=GTM&role=marketing&role=sales&sortBy=keyword&tab=any&usVisaNotRequired=any',
  'https://www.workatastartup.com/companies?companySize=seed&demographic=any&hasEquity=any&hasSalary=any&industry=B2B%20Software%20and%20Services&interviewProcess=any&jobType=fulltime&layout=list-compact&query=Growth&role=sales&role=marketing&sortBy=keyword&tab=any&usVisaNotRequired=any',
  'https://www.workatastartup.com/companies?companySize=seed&demographic=any&hasEquity=any&hasSalary=any&industry=B2B%20Software%20and%20Services&interviewProcess=any&jobType=fulltime&layout=list-compact&query=Founding%20GTM&role=sales&role=marketing&sortBy=keyword&tab=any&usVisaNotRequired=any',
  'https://www.workatastartup.com/companies?companySize=seed&demographic=any&hasEquity=any&hasSalary=any&industry=B2B%20Software%20and%20Services&interviewProcess=any&jobType=fulltime&layout=list-compact&query=DevRel&role=sales&role=marketing&sortBy=keyword&tab=any&usVisaNotRequired=any',
  'https://www.workatastartup.com/companies?companySize=seed&demographic=any&hasEquity=any&hasSalary=any&industry=B2B%20Software%20and%20Services&interviewProcess=any&jobType=fulltime&layout=list-compact&query=creator&role=sales&role=marketing&sortBy=keyword&tab=any&usVisaNotRequired=any'
];

async function extractCompaniesFromQuery(page, url) {
  console.log(`Scraping query URL: ${url.substring(0, 100)}...`);
  await page.goto(url, { waitUntil: 'networkidle' });

  // Wait specifically for the element that contains the data-page attribute
  try {
    await page.waitForSelector('[data-page]', { timeout: 10000 });
  } catch (e) {
    console.log("Timeout waiting for [data-page]. Page might have failed to load or requires auth.");
  }

  const companies = await page.evaluate(() => {
    // Some inertia apps use #app, but let's just find anything with data-page
    const appDiv = document.querySelector('[data-page]');
    if (!appDiv) {
        console.log("CRITICAL: No element with data-page found on the page!");
        return [];
    }
    
    try {
      const data = JSON.parse(appDiv.dataset.page);
      
      console.log("DATA KEYS:", Object.keys(data));
      if (data.props) console.log("PROPS KEYS:", Object.keys(data.props));
      if (data.props && data.props.initialState) console.log("INITIAL STATE KEYS:", Object.keys(data.props.initialState));
      
      const results = [];
      const extractedSlugs = new Set();
      
      // Let's try to grab from JSON first (the robust way)
      if (data && data.props && data.props.companies) {
         // Usually it's an array or a paginated object
         const comps = Array.isArray(data.props.companies) ? data.props.companies : (data.props.companies.results || data.props.companies.data || []);
         for (const c of comps) {
             if (c.slug) {
                 extractedSlugs.add(c.slug);
                 results.push({ slug: c.slug, name: c.name || c.slug });
             }
         }
      }

      // Fallback: If JSON extraction fails, scrape the DOM links
      if (results.length === 0) {
          const links = document.querySelectorAll('a[href^="/companies/"]');
          links.forEach(link => {
            const href = link.getAttribute('href');
            const parts = href.split('/');
            if (parts.length >= 3 && parts[1] === 'companies') {
              const slug = parts[2];
              // Ignore standard routes that aren't company slugs
              if (!['edit', 'new', 'search'].includes(slug) && !extractedSlugs.has(slug)) {
                extractedSlugs.add(slug);
                results.push({ slug, name: slug });
              }
            }
          });
      }
      
      return results;
    } catch (e) {
      console.error("Error parsing data-page:", e);
      return [];
    }
  });
  
  return companies;
}

async function scrapeCompanyJobs(page, company) {
  console.log(`Scraping jobs for company: ${company.slug}`);
  const internalUrl = `https://www.workatastartup.com/companies/${company.slug}`;
  
  try {
    // === METHOD 1: Try authenticated JSON extraction first (Most Reliable) ===
    await page.goto(internalUrl, { waitUntil: 'networkidle' });
    
    try {
      await page.waitForSelector('[data-page]', { timeout: 8000 });
      
      const internalJobs = await page.evaluate(() => {
        const appDiv = document.querySelector('[data-page]');
        if (!appDiv) return null;
        
        try {
          const data = JSON.parse(appDiv.dataset.page);
          const companyData = data.props.company || data.props.rawCompany || {};
          const jobsList = companyData.jobs || [];
          
          if (jobsList.length > 0) {
            return jobsList.map(job => ({
              id: job.id ? String(job.id) : null,
              title: job.title || '',
              location: job.location || ''
            }));
          }
        } catch (e) {
          return null;
        }
        return null;
      });

      if (internalJobs && internalJobs.length > 0) {
        return internalJobs;
      }
    } catch (e) {
      console.log(`  -> Internal JSON extraction failed for ${company.slug}, attempting public fallback...`);
    }

    // === METHOD 2: Fallback to public HTML extraction (User's Idea) ===
    const publicUrl = `https://www.ycombinator.com/companies/${company.slug}/jobs`;
    const response = await page.goto(publicUrl, { waitUntil: 'networkidle' });
    
    if (response && response.status() === 404) {
      console.log(`  -> No public jobs page found for ${company.slug}`);
      return [];
    }

    const publicJobs = await page.evaluate(() => {
      const jobCards = Array.from(document.querySelectorAll('.flex.w-full.flex-row.justify-between'));
      const parsedJobs = [];

      for (let i = 0; i < jobCards.length; i++) {
        const card = jobCards[i];
        const titleEl = card.querySelector('.font-bold');
        const title = titleEl ? titleEl.textContent.trim() : null;

        if (title) {
          const detailsEl = card.querySelectorAll('div > span');
          let location = "Unknown";
          
          if (detailsEl.length > 0) {
            location = detailsEl[0].textContent.trim();
          }

          parsedJobs.push({
            id: `yc_${Date.now()}_${i}_${title.replace(/\s+/g, '_')}`,
            title: title,
            location: location
          });
        }
      }
      return parsedJobs;
    });

    return publicJobs;

  } catch (error) {
    console.error(`Error scraping jobs for ${company.slug}:`, error.message);
    return [];
  }
}

async function runScraper() {
  if (!fs.existsSync('state.json')) {
    console.error('ERROR: state.json not found. Please run auth.js first to log in.');
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ storageState: 'state.json' });
  const page = await context.newPage();

  const allFoundCompanies = new Map();

  for (const url of QUERY_URLS) {
    const companies = await extractCompaniesFromQuery(page, url);
    for (const c of companies) {
      if (!allFoundCompanies.has(c.slug)) {
        allFoundCompanies.set(c.slug, c);
      }
    }
  }

  console.log(`Found ${allFoundCompanies.size} unique companies across all queries.`);

  let newCompaniesCount = 0;
  let newJobsCount = 0;

  for (const [slug, company] of allFoundCompanies) {
    const isNewCompany = db.insertCompany(slug, company.name);
    if (isNewCompany) newCompaniesCount++;

    const jobs = await scrapeCompanyJobs(page, company);
    
    for (const job of jobs) {
      if (job.id && job.title) {
        const isNewJob = db.insertJob(job.id, slug, job.title, job.location);
        if (isNewJob) {
          console.log(`[NEW JOB] ${slug} - ${job.title} (${job.location})`);
          newJobsCount++;
        }
      }
    }
    
    await page.waitForTimeout(1000);
  }

  console.log('--- SCRAPE COMPLETE ---');
  console.log(`New Companies Added: ${newCompaniesCount}`);
  console.log(`New Jobs Found: ${newJobsCount}`);

  await browser.close();
}

runScraper().catch(console.error);
