# Output Templates

One template per schema type. Replace every [BRACKETED_FIELD] with content extracted from the page. Never leave bracket text in the final output. If a required field is not found on the page, write `"MISSING_fieldName": "not found on page"` instead of guessing.

---

## Template: FAQPage

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[QUESTION_TEXT_1]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[ANSWER_TEXT_1]"
      }
    },
    {
      "@type": "Question",
      "name": "[QUESTION_TEXT_2]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[ANSWER_TEXT_2]"
      }
    }
  ]
}
```

Add more Question objects for each FAQ pair on the page. Minimum 2.

Worked example:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How long does shipping take?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Standard shipping takes 5-7 business days. Express shipping takes 1-2 business days."
      }
    },
    {
      "@type": "Question",
      "name": "Do you offer refunds?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. We offer full refunds within 30 days of purchase. Contact support@example.com to start a return."
      }
    }
  ]
}
```

---

## Template: Article / BlogPosting

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "[ARTICLE_TITLE]",
  "image": [
    "[ARTICLE_IMAGE_URL_16x9]"
  ],
  "datePublished": "[PUBLISH_DATE_ISO8601]",
  "dateModified": "[MODIFIED_DATE_ISO8601]",
  "author": {
    "@type": "Person",
    "name": "[AUTHOR_NAME]",
    "url": "[AUTHOR_PROFILE_URL]"
  },
  "publisher": {
    "@type": "Organization",
    "name": "[SITE_NAME]",
    "url": "[SITE_URL]",
    "logo": {
      "@type": "ImageObject",
      "url": "[LOGO_URL]"
    }
  },
  "description": "[ARTICLE_DESCRIPTION]",
  "url": "[ARTICLE_CANONICAL_URL]"
}
```

Use `"Article"` for general editorial content. Use `"BlogPosting"` for informal blog posts. Use `"NewsArticle"` for news publications.

If `dateModified` is not on the page, omit it. If author profile URL is not on the page, use just `"name"` without `"url"`.

Worked example:

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "How We Cut Our API Response Time by 60%",
  "image": [
    "https://blog.example.com/images/api-performance-16x9.jpg"
  ],
  "datePublished": "2026-03-15T09:00:00+00:00",
  "dateModified": "2026-03-18T14:30:00+00:00",
  "author": {
    "@type": "Person",
    "name": "Sarah Chen",
    "url": "https://blog.example.com/authors/sarah-chen"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Example Engineering Blog",
    "url": "https://blog.example.com",
    "logo": {
      "@type": "ImageObject",
      "url": "https://blog.example.com/logo.png"
    }
  },
  "description": "We profiled our API and found three changes that reduced p95 latency from 800ms to 320ms.",
  "url": "https://blog.example.com/posts/api-performance"
}
```

---

## Template: Organization

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "[SITE_URL]/#organization",
  "name": "[COMPANY_NAME]",
  "url": "[COMPANY_URL]",
  "logo": {
    "@type": "ImageObject",
    "url": "[LOGO_URL]",
    "width": [LOGO_WIDTH],
    "height": [LOGO_HEIGHT]
  },
  "description": "[COMPANY_DESCRIPTION]",
  "sameAs": [
    "[SOCIAL_PROFILE_URL_1]",
    "[SOCIAL_PROFILE_URL_2]"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "email": "[SUPPORT_EMAIL]"
  }
}
```

Include only social profiles and contact info that appear on the page. Omit `contactPoint` if no contact details are visible. Omit `logo` dimensions if not known.

Worked example:

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  "name": "Acme Corp",
  "url": "https://example.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://example.com/logo.png"
  },
  "description": "Acme Corp builds developer tools for API monitoring and observability.",
  "sameAs": [
    "https://www.linkedin.com/company/acme-corp",
    "https://github.com/acme-corp",
    "https://twitter.com/acmecorp"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer support",
    "email": "support@example.com"
  }
}
```

---

## Template: Product

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[PRODUCT_NAME]",
  "image": [
    "[PRODUCT_IMAGE_URL]"
  ],
  "description": "[PRODUCT_DESCRIPTION]",
  "brand": {
    "@type": "Brand",
    "name": "[BRAND_NAME]"
  },
  "offers": {
    "@type": "Offer",
    "url": "[PRODUCT_PAGE_URL]",
    "priceCurrency": "[CURRENCY_CODE]",
    "price": "[PRICE_VALUE]",
    "availability": "https://schema.org/InStock"
  }
}
```

For availability, use one of:
- `"https://schema.org/InStock"` — product is available
- `"https://schema.org/OutOfStock"` — product is not available
- `"https://schema.org/PreOrder"` — product is available for pre-order

Add `aggregateRating` only if actual ratings and review counts are visible on the page.

Worked example:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "API Monitor Pro",
  "image": [
    "https://example.com/product/api-monitor-16x9.jpg",
    "https://example.com/product/api-monitor-1x1.jpg"
  ],
  "description": "Real-time API monitoring with alerting, dashboards, and 90-day log retention.",
  "brand": {
    "@type": "Brand",
    "name": "Acme Corp"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/products/api-monitor-pro",
    "priceCurrency": "USD",
    "price": "49.00",
    "availability": "https://schema.org/InStock"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": 4.7,
    "reviewCount": 128,
    "bestRating": 5
  }
}
```

---

## Template: WebSite

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "[SITE_URL]/#website",
  "name": "[SITE_NAME]",
  "url": "[SITE_URL]",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "[SEARCH_URL_TEMPLATE]"
    },
    "query-input": "required name=search_term_string"
  }
}
```

Only include `potentialAction` if the site has a working search feature. For sites without search, use the minimal version:

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "[SITE_URL]/#website",
  "name": "[SITE_NAME]",
  "url": "[SITE_URL]"
}
```

Worked example (with search):

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://example.com/#website",
  "name": "Example",
  "url": "https://example.com",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://example.com/search?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
```

---

## Template: HowTo

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "[GUIDE_TITLE]",
  "image": "[GUIDE_FEATURE_IMAGE_URL]",
  "estimatedDuration": "[DURATION_ISO8601]",
  "step": [
    {
      "@type": "HowToStep",
      "name": "[STEP_1_TITLE]",
      "text": "[STEP_1_DESCRIPTION]"
    },
    {
      "@type": "HowToStep",
      "name": "[STEP_2_TITLE]",
      "text": "[STEP_2_DESCRIPTION]"
    }
  ]
}
```

Omit `image` if there is no feature image on the page. Omit `estimatedDuration` if no time estimate is given. Add one HowToStep object for each numbered step on the page.

Worked example:

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Set Up SSH Key Authentication",
  "estimatedDuration": "PT10M",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Generate an SSH key pair",
      "text": "Run ssh-keygen -t ed25519 -C your-email@example.com and follow the prompts."
    },
    {
      "@type": "HowToStep",
      "name": "Copy your public key to the server",
      "text": "Run ssh-copy-id user@server-address to add your public key to the server's authorized_keys file."
    },
    {
      "@type": "HowToStep",
      "name": "Test the connection",
      "text": "Run ssh user@server-address. You should connect without a password prompt."
    }
  ]
}
```

---

## Template: BreadcrumbList

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "[BREADCRUMB_1_TEXT]",
      "item": "[BREADCRUMB_1_URL]"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "[BREADCRUMB_2_TEXT]",
      "item": "[BREADCRUMB_2_URL]"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "[CURRENT_PAGE_TITLE]"
    }
  ]
}
```

The last item in the list is the current page. It does not need an `item` URL. All other items need absolute URLs.

Worked example:

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Blog",
      "item": "https://example.com/blog"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "How to Set Up SSH Key Authentication"
    }
  ]
}
```

---

## Template: SoftwareApplication

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "[APP_NAME]",
  "operatingSystem": "[OS]",
  "applicationCategory": "[CATEGORY]",
  "description": "[APP_DESCRIPTION]",
  "url": "[APP_URL]",
  "offers": {
    "@type": "Offer",
    "price": "[PRICE]",
    "priceCurrency": "[CURRENCY_CODE]"
  }
}
```

For free apps, use `"price": "0"`. For `applicationCategory`, use one of: `"GameApplication"`, `"BusinessApplication"`, `"EducationalApplication"`, `"DeveloperApplication"`, `"DesignApplication"`, `"UtilitiesApplication"`, `"SecurityApplication"`.

For `operatingSystem`, use: `"Windows"`, `"macOS"`, `"Linux"`, `"Android"`, `"iOS"`, `"Web"`. Use an array if multiple apply: `["macOS", "Windows", "Linux"]`.

Worked example:

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "API Monitor Pro",
  "operatingSystem": "Web",
  "applicationCategory": "DeveloperApplication",
  "description": "Real-time API monitoring with alerting and 90-day log retention.",
  "url": "https://example.com/products/api-monitor-pro",
  "offers": {
    "@type": "Offer",
    "price": "49.00",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": 4.7,
    "reviewCount": 128,
    "bestRating": 5
  }
}
```

---

## Template: LocalBusiness

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[BUSINESS_NAME]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[STREET_ADDRESS]",
    "addressLocality": "[CITY]",
    "addressRegion": "[STATE_OR_REGION]",
    "postalCode": "[POSTAL_CODE]",
    "addressCountry": "[COUNTRY_CODE]"
  },
  "telephone": "[PHONE_NUMBER]",
  "url": "[WEBSITE_URL]",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["[DAY_1]", "[DAY_2]"],
      "opens": "[OPENS_TIME]",
      "closes": "[CLOSES_TIME]"
    }
  ]
}
```

For `addressCountry`, use ISO 3166-1 alpha-2 codes: "US", "GB", "CA", "AU", etc.

For `dayOfWeek`, use full day names: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday".

For opening hours times, use 24-hour format: "09:00", "17:30", "22:00".

Worked example:

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Riverside Coffee",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "42 Market Street",
    "addressLocality": "Portland",
    "addressRegion": "OR",
    "postalCode": "97201",
    "addressCountry": "US"
  },
  "telephone": "+1-503-555-0142",
  "url": "https://riversidecoffee.example.com",
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "07:00",
      "closes": "18:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Saturday", "Sunday"],
      "opens": "08:00",
      "closes": "16:00"
    }
  ]
}
```

---

## Fill-in Rules

1. Replace every [BRACKETED_FIELD] with content from the page. Never use the bracket text in the final output.
2. If a required field is not on the page, write: `"MISSING_fieldName": "not found on page"`
3. If a recommended field is not on the page, omit it silently.
4. All URLs must be absolute (start with `https://`).
5. All dates must be ISO 8601 format.
6. Validate JSON syntax: no trailing commas, balanced brackets, all strings in double quotes.
7. Output each schema type as a separate `<script type="application/ld+json">` block.
