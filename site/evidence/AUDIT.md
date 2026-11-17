# Preview audit

Local Chromium audit on 2026-11-16, using Lighthouse 13.6.0 with its default mobile configuration against the local static server:

| Category | Score |
| --- | --- |
| Performance | 100 |
| Accessibility | 100 |
| Best practices | 100 |
| SEO | 100 |

These are local preview measurements. Repeat against the deployed URL to include hosting, network, and cache behavior. Automated accessibility checks are not a complete WCAG conformance assessment.

Twelve browser tests pass, including axe checks for the home page and all three generated document pages in light and dark themes, mobile/desktop overflow, invalid input, safe rendering, local upload, and result download.

The accessibility audit found empty links left by removed external badges; the build now retains their accessible text. The initial Lighthouse console error came from a missing favicon; a local SVG icon fixes it.

## Condensed site and Pages launch, November 17, 2026

The landing page now contains a short introduction, package and guide links, and
the browser scorer. Long explanations moved to separate guides. Desktop/mobile
screenshots were refreshed. Sixteen browser tests pass, including light/dark axe
checks across five pages, exact large-number scoring with creator settings,
legacy anchors, file upload/download, errors, and text-only rendering.
Horizontal code blocks are keyboard focusable. The earlier Lighthouse results
were for the preview; they are not a new measurement of this layout.

## Design pass

The install card now sits beside the introduction on desktop, with resources in a
compact row and a cleaner editor/results panel. The desktop page is about 1,300px
tall at 1440px width. Mobile stacks the same content without horizontal overflow.
Eighteen browser tests pass, including the new example selector and clipboard copy.
Light/dark accessibility checks and all existing scorer assertions are retained.
