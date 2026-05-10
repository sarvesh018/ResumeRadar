import { startNaukriDetection } from './apply-detector'

if (window.location.hostname.includes('naukri.com')) {
  console.log('[ResumeRadar] Loaded on Naukri:', window.location.href)
  startNaukriDetection()
}