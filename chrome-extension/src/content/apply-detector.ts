import { extractNaukriJob } from './naukri-extractor'
import type { ExtensionMessage } from '../shared/types'

let lastDetectionTime = 0
const DEBOUNCE_MS = 2000

function isApplyButton(element: Element): boolean {
  if (!element) return false
  const tag = element.tagName?.toLowerCase()
  if (tag !== 'button' && tag !== 'a' && tag !== 'span' && tag !== 'div') return false

  const text = ((element as HTMLElement).innerText || element.textContent || '').toLowerCase().trim()
  const className = (element.className || '').toString().toLowerCase()
  const id = (element.id || '').toLowerCase()
  const ariaLabel = element.getAttribute('aria-label')?.toLowerCase() || ''

  const applyTexts = [
    'apply', 'easy apply', 'apply now', 'quick apply',
    "i'm interested", 'apply on company site', 'register & apply',
  ]

  const textMatches = applyTexts.some(t => text === t || text.startsWith(t))
  const classMatches = (
    className.includes('apply-button') ||
    className.includes('apply-btn') ||
    className.includes('applybutton') ||
    className.includes('btn-apply') ||
    id.includes('apply') ||
    ariaLabel.includes('apply')
  )

  return textMatches || classMatches
}

function findApplyAncestor(element: Element | null): Element | null {
  let current: Element | null = element
  let depth = 0
  while (current && depth < 5) {
    if (isApplyButton(current)) return current
    current = current.parentElement
    depth++
  }
  return null
}

function handleClick(event: MouseEvent) {
  const target = event.target as Element
  if (!target) return

  const applyButton = findApplyAncestor(target)
  if (!applyButton) return

  const now = Date.now()
  if (now - lastDetectionTime < DEBOUNCE_MS) return
  lastDetectionTime = now

  console.log('[ResumeRadar] Apply button clicked:', applyButton)

  setTimeout(() => {
    const jobData = extractNaukriJob()

    if (!jobData) {
      console.warn('[ResumeRadar] No job data extracted')
      showInPageNotification('Could not extract job details. Try opening the full job page first.', 'error')
      return
    }

    console.log('[ResumeRadar] Extracted job:', jobData)

    const message: ExtensionMessage = { type: 'JOB_DETECTED', data: jobData }
    chrome.runtime.sendMessage(message, (response) => {
      if (chrome.runtime.lastError) {
        console.error('[ResumeRadar] Message failed:', chrome.runtime.lastError)
        return
      }
      if (response?.success) {
        showInPageNotification(
          `Captured: ${jobData.role_title} at ${jobData.company}. Click the ResumeRadar icon to match & save.`,
          'success'
        )
      }
    })
  }, 200)
}

function showInPageNotification(message: string, type: 'success' | 'error') {
  const existing = document.getElementById('resumeradar-notification')
  if (existing) existing.remove()

  const colors = {
    success: { bg: '#534AB7', text: '#FFFFFF' },
    error: { bg: '#DC2626', text: '#FFFFFF' },
  }

  const div = document.createElement('div')
  div.id = 'resumeradar-notification'
  div.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${colors[type].bg};
    color: ${colors[type].text};
    padding: 12px 18px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 999999;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 13px;
    max-width: 360px;
    line-height: 1.4;
    animation: rr-slide-in 0.3s ease-out;
  `

  if (!document.getElementById('rr-styles')) {
    const style = document.createElement('style')
    style.id = 'rr-styles'
    style.textContent = `
      @keyframes rr-slide-in {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    `
    document.head.appendChild(style)
  }

  div.innerHTML = `
    <div style="font-weight: 600; margin-bottom: 4px;">ResumeRadar</div>
    <div>${message}</div>
  `

  document.body.appendChild(div)

  setTimeout(() => {
    div.style.transition = 'opacity 0.3s'
    div.style.opacity = '0'
    setTimeout(() => div.remove(), 300)
  }, 6000)
}

export function startNaukriDetection() {
  console.log('[ResumeRadar] Naukri detection started')
  document.addEventListener('click', handleClick, true)
}