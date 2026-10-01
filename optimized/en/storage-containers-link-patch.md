# logbatt.com/storage-containers/ – link patch (product detail pages)

Date: 2026-10-01. Background: `notes/geo-analysis-com-hardware-2026-10-01.md`, section 3.1. The
category page does not link to the three product detail pages, so AI engines almost never retrieve
them (XL Storage 2, M Storage 1, L Storage 0 retrievals in 30 days).

The Gutenberg source of the English storage page **isn't in this repo**. This patch is based on the
live front-end HTML of 2026-10-01, so it consists of insert/replace steps for the block editor.
If you add the page's Gutenberg code to `optimized/en/storage-containers.html`, I can apply the
patch to the file directly, the way it was done for `transport-crates.html`.

Target URLs (checked on 2026-10-01, all return 200, no redirects):

| Product | Card anchor on the page | Product detail page |
| --- | --- | --- |
| SafetyBATTbox XL Storage | `#safety-batt-box-xl-storage` | `https://www.logbatt.com/storage-containers/safetybattbox-xl-storage/` |
| SafetyBATTbox L Storage | `#safety-batt-box-l-storage` | `https://www.logbatt.com/storage-containers/safetybattbox-l-storage/` |
| SafetyBATTbox M Storage | `#safety-batt-box-m-storage` | `https://www.logbatt.com/storage-containers/safetybattbox-m-storage/` |

---

## 1. Product carousel at the top: point the buttons to the product pages

The live EN page already has the product carousel (the `rh/block-splide` block with three slides:
XL Storage, L-Storage, M-Storage). Its "Go to the product" buttons currently jump to anchors on the
same page (`#safety-batt-box-xl-storage` etc.). On the German page (`/lagerbehaelter/`) the same
buttons open the product pages. In the editor, change only the button link (the text stays):

| Slide | Old link | New link |
| --- | --- | --- |
| XL Storage | `#safety-batt-box-xl-storage` | `https://www.logbatt.com/storage-containers/safetybattbox-xl-storage/` |
| L-Storage | `#safety-batt-box-l-storage` | `https://www.logbatt.com/storage-containers/safetybattbox-l-storage/` |
| M-Storage | `#safety-batt-box-m-storage` | `https://www.logbatt.com/storage-containers/safetybattbox-m-storage/` |

## 1b. Product overview: link the box titles

Section "Product overview: the SafetyBATTbox storage containers compared". Put the link on the
H4 title of each box, the same way the German transport-crates page does it. Don't add any extra text.
In the editor: select the title text → link → paste the URL. In the code editor, the three
headings look like this afterwards:

```html
<!-- wp:heading {"level":4,"anchor":"safety-batt-box-xl-storage"} -->
<h4 id="safety-batt-box-xl-storage" class="wp-block-heading"><a href="https://www.logbatt.com/storage-containers/safetybattbox-xl-storage/" data-type="link" data-id="https://www.logbatt.com/storage-containers/safetybattbox-xl-storage/">SafetyBATTbox XL Storage</a></h4>
<!-- /wp:heading -->
```
```html
<!-- wp:heading {"level":4,"anchor":"safety-batt-box-l-storage"} -->
<h4 id="safety-batt-box-l-storage" class="wp-block-heading"><a href="https://www.logbatt.com/storage-containers/safetybattbox-l-storage/" data-type="link" data-id="https://www.logbatt.com/storage-containers/safetybattbox-l-storage/">SafetyBATTbox L Storage</a></h4>
<!-- /wp:heading -->
```
```html
<!-- wp:heading {"level":4,"anchor":"safety-batt-box-m-storage"} -->
<h4 id="safety-batt-box-m-storage" class="wp-block-heading"><a href="https://www.logbatt.com/storage-containers/safetybattbox-m-storage/" data-type="link" data-id="https://www.logbatt.com/storage-containers/safetybattbox-m-storage/">SafetyBATTbox M Storage</a></h4>
<!-- /wp:heading -->
```

Leave the left "Products" navigation (jump links within the page) unchanged.

## 2. Fix the broken rental link (404)

Section "Storage containers — now also available for hire!": the word **"hired"** links to
`https://www.logbatt.com/transport-crates/rent-storage-boxes/`, which returns **404**.

Replace with:
```
https://www.logbatt.com/transport-crates/storage-container-leasing/
```

## 3. JSON-LD: give each product its page URL

In the page's JSON-LD (the `ItemList` with the three `Product` items), add a `url` line directly
below each `@id` line:

```json
"@id": "https://www.logbatt.com/storage-containers/#product-xl-storage",
"url": "https://www.logbatt.com/storage-containers/safetybattbox-xl-storage/",
```
```json
"@id": "https://www.logbatt.com/storage-containers/#product-l-storage",
"url": "https://www.logbatt.com/storage-containers/safetybattbox-l-storage/",
```
```json
"@id": "https://www.logbatt.com/storage-containers/#product-m-storage",
"url": "https://www.logbatt.com/storage-containers/safetybattbox-m-storage/",
```

Don't forget the comma at the end of each new line. Afterwards, check the page with
https://validator.schema.org/.

## 4. Check after publishing

- Front end: the three carousel buttons and the three box titles in the product overview each open
  the correct product page.
- The "hired" link opens the rental page (no 404).
- Rich Results Test / Schema validator: no errors, each product shows its `url`.
- Side note, not part of this patch: on the live page, several product images use
  `src="https://www.logbatt.de/…"`. On `/transport-crates/` this was blocked by the front-end CSP
  (see commit d3bf7f0). Here a `srcset` on `www.logbatt.com` exists, so most browsers probably
  still show the images, but switching the `src` to `www.logbatt.com` is the safe option.
