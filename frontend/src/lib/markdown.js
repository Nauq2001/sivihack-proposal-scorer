/**
 * Minimal Markdown renderer for the source pane.
 *
 * Every block it emits carries `class="b"` and `data-text` with its plain
 * text, so a citation quote can be matched against the rendered document and
 * the matching block highlighted. That is the whole reason this file exists
 * instead of a Markdown library.
 */

export function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}

/** Whitespace, dash and quote differences must not break a citation match. */
export function norm(s) {
  return String(s).toLowerCase().replace(/[–—]/g, '-').replace(/[’‘]/g, "'").replace(/\s+/g, ' ').trim()
}

export function words(s) {
  return (String(s).trim().match(/\S+/g) || []).length
}

const inline = (t) => esc(t).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/`(.+?)`/g, '<code>$1</code>')
const plain = (t) => t.replace(/\*\*|`/g, '')

export function renderMarkdown(src) {
  const lines = String(src).replace(/\r/g, '').split('\n')
  const listStart = (l) => /^(\d+\.|-)\s/.test(l)
  const blockStart = (l) => /^#{1,6}\s/.test(l) || l.startsWith('|') || listStart(l)
  let html = ''
  let i = 0

  while (i < lines.length) {
    const line = lines[i]
    if (!line.trim()) { i++; continue }

    const heading = line.match(/^(#{1,3})\s+(.*)$/)
    if (heading) {
      const level = heading[1].length
      html += `<h${level} class="b" data-text="${esc(plain(heading[2]))}">${inline(heading[2])}</h${level}>`
      i++
      continue
    }

    if (line.startsWith('|')) {
      const rows = []
      while (i < lines.length && lines[i].startsWith('|')) { rows.push(lines[i]); i++ }
      let table = '<div class="tbl"><table>'
      let first = true
      for (const row of rows) {
        if (/^\|[\s|:-]+\|?$/.test(row.trim())) continue
        const cells = row.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim())
        const tag = first ? 'th' : 'td'
        first = false
        table += `<tr class="b" data-text="${esc(plain(cells.join(' ')))}">${cells.map((c) => `<${tag}>${inline(c)}</${tag}>`).join('')}</tr>`
      }
      html += table + '</table></div>'
      continue
    }

    if (listStart(line)) {
      const ordered = /^\d+\./.test(line)
      const items = []
      while (i < lines.length && (listStart(lines[i]) || (items.length && /^\s+\S/.test(lines[i])))) {
        if (listStart(lines[i])) items.push(lines[i].replace(/^(\d+\.|-)\s+/, ''))
        else items[items.length - 1] += ' ' + lines[i].trim()
        i++
      }
      const tag = ordered ? 'ol' : 'ul'
      html += `<${tag}>${items.map((x) => `<li class="b" data-text="${esc(plain(x))}">${inline(x)}</li>`).join('')}</${tag}>`
      continue
    }

    const para = []
    while (i < lines.length && lines[i].trim() && !blockStart(lines[i])) { para.push(lines[i].trim()); i++ }
    if (!para.length) { i++; continue }
    const text = para.join(' ')
    html += `<p class="b" data-text="${esc(plain(text))}">${inline(text)}</p>`
  }

  return html
}

/** Blocks inside `root` whose text contains `quote`. */
export function findBlocks(root, quote) {
  const needle = norm(quote)
  return [...root.querySelectorAll('.b')].filter((b) => norm(b.dataset.text).includes(needle))
}
