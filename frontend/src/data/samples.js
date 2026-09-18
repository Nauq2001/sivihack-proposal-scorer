/** RFP và 4 proposal mẫu của BTC, kèm kết quả đã lưu cho từng bản.
 *  Các file JSON là dữ liệu mẫu của hợp đồng /api/review — xem
 *  docs/api/review-contract.md. App dùng chúng khi backend chưa chạy. */

import rfpText from '../samples/rfp_nordframe.md?raw'
import weakText from '../samples/response_1_weak.md?raw'
import mediumText from '../samples/response_2_medium.md?raw'
import strongText from '../samples/response_3_strong.md?raw'
import overText from '../samples/response_4_overpromise.md?raw'

import weakResult from '../mocks/response_1_weak.json'
import mediumResult from '../mocks/response_2_medium.json'
import strongResult from '../mocks/response_3_strong.json'
import overResult from '../mocks/response_4_overpromise.json'

import { norm } from '../lib/markdown.js'

export const RFP = { name: 'rfp_nordframe.md', text: rfpText }

export const SAMPLES = [
  { id: 'weak', chip: 'Weak', label: 'BrightPath', name: 'response_1_weak.md', text: weakText, result: weakResult },
  { id: 'medium', chip: 'Medium', label: 'Clarion', name: 'response_2_medium.md', text: mediumText, result: mediumResult },
  { id: 'strong', chip: 'Strong', label: 'Fernglow', name: 'response_3_strong.md', text: strongText, result: strongResult },
  { id: 'over', chip: 'Overpromising', label: 'Vantix', name: 'response_4_overpromise.md', text: overText, result: overResult },
]

export const sampleById = (id) => SAMPLES.find((s) => s.id === id)

/** Mẫu còn nguyên văn, nên kết quả đã lưu vẫn đúng với nó. */
export function matchSample(rfp, proposal) {
  if (norm(rfp) !== norm(RFP.text)) return null
  return SAMPLES.find((s) => norm(s.text) === norm(proposal)) || null
}
