// The script every book in this repository shares: sidebar, contents, previous/next, tabs, the "From the books"
// pop-ups, lab numbers and diagram colours. Plain script, no modules, so a page works when opened straight from disk.
//
// A page loads, in this order: its book's data files (book-refs.js, lab-data.js),
// this file, then its book's own assets/book.js. That last file calls startBook() with the book's chapter list
// and then draws whatever only that book has.

const here = decodeURIComponent(location.pathname.split("/").pop()) || "index.html";

// A chapter as a link, or as greyed text while it is not written yet. Numbered files show their number.
function chapterEntry(c) {
  const n = /^\d\d-/.test(c.file) ? Number(c.file.slice(0, 2)) : 0;
  const title = (n ? `<span class="num">${n}</span>` : "") + c.title;
  if (!c.ready) return `<span class="soon">${title}</span>`;
  const current = c.file === here ? ' aria-current="page"' : "";
  return `<a href="${c.file}"${current}>${title}</a>`;
}

// The chapter list grouped by part; `partClass(part)` gives each part its colour class.
function chapterList(book) {
  const parts = [...new Set(book.chapters.map((c) => c.part))];
  return parts
    .map((part) => {
      const items = book.chapters.filter((c) => c.part === part).map((c) => `<li>${chapterEntry(c)}</li>`);
      return `<section class="${book.partClass(part)}"><h2>${part}</h2><ul>${items.join("")}</ul></section>`;
    })
    .join("");
}

// book = { title: "HTML for the sidebar", chapters: [{ file, part, title, ready }], partClass, ideas: ["model", ...] }
function startBook(book) {
  const sidebar = document.getElementById("sidebar");
  if (sidebar) sidebar.innerHTML = `<a class="book-title" href="index.html">${book.title}</a>${chapterList(book)}`;

  const contents = document.getElementById("contents");
  if (contents) contents.innerHTML = chapterList(book);

  const index = book.chapters.findIndex((c) => c.file === here);
  const pager = document.getElementById("pager");
  if (index >= 0 && pager) {
    const prev = book.chapters.slice(0, index).reverse().find((c) => c.ready);
    const next = book.chapters.slice(index + 1).find((c) => c.ready);
    pager.innerHTML =
      (prev ? `<a class="prev" href="${prev.file}">← ${prev.title}</a>` : "<span></span>") +
      (next ? `<a class="next" href="${next.file}">${next.title} →</a>` : "<span></span>");
  }

  showLabNumbers();
  startTabs();
  startRefCards();
  startFilter();
  startCanvases();
}

// Type-to-filter: <input id="filter"> hides what does not match in #terms (a table's rows after the header,
// or the .qa question cards of an interview page), and <p id="count"> says how many are shown.
// data-noun on #terms names what is counted ("terms" by default). Pages without these elements are left alone.
function startFilter() {
  const filter = document.getElementById("filter"), table = document.getElementById("terms");
  if (!filter || !table) return;
  const rows = table.tagName === "TABLE" ? [...table.querySelectorAll("tr")].slice(1) : [...table.querySelectorAll(".qa")];
  const count = document.getElementById("count");
  const apply = () => {
    const text = filter.value.trim().toLowerCase();
    let shown = 0;
    rows.forEach((row) => {
      const match = row.textContent.toLowerCase().includes(text);
      row.hidden = !match;
      shown += match;
    });
    if (count) count.textContent = `${shown} of ${rows.length} ${table.dataset.noun || "terms"}`;
  };
  filter.addEventListener("input", apply);
  apply();
}

// Lab numbers: <span data-lab="latency.total.p95"></span> shows that value from the book's assets/lab-data.js.
// shared/tools/check.py makes sure every path exists, so no number on a page is typed by hand.
function showLabNumbers() {
  if (typeof LAB === "undefined") return; // a top-level const is not a property of window
  document.querySelectorAll("[data-lab]").forEach((el) => {
    const value = el.dataset.lab.split(".").reduce((v, key) => (v == null ? undefined : v[key]), LAB);
    el.textContent = typeof value === "number" ? value.toLocaleString("en-US", { maximumFractionDigits: 5 }) : String(value);
  });
}

// Tabs: buttons with aria-controls pointing at panels. Without this script every panel simply shows.
// A link ending in #systems opens that tab.
function startTabs() {
  document.querySelectorAll(".tabs").forEach((tabs) => {
    const buttons = [...tabs.querySelectorAll("[role=tab]")];
    const panels = buttons.map((button) => document.getElementById(button.getAttribute("aria-controls")));
    const show = (wanted) => {
      buttons.forEach((button, i) => {
        button.setAttribute("aria-selected", String(i === wanted));
        panels[i].hidden = i !== wanted;
      });
    };
    buttons.forEach((button, i) =>
      button.addEventListener("click", () => {
        show(i);
        history.replaceState(null, "", "#" + panels[i].id);
        tabs.scrollIntoView({ block: "start" });
      }),
    );
    show(Math.max(0, panels.findIndex((panel) => "#" + panel.id === location.hash)));
  });
}

// "From the books": each card opens a pop-up built from BOOK_REFS (the book's assets/book-refs.js).
// It shows what the book chapter covers, what the sections behind this page say, and when to read it.
function startRefCards() {
  if (typeof BOOK_REFS === "undefined") return;
  const dialog = document.createElement("dialog");
  dialog.className = "ref-dialog";
  document.body.append(dialog);
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog || event.target.closest(".close")) dialog.close(); // the backdrop, or the button
  });

  document.querySelectorAll(".ref-card").forEach((card) => {
    card.addEventListener("click", () => {
      const [bookKey, chapter] = card.dataset.ref.split("-");
      const source = BOOKS[bookKey];
      const ref = BOOK_REFS[card.dataset.ref];
      const cited = (card.dataset.sections || "").split("|").filter((title) => ref.sections[title]);
      const sections = cited.map((title) => `<dt>${title}</dt><dd>${ref.sections[title]}</dd>`).join("");
      dialog.className = `ref-dialog ref-${bookKey}`;
      dialog.innerHTML = `
        <header>
          <div><p>${source.title}</p><h3>Chapter ${chapter}: ${ref.chapter}</h3><small>${source.authors}</small></div>
          <button type="button" class="close">Close</button>
        </header>
        <div class="body">
          <p>${ref.about}</p>
          ${sections ? `<h4>The sections behind this page</h4><dl>${sections}</dl>` : ""}
          <h4>The chapter's main ideas</h4>
          <ul>${ref.ideas.map((idea) => `<li>${idea}</li>`).join("")}</ul>
          <div class="callout"><p><strong>Read it when:</strong> ${ref.read_when}</p></div>
        </div>`;
      dialog.showModal();
    });
  });
  // A link ending in #ref-2 opens the second card's pop-up straight away.
  const wanted = location.hash.match(/^#ref-(\d+)$/);
  if (wanted) document.querySelectorAll(".ref-card")[wanted[1] - 1]?.click();
}

// ---------- The system canvas ----------
// <figure class="canvas"> holds its diagram as JSON in a <script type="application/json">:
//   { "cols": 5, "still": true (no travelling dots),
//     "nodes": [{ "id", "col", "row", "icon", "title", "sub", "kind", "tag", "shape": "gate" | "end", "span" }],
//     "edges": [{ "from", "to", "label", "at", "type": "main" | "alt" | "fail", "via": "top" | "bottom" | "down" }],
//     "lanes": [{ "label", "kind", "nodes": ["id", ...] }] }
// Cards sit on a CSS grid; the links are drawn after layout as curves, and redrawn when the size changes.
// Line icons, drawn for these books (24 x 24, stroke only).
const ICONS = {
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"/>',
  lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
  shield: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
  route: '<path d="M12 3v18"/><path d="M5 5h10l3 3-3 3H5z"/><path d="M19 13H9l-3 3 3 3h10z"/>',
  bolt: '<path d="M13 3L5 14h6l-1 7 8-11h-6z"/>',
  search: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
  spark: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>',
  gateway: '<rect x="3" y="7" width="18" height="10" rx="3"/><path d="M7 12h10M14 9l3 3-3 3"/>',
  doc: '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
  db: '<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/><path d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3"/>',
  queue: '<rect x="4" y="4" width="16" height="4" rx="1.5"/><rect x="4" y="10" width="16" height="4" rx="1.5"/><rect x="4" y="16" width="16" height="4" rx="1.5"/>',
  clock: '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
  check: '<path d="M5 12l5 5 9-10"/>',
  alert: '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17v.5"/>',
  sync: '<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v5h-5"/>',
  gate: '<path d="M12 3l9 9-9 9-9-9z"/><path d="M10 10a2 2 0 1 1 2.5 2c-.4.2-.5.5-.5 1M12 15.5v.5"/>',
  stream: '<path d="M4 7h16M4 12h11M4 17h14"/>',
  swap: '<path d="M4 8h14l-3-3M20 16H6l3 3"/>',
  org: '<circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M12 7v5M12 12l-6 5M12 12l6 5"/>',
  eval: '<rect x="6" y="4" width="12" height="17" rx="2"/><path d="M9 4h6v3H9z"/><path d="M9 14l2 2 4-4"/>',
  code: '<path d="M8 8l-4 4 4 4M16 8l4 4-4 4"/>',
  moon: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
  key: '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3"/>',
  pulse: '<path d="M3 12h4l2-5 3 10 3-8 2 3h4"/>',
};
const SVG_NS = "http://www.w3.org/2000/svg";
const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;

function renderCanvas(figure) {
  const spec = JSON.parse(figure.querySelector("script[type='application/json']").textContent);
  const inner = document.createElement("div");
  inner.style.cssText = "position: relative; width: max-content; min-width: 100%;";
  const grid = document.createElement("div");
  grid.className = "canvas-grid";
  grid.style.gridTemplateColumns = `repeat(${spec.cols}, auto)`;
  const cards = {};
  for (const n of spec.nodes) {
    const card = document.createElement("div");
    card.className = `cnode ${n.kind || "plain"}${n.shape ? " " + n.shape : ""}`;
    card.style.gridColumn = n.col;
    card.style.gridRow = n.span ? `${n.row} / span ${n.span}` : n.row; // a decision can sit across two rows
    card.innerHTML = `<span class="chip"><svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[n.icon] || ICONS.doc}</svg></span>` +
      `<b>${n.title}</b>${n.sub ? `<small>${n.sub}</small>` : ""}${n.tag ? `<span class="tag">${n.tag}</span>` : ""}`;
    grid.append(card);
    cards[n.id] = card;
  }
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.classList.add("wires");
  inner.append(svg, grid);
  figure.append(inner);

  const box = (el) => {
    const r = el.getBoundingClientRect(), o = inner.getBoundingClientRect();
    const left = r.left - o.left, top = r.top - o.top;
    return { left, top, right: left + r.width, bottom: top + r.height, cx: left + r.width / 2, cy: top + r.height / 2 };
  };
  const draw = () => {
    inner.querySelectorAll(".wire-label, .canvas-lane").forEach((el) => el.remove());
    for (const lane of spec.lanes || []) {
      const boxes = lane.nodes.map((id) => box(cards[id]));
      const div = document.createElement("div");
      div.className = `canvas-lane ${lane.kind || "plain"}`;
      const pad = 18, top = Math.min(...boxes.map((b) => b.top)) - pad - 14;
      const left = Math.min(...boxes.map((b) => b.left)) - pad;
      div.style.cssText = `left:${left}px; top:${top}px; width:${Math.max(...boxes.map((b) => b.right)) + pad - left}px; height:${Math.max(...boxes.map((b) => b.bottom)) + pad - top}px;`;
      div.innerHTML = `<span>${lane.label}</span>`;
      inner.prepend(div);
    }
    packets = packets.filter((p) => !svg.contains(p.dot)); // the old dots of this canvas go with its old wires
    let paths = "";
    spec.edges.forEach((e, i) => {
      const a = box(cards[e.from]), z = box(cards[e.to]);
      let d;
      if (e.via === "down") { // bottom to top, even on a diagonal: keeps a card's sides free for other wires
        const dy = Math.max(24, (z.top - a.bottom) / 2);
        d = `M${a.cx},${a.bottom} C${a.cx},${a.bottom + dy} ${z.cx},${z.top - dy} ${z.cx},${z.top}`;
      } else if (z.left >= a.right - 2) { // to the right: leave the right side, arrive on the left
        const dx = Math.max(28, (z.left - a.right) / 2);
        d = `M${a.right},${a.cy} C${a.right + dx},${a.cy} ${z.left - dx},${z.cy} ${z.left},${z.cy}`;
      } else if (z.right <= a.left + 2 && e.via === "top") { // back to the left, looping over the cards
        const rise = Math.min(a.top, z.top) - 36;
        d = `M${a.cx},${a.top} C${a.cx},${rise} ${z.cx},${rise} ${z.cx},${z.top}`;
      } else if (z.right <= a.left + 2 && e.via === "bottom") { // back to the left, looping under the cards
        const dip = Math.max(a.bottom, z.bottom) + 36;
        d = `M${a.cx},${a.bottom} C${a.cx},${dip} ${z.cx},${dip} ${z.cx},${z.bottom}`;
      } else if (z.right <= a.left + 2) { // back to the left: leave the left side, arrive on the right
        const dx = Math.max(28, (a.left - z.right) / 2);
        d = `M${a.left},${a.cy} C${a.left - dx},${a.cy} ${z.right + dx},${z.cy} ${z.right},${z.cy}`;
      } else if (z.top >= a.bottom) { // straight down
        const dy = (z.top - a.bottom) / 2;
        d = `M${a.cx},${a.bottom} C${a.cx},${a.bottom + dy} ${z.cx},${z.top - dy} ${z.cx},${z.top}`;
      } else { // straight up
        const dy = (a.top - z.bottom) / 2;
        d = `M${a.cx},${a.top} C${a.cx},${a.top - dy} ${z.cx},${z.bottom + dy} ${z.cx},${z.bottom}`;
      }
      const type = e.type || "main";
      paths += `<path class="wire ${type}" d="${d}" data-i="${i}"/>`;
    });
    svg.innerHTML = paths;
    svg.querySelectorAll("path.wire").forEach((path) => {
      const e = spec.edges[path.dataset.i];
      const type = e.type || "main";
      const len = path.getTotalLength();
      const tip = path.getPointAtLength(len), back = path.getPointAtLength(Math.max(0, len - 6));
      const angle = (Math.atan2(tip.y - back.y, tip.x - back.x) * 180) / Math.PI;
      svg.insertAdjacentHTML("beforeend",
        `<polygon class="wire-head ${type}" points="-7,-4.5 1,0 -7,4.5" transform="translate(${tip.x} ${tip.y}) rotate(${angle})"/>`);
      if (type === "main" && !calm && !spec.still) {
        const dot = document.createElementNS(SVG_NS, "circle");
        dot.setAttribute("class", "packet");
        dot.setAttribute("r", "3.5");
        const start = path.getPointAtLength(0); // on the wire from the first frame, never in the corner
        dot.setAttribute("cx", start.x);
        dot.setAttribute("cy", start.y);
        svg.append(dot);
        packets.push({ dot, path, len, offset: path.dataset.i * 25 }); // staggered, so the dots do not move in step
      }
      if (e.label) {
        const mid = path.getPointAtLength(len * (e.at || 0.55));
        const start = path.getPointAtLength(0);
        // A level wire: lift the label above it, off the line. Not a loop: its ends are level, but its middle is not.
        const flat = !e.via && Math.abs(tip.y - start.y) < 8;
        const label = document.createElement("span");
        label.className = `wire-label ${type}`;
        label.style.left = `${mid.x}px`;
        label.style.top = `${flat ? mid.y - 15 : mid.y}px`;
        label.innerHTML = e.label;
        inner.append(label);
      }
    });
  };
  let queued = false;
  new ResizeObserver(() => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; draw(); });
  }).observe(inner);
}
// The dots that travel along the main path, moved by one animation loop for every canvas on the page.
let packets = [];
function movePackets(now) {
  for (const p of packets) {
    const at = p.path.getPointAtLength(((now / 1000) * 70 + p.offset) % p.len); // 70 pixels a second
    p.dot.setAttribute("cx", at.x);
    p.dot.setAttribute("cy", at.y);
  }
  requestAnimationFrame(movePackets);
}
function startCanvases() {
  document.querySelectorAll("figure.canvas").forEach(renderCanvas);
  if (!calm && packets.length) requestAnimationFrame(movePackets);
}
