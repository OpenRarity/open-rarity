# DNS cutover handoff

The new site is deployed at https://openrarity.github.io/open-rarity/.
IT or the domain owner performs the cutover; the existing site stays live until then.

1. Verify `openrarity.dev` in the OpenRarity organization's Pages settings using
   the exact TXT record GitHub supplies. Keep that verification record.
2. Review the deployed site. Export existing DNS records and lower the relevant
   TTLs to 300 seconds ahead of the change window.
3. At cutover, set `openrarity.dev` as the repository Pages custom domain, then
   replace the old hosting records with these DNS-only records (proxy off):

   | Name | Type | Value |
   | --- | --- | --- |
   | `@` | A | `185.199.108.153` |
   | `@` | A | `185.199.109.153` |
   | `@` | A | `185.199.110.153` |
   | `@` | A | `185.199.111.153` |
   | `www` | CNAME | `openrarity.github.io` |

4. Remove conflicting old hosting A/AAAA/CNAME records only. Preserve mail,
   organization verification, and other unrelated TXT records.
5. Set the repository Actions variable `SITE_URL` to `https://openrarity.dev`
   and run the Site preview workflow on main to refresh the sitemap.
6. Enable Enforce HTTPS once GitHub issues the certificate. Verify root and www,
   redirects, docs, scorer upload/download, and social previews.

Keep the previous hosting subscription and exported DNS configuration for a week.
Rollback restores the previous hosting records and removes the Pages custom domain.
No DNS or old-hosting changes are performed by the deployment workflow.

[GitHub's current custom-domain instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
