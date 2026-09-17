/** The fictional RFP and proposals from the sponsor, plus the reviewed output
 *  for each one. The JSON files are the contract samples in
 *  docs/api/review-contract.md — the app falls back to them when the scoring
 *  service isn't running. */

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
  { id: 'weak', label: 'Response 1: BrightPath (weak)', name: 'response_1_weak.md', text: weakText, result: weakResult },
  { id: 'medium', label: 'Response 2: Clarion (medium)', name: 'response_2_medium.md', text: mediumText, result: mediumResult },
  { id: 'strong', label: 'Response 3: Fernglow (strong)', name: 'response_3_strong.md', text: strongText, result: strongResult },
  { id: 'over', label: 'Response 4: Vantix (overpromising)', name: 'response_4_overpromise.md', text: overText, result: overResult },
]

export const sampleById = (id) => SAMPLES.find((s) => s.id === id)

/** A sample whose text is still unedited, so its stored result still applies. */
export function matchSample(rfp, proposal) {
  if (norm(rfp) !== norm(RFP.text)) return null
  return SAMPLES.find((s) => norm(s.text) === norm(proposal)) || null
}
