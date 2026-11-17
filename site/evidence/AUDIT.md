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
