import type { ExtractedJobData } from '../shared/types'

/**
 * Tries multiple selectors and returns the first non-empty text content.
 */
function trySelectors(selectors: string[], root: Document | Element = document): string {
  for (const sel of selectors) {
    try {
      const el = root.querySelector(sel)
      if (el) {
        const text = (el as HTMLElement).innerText?.trim() || el.textContent?.trim() || ''
        if (text) return text
      }
    } catch {}
  }
  return ''
}

function extractCompany(): string {
  return trySelectors([
    '.styles_jd-header-comp-name__MvqAI a',
    '.styles_jd-header-comp-name__MvqAI',
    '.jd-header-comp-name a',
    '.jd-header-comp-name',
    'a[class*="comp-name"]',
    'div[class*="company-name"]',
    '.company-name',
    '.companyInfo .subTitle',
    '.companyInfo a',
    '[itemprop="hiringOrganization"]',
  ])
}

function extractRole(): string {
  return trySelectors([
    '.styles_jd-header-title__rZwM1',
    '.jd-header-title',
    'h1.jd-header-title',
    'h1[class*="job-title"]',
    'h1[class*="jd-title"]',
    'h1[class*="header-title"]',
    '.title.fw500',
    '.title',
    '[itemprop="title"]',
    'h1',
  ])
}

function extractLocation(): string {
  return trySelectors([
    '.styles_jhc__loc___Du2H a',
    '.styles_jhc__loc___Du2H',
    '.jhc-location',
    'span[class*="location"]',
    '.locWdth',
    '.location',
    '[itemprop="jobLocation"]',
  ])
}

function extractIsRemote(): boolean {
  const indicators = ['work from home', 'remote', 'wfh', 'home based']
  const allText = document.body.innerText.toLowerCase()
  return indicators.some(term => allText.includes(term))
}

function extractSalary(): { min?: number; max?: number } {
  const salaryText = trySelectors([
    '.styles_jhc__salary__jdfEC',
    '.salary',
    'span[class*="salary"]',
    '[itemprop="baseSalary"]',
  ])

  if (!salaryText || salaryText.toLowerCase().includes('not disclosed')) {
    return {}
  }

  const lacsMatch = salaryText.match(/(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*Lacs?/i)
  if (lacsMatch) {
    return {
      min: Math.round(parseFloat(lacsMatch[1]) * 100000),
      max: Math.round(parseFloat(lacsMatch[2]) * 100000),
    }
  }

  const numbers = salaryText.match(/[\d,]+/g)?.map(s => parseInt(s.replace(/,/g, '')))
    .filter(n => !isNaN(n) && n > 1000) || []
  if (numbers.length >= 2) {
    return { min: numbers[0], max: numbers[1] }
  }
  return {}
}

function extractJDText(): string {
  const selectors = [
    '.styles_JDC__dang-inner-html__h0K4t',
    '.styles_job-desc-container__txpYf',
    '.dang-inner-html',
    '.job-desc',
    'section[class*="job-desc"]',
    'div[class*="job-desc"]',
    'section.styles_JDC__dang-inner-html__h0K4t',
    '[itemprop="description"]',
  ]

  for (const sel of selectors) {
    const el = document.querySelector(sel)
    if (el) {
      const text = (el as HTMLElement).innerText?.trim()
      if (text && text.length > 100) return text
    }
  }

  // Last resort: find largest text block
  const sections = document.querySelectorAll('section, article, div[class*="desc"]')
  let largest = ''
  sections.forEach(section => {
    const text = (section as HTMLElement).innerText?.trim() || ''
    if (text.length > largest.length && text.length > 200 && text.length < 50000) {
      largest = text
    }
  })
  return largest
}

export function extractNaukriJob(): ExtractedJobData | null {
  const company = extractCompany()
  const role_title = extractRole()
  const jd_text = extractJDText()

  if (!company || !role_title) {
    console.warn('[ResumeRadar] Could not extract company or role')
    return null
  }

  const salary = extractSalary()

  return {
    company,
    role_title,
    jd_text: jd_text || `Job at ${company} for ${role_title}. Full description not extracted.`,
    jd_url: window.location.href,
    location: extractLocation() || undefined,
    is_remote: extractIsRemote(),
    salary_min: salary.min,
    salary_max: salary.max,
    source: 'naukri',
    extracted_at: new Date().toISOString(),
  }
}