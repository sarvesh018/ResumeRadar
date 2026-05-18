import { ExtensionMessage } from '../shared/types'
import { addJobToQueue, getPendingCount } from '../shared/storage'

console.log('[ResumeRadar] Background worker started')

async function updateBadge() {
  const count = await getPendingCount()
  if (count > 0) {
    chrome.action.setBadgeText({ text: String(count) })
    chrome.action.setBadgeBackgroundColor({ color: '#534AB7' })
  } else {
    chrome.action.setBadgeText({ text: '' })
  }
}

chrome.runtime.onInstalled.addListener(() => {
  console.log('[ResumeRadar] Extension installed')
  updateBadge()
})

updateBadge()

chrome.runtime.onMessage.addListener(
  (message: ExtensionMessage, _sender, sendResponse) => {
    console.log('[ResumeRadar] Message:', message.type)

    if (message.type === 'JOB_DETECTED') {
      addJobToQueue(message.data)
        .then((result) => {
          updateBadge()
          sendResponse({
            success: true,
            added: result.added,
            total: result.total,
          })
        })
        .catch((error) => {
          console.error('[ResumeRadar] Failed to add to queue:', error)
          sendResponse({ success: false, error: error.message })
        })
      return true
    }

    if (message.type === 'CLEAR_BADGE') {
      chrome.action.setBadgeText({ text: '' })
      sendResponse({ success: true })
      return true
    }

    if (message.type === 'GET_QUEUE_COUNT') {
      getPendingCount().then((count) => sendResponse({ count }))
      return true
    }

    return false
  }
)

chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes.job_queue) {
    updateBadge()
  }
})