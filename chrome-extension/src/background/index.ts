import { ExtensionMessage } from '../shared/types'
import { setLatestJob } from '../shared/storage'

console.log('[ResumeRadar] Background worker started')

chrome.runtime.onInstalled.addListener(() => {
  console.log('[ResumeRadar] Extension installed')
})

chrome.runtime.onMessage.addListener(
  (message: ExtensionMessage, sender, sendResponse) => {
    console.log('[ResumeRadar] Message received:', message.type)

    if (message.type === 'JOB_DETECTED') {
      setLatestJob(message.data)
        .then(() => {
          chrome.action.setBadgeText({ text: '1', tabId: sender.tab?.id })
          chrome.action.setBadgeBackgroundColor({ color: '#534AB7' })
          sendResponse({ success: true })
        })
        .catch((error) => {
          console.error('[ResumeRadar] Failed to store job:', error)
          sendResponse({ success: false, error: error.message })
        })
      return true
    }

    if (message.type === 'CLEAR_LATEST_JOB') {
      chrome.action.setBadgeText({ text: '' })
      sendResponse({ success: true })
      return true
    }

    return false
  }
)

chrome.action.onClicked.addListener(() => {
  chrome.action.setBadgeText({ text: '' })
})