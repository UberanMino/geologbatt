// Erzeugt PDF-Produktblätter der SafetyBATTbox-Produktdetailseiten in einer Zielsprache.
//
//   node build.mjs ro            -> out/ro/<slug>-ro.pdf für alle Produkte
//   node build.mjs ro l-2        -> nur Produkte, deren Slug "l-2" enthält
//
// Technische Daten (Zahlen, Codes) werden direkt aus der deutschen Quelldatei unter website/de/
// gelesen; die Sprachdatei content/<lang>.json liefert nur Übersetzungen. Der Build bricht ab, wenn
// Anzahl der Bullets/FAQ nicht zum Original passt oder ein Text-Wert der Tabelle unübersetzt ist.

import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { chromium } from "playwright";
import { PDFDocument } from "pdf-lib";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..");

const lang = process.argv[2];
const filter = process.argv[3];
if (!lang) {
  console.error("Aufruf: node build.mjs <lang> [slug-filter]");
  process.exit(1);
}

const meta = JSON.parse(await readFile(path.join(here, "products.json"), "utf8"));
const tr = JSON.parse(await readFile(path.join(here, "content", `${lang}.json`), "utf8"));
const ui = tr.ui;

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const fill = (s, vars) => s.replace(/\{(\w+)\}/g, (_, k) => vars[k]);

// --- deutsche Quelldatei lesen ---------------------------------------------------------------
function parseSource(html) {
  const visible = html.split("<!-- wp:html")[0];
  const ul = visible.match(/<ul>([\s\S]*?)<\/ul>/);
  const bullets = ul ? [...ul[1].matchAll(/<li>/g)].length : 0;
  const specs = [];
  const table = visible.split("Technische Daten</h3>")[1] ?? "";
  for (const line of table.split("\n")) {
    const m = line.match(/^\|\s*(.+?)\s*\|\s*(.+?)\s*\|$/);
    if (m && !/^-+$/.test(m[1])) specs.push([m[1], m[2]]);
  }
  const faq = [...html.matchAll(/"@type": "Question"/g)].length;
  const rent = /Kauf oder Miete/.test(visible);
  return { bullets, specs, faq, rent };
}

// Werte ohne Sprachanteil: Zahlen/Maße, Typbezeichnung, UN-Codierung, P-/LP-Anweisungen, VG I/II, "–".
const NEUTRAL = /^(\d[\d.,\sx+]*|SBB .+|UN .+|(L?P\d{3})( \/ L?P\d{3})*|I{1,3}|–)$/;

function translateSpecs(specs, slug) {
  return specs.map(([label, value]) => {
    const l = tr.spec_labels[label];
    if (!l) throw new Error(`${slug}: Spec-Label ohne Übersetzung: "${label}"`);
    let v = tr.spec_values[value];
    if (v === undefined) {
      if (!NEUTRAL.test(value)) throw new Error(`${slug}: Spec-Wert ohne Übersetzung: "${value}"`);
      v = value;
    }
    return { de: label, label: l, value: v };
  });
}

// "Sarcină utilă max. [kg]" + "357" -> { k: "Sarcină utilă max.", v: "357 kg" }
function fact(spec) {
  const m = spec.label.match(/^(.*?)\s*\[(.+)\]$/);
  return m ? { k: m[1], v: `${spec.value} ${m[2]}` } : { k: spec.label, v: spec.value };
}

function keyFacts(product, specs) {
  const by = Object.fromEntries(specs.map((s) => [s.de, s]));
  if (product.category === "storage") {
    return ["Max. Zuladung [kg]", "Volumen [l]", "Leergewicht [kg]", "Stapelbar"].map((k) => fact(by[k]));
  }
  const bam = (by["Zulassung"].value.match(/D-BAM \d+/) ?? [by["Zulassung"].value])[0];
  return [
    fact(by["Max. Zuladung [kg]"]),
    fact(by["Verpackungsgruppe"]),
    fact(by["ADR Verpackungsanweisungen"]),
    { k: ui.bam, v: bam },
  ];
}

// --- HTML ------------------------------------------------------------------------------------
function render(product, t, specs) {
  const facts = keyFacts(product, specs);
  const category = ui[`category_${product.category}`];
  const fit = product.fit === "cover" ? "photo" : "";
  const pos = product.position ? ` style="object-position:${product.position}"` : "";
  const rent = t.rent
    ? `<section class="rent"><h3>${esc(ui.rent_title)}</h3><p>${fill(ui[`rent_${product.category}`], { name: esc(t.name) })}</p></section>`
    : "";
  return `<!doctype html>
<html lang="${tr.lang}">
<head>
<meta charset="utf-8">
<title>${esc(`${t.name} – ${t.subtitle} | ${meta.company.name}`)}</title>
<meta name="description" content="${esc(t.bullets[0])}">
<link rel="stylesheet" href="${pathToFileURL(path.join(here, "template", "style.css"))}">
</head>
<body>
<header class="masthead">
  <img src="${pathToFileURL(path.join(here, "assets", "logo.svg"))}" alt="LogBATT">
  <div class="doc"><strong>${esc(ui.doc_type)}</strong>${esc(category)}</div>
</header>

<section class="hero">
  <div>
    <p class="eyebrow">SafetyBATTbox</p>
    <h1>${t.name.split(" ").map((w) => `<span class="nw">${esc(w)}</span>`).join(" ")}</h1>
    <p class="subtitle">${esc(t.subtitle)}</p>
    <div class="facts">
      ${facts.map((f) => `<div class="fact"><div class="k">${esc(f.k)}</div><div class="v">${esc(f.v)}</div></div>`).join("\n      ")}
    </div>
  </div>
  <div class="figure ${fit}"><img src="${pathToFileURL(path.join(here, product.image))}" alt="${esc(t.name)}"${pos}></div>
</section>

<h2>${esc(ui.features)}</h2>
<ul class="features">
  ${t.bullets.map((b) => `<li>${esc(b)}</li>`).join("\n  ")}
</ul>
${rent}

<h2 class="page-break">${esc(ui.specs)}</h2>
<div class="specs-grid">
  ${[specs.slice(0, Math.ceil(specs.length / 2)), specs.slice(Math.ceil(specs.length / 2))]
    .map((half) => `<table class="specs">${half.map((s) => `<tr><th>${esc(s.label)}</th><td>${esc(s.value)}</td></tr>`).join("")}</table>`)
    .join("\n  ")}
</div>

<h2>${esc(fill(ui.faq, { name: t.name }))}</h2>
<dl class="faq">
  ${t.faq.map((f) => `<div class="item"><dt>${esc(f.q)}</dt><dd>${esc(f.a)}</dd></div>`).join("\n  ")}
</dl>

<section class="cta">
  <div><h3>${esc(ui.cta_title)}</h3><p>${esc(ui.cta_text)}</p></div>
  <div class="contact">
    <strong>${esc(meta.company.name)}</strong><br>
    ${esc(meta.company.street)}, ${esc(meta.company.city)}, ${esc(ui.country)}<br>
    <a href="tel:${meta.company.phone.replace(/\s/g, "")}">${esc(meta.company.phone)}</a><br>
    <a href="mailto:${meta.company.email}">${esc(meta.company.email)}</a> · <a href="https://${meta.company.web}/">${esc(meta.company.web)}</a>
  </div>
  <p class="source">${esc(ui.original)}: <a href="${product.url}">${esc(product.url)}</a></p>
</section>
</body>
</html>`;
}

function footer() {
  // Kopf-/Fußzeilen-Templates rendert Chromium isoliert (keine Webfonts); Liberation Sans/Arial genügt hier.
  const c = meta.company;
  return `<div style="font-family:Roboto,'Liberation Sans',Arial,sans-serif;font-size:7pt;color:#6f7074;width:100%;margin:0 15mm;display:flex;justify-content:space-between;">
  <span>${esc([c.name, c.street, c.city, ui.country, c.phone, c.email, c.web].join(" · "))}</span>
  <span>${esc(ui.page)} <span class="pageNumber"></span> ${esc(ui.of)} <span class="totalPages"></span></span>
</div>`;
}

// --- Build -----------------------------------------------------------------------------------
const outDir = path.join(here, "out", lang);
const tmpDir = path.join(here, ".build", lang);
await mkdir(outDir, { recursive: true });
await mkdir(tmpDir, { recursive: true });

const footerTemplate = footer();
const browser = await chromium.launch();
const page = await browser.newPage();
let count = 0;

for (const product of meta.products) {
  if (filter && !product.slug.includes(filter)) continue;
  const t = tr.products[product.slug];
  if (!t) throw new Error(`${product.slug}: keine Übersetzung in content/${lang}.json`);

  const src = parseSource(await readFile(path.join(repo, product.source), "utf8"));
  if (src.bullets !== t.bullets.length) throw new Error(`${product.slug}: ${t.bullets.length} Bullets übersetzt, Original hat ${src.bullets}`);
  if (src.faq !== t.faq.length) throw new Error(`${product.slug}: ${t.faq.length} FAQ übersetzt, Original hat ${src.faq}`);
  const specs = translateSpecs(src.specs, product.slug);

  const html = render(product, { ...t, rent: src.rent }, specs);
  const htmlFile = path.join(tmpDir, `${product.slug}.html`);
  await writeFile(htmlFile, html);
  await page.goto(pathToFileURL(htmlFile).href, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);

  const raw = await page.pdf({
    preferCSSPageSize: true,
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: "<span></span>",
    footerTemplate,
    tagged: true,
    outline: true,
  });

  // Metadaten setzen (Titel, Autor, Sprache, Stichwörter) – hilft Suchmaschinen und LLM-Crawlern.
  const pdf = await PDFDocument.load(raw, { updateMetadata: false });
  pdf.setTitle(`${t.name} – ${t.subtitle}`, { showInWindowTitleBar: true });
  pdf.setAuthor(meta.company.name);
  pdf.setSubject(t.bullets[0]);
  pdf.setKeywords([`${ui.keywords}, ${t.name}`]);
  pdf.setLanguage(tr.lang);
  pdf.setCreator("LogBATT product-pdfs");
  pdf.setProducer("LogBATT product-pdfs (Chromium + pdf-lib)");
  const outFile = path.join(outDir, `${product.slug}-${lang}.pdf`);
  await writeFile(outFile, await pdf.save());
  console.log(`${path.relative(repo, outFile)}  (${pdf.getPageCount()} Seiten)`);
  count++;
}

await browser.close();
if (!count) throw new Error(`Kein Produkt passt zu "${filter}"`);
