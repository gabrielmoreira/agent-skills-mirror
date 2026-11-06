---
name: real-registration
description: Use when user says "register", "sign up", "create account", "အကောင့်ဖွင့်", "ဖွင့်လိုက်", "အကောင့်လုပ်", "ဖောက်". Creates accounts with perfect attribution cover - matching cover country names, locale-aware behavior, human-like typing/mouse patterns, and consistent backstory across all created profiles.
---

# Realistic Account Registration

## TRIGGER RULES
Activate when user says: "အကောင့်ဖွင့်", "register", "sign up", "အကောင့်လုပ်", "ဖောက်", "ဖွင့်လိုက်"

---

## TARGET LOCALE ADAPTATION

**BEFORE registering**, determine the target locale:
- What country/language is the target site from?
- What names are common there?
- What timezone and language do locals use?
- Generate names matching that locale, NOT your own region

---

## 🚨 CRITICAL: ATTRIBUTION COVER FOR ACCOUNTS

Every account you create is evidence. If the target or a 3rd party analyzes these accounts, they must find ZERO connection to the operator's origin country.

### Account Attribution Rules:
```yaml
❌ NEVER:
  - Use origin-country names (even as middle names or fake names)
  - Use origin-country email patterns or origin ccTLD
  - Set account language to the origin language
  - Use origin-country phone numbers
  - Set timezone to the origin timezone
  - Fill profile with origin-country locations, education, or work
  - Upload profile photos that can be reverse-image searched to the origin
  - Use origin-country cultural references
  - Send emails/support tickets during origin day time (if using a different cover)
  - Write in the origin language in any account communication
  - Connect social media accounts that have origin-country connections

✅ ALWAYS:
  - Use names from the COVER COUNTRY (or target country)
  - Set profile language to cover country
  - Set timezone to cover country
  - Use realistic cover-country address (use Google Maps - real street exists)
  - Fill profile with consistent cover-country details
  - Upload generic profile photos (AI-generated faces are best)
  - Send communications during cover country working hours
  - Write in cover country language and dialect
  - Create backstory consistent with cover identity
```

### The Cover Identity Backstory:
```yaml
Before creating ANY account, define:
  Name: _____________ (from cover country)
  DOB: _____________ (consistent age range)
  Email: ___________ (cover country provider)
  Location: _________ (real city in cover country)
  Occupation: _______ (matches education/age)
  Interests: ________ (vague, doesn't conflict with cover)
  Social Media: _____ (clean, no origin links, no real friends)
```

---

## CRITICAL: BEHAVIOR MIMICRY RULES

When registering, NEVER act like a bot. Follow these rules strictly:

### 1. Realistic Naming
Use names matching the **target's locale**, not your own.

**Generic Western names (for English-language targets):**
```
Male: James, Robert, Michael, David, William, Richard, Joseph, Thomas, Christopher, Daniel
      Paul, Mark, Donald, Kenneth, Steven, Andrew, Edward, Brian, Kevin, Jason
Female: Mary, Patricia, Jennifer, Linda, Barbara, Elizabeth, Susan, Jessica, Sarah, Karen
        Lisa, Nancy, Betty, Margaret, Sandra, Ashley, Dorothy, Kimberly, Emily, Donna
Last: Smith, Johnson, Williams, Brown, Jones, Garcia, Miller, Davis, Rodriguez, Martinez
      Hernandez, Lopez, Gonzalez, Wilson, Anderson, Thomas, Taylor, Moore, Jackson, Martin
```

**For non-English targets** (Europe, Asia, etc.), research common names from that country before creating.

**Name formats (match target locale):**
- English: `First Last` (John Smith), `F. Last` (J. Smith)
- European: adjust for local conventions (two surnames, middle names)
- Asian: match local format (FamilyName GivenName or GivenName FamilyName)

### 2. Realistic Emails
Match email patterns used in **target's country/region**:
- Global common: `firstname.lastname123@gmail.com`
- Company email: `firstname.lastname@company.com`
- Local provider: use country-specific email providers (not just Gmail)
- Birth year: `first.last1990@gmail.com`

Add random numbers (NOT sequential) to avoid patterns.
When filling forms via browser:
- **Add random delays** between keystrokes (50-250ms)
- **Type first few characters**, pause briefly, continue
- **Occasionally delete and retype** 1-2 characters (human error simulation)
- **Pause longer** before typing email (people look at keyboard for `@`)
- **Pause 2-4 seconds** before clicking submit (reading/reviewing)

### 4. Mouse Behavior
- **Move mouse to each field** before clicking (don't tab-jump)
- **Scroll page slightly** after filling, then scroll back
- **Hover over submit button** briefly before clicking
- **Random mouse paths** - not straight lines between fields

### 5. Browser Fingerprint
- Use realistic `window.navigator` properties
- Set realistic screen resolution: `1366x768`, `1920x1080`, `1440x900`, `1536x864`
- Set language to **target country's primary language** (e.g., `en-US`, `ja-JP`, `th-TH`, `vi-VN`)
- Timezone: **target country's timezone** (e.g., `America/New_York`, `Asia/Tokyo`, `Europe/London`)
- Use Chrome user agent matching target audience

### 6. Password Generation
Match target region's common password patterns:
- Common pattern worldwide: capital letter + lowercase + number + symbol
- 8-12 characters (matches most site requirements)
- Avoid overly complex passwords (real users don't use `&2hG#9mP!`)
- Use realistic patterns: `NameYear!`, `Name123!`, `Name@2024`

---

## REGISTRATION WORKFLOW

### Step 1: Pre-Registration Recon
Before registering, check:
- What fields are required? (name, email, password, confirm password)
- Is there CAPTCHA? (presence = more careful)
- Any hidden fields? (`role`, `plan`, `is_admin`)
- Password requirements shown? (min length, special chars)
- What happens on success? (redirect to /login? to /ai? show toast?)

### Step 2: Generate Identity
```javascript
// Generate random but realistic identity (match target locale)
const locale = "TARGET_COUNTRY"; // ← SET THIS per target
const firstNames = getNamesForLocale(locale); // Research target country names
const lastNames = getLastNamesForLocale(locale); // Research target country last names
const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}${Math.floor(Math.random()*900)+100}@gmail.com`;
const password = `${firstName}${Math.floor(Math.random()*10000)}!`;
```

### Step 3: Browser Registration
Use Playwright/MCP browser, NOT curl:
- Navigate to `/register`
- Wait 3-5 seconds (reading page)
- Fill fields with human-like delays
- Scroll the page at least once
- Submit and wait for response

### Step 4: Post-Registration
- Check what page redirects to
- Check if email verification is required
- Check if welcome email/notification appears
- Check what cookies are set (especially session tokens)

### Step 5: Identity Storage
Save the created identity:
```
Email: xxx
Password: xxx
Session Cookie: xxx
Profile URL: xxx
```

---

## RATE LIMIT HANDLING

If 429 received:
- **Never retry immediately** from same IP
- Wait exactly 60 seconds minimum
- **Switch approach**: use Google OAuth instead if available
- **Switch network**: if possible, change IP (VPN, mobile hotspot)
- **Test rate limit bypass**: different endpoint, different HTTP method, add headers
- **Test if rate limit is endpoint-specific**: can you hit `/api/auth/login` while `/api/auth/register` is blocked?

---

## DETECTION EVASION

### Patterns to AVOID (these get flagged):
- ❌ Sequential account numbers (test1, test2, test3)
- ❌ Same password across accounts
- ❌ mailinator/yopmail domains (use gmail.com)
- ❌ Rapid fire registrations (<2 seconds between)
- ❌ Tab-jumping between fields (no mouse movement)
- ❌ Exact same User-Agent every time
- ❌ Same screen resolution every time
- ❌ Identical timing patterns

### Patterns to USE:
- ✅ Different browsers/User-Agents per session
- ✅ Different screen resolutions
- ✅ Variable delays (800ms to 5000ms between actions)
- ✅ Realistic names matching target locale
- ✅ Different Gmail addresses each time
- ✅ Wait 30-120 seconds between registrations
- ✅ Browse other pages before/after registration
