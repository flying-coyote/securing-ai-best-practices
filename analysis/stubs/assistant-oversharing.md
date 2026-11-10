---
evidence-tier: Mixed
convergence: single-source
applies-to-signals: [grounding-permissions-unreviewed, sensitivity-labels-absent, restricted-search-unset]
surfaces: [S1, S2]
pins:
  - "CoSAI secure-ai-tooling 622605a1"
summary-section: "Summary for the review"
last-verified: 2026-11-10
revalidate-by: 2027-03-03
status: EMERGING
---

# Assistant oversharing (S1, S2): declared gap

Evidence tier: Mixed. What each vendor control does and what its default is comes from the assistant vendor's own admin and governance documentation (B); the control and risk vocabulary comes from the CoSAI risk map (A); the ordering of the three practices is my judgement (D). This repo has no lab result on the family, which is why it is a stub.

## Summary for the review

An enterprise assistant grounded on company content answers from whatever the asking user can already reach, so a permissions mistake that sat unnoticed in a file share becomes something a single prompt can find, and the controls that matter are the ones the assistant vendor documents for the content side rather than anything on the model side. Until this repo has measured how those controls behave, read the vendor's own governance guidance and the CoSAI data controls named below.

- Review permissions on the content the assistant can ground on before or alongside rollout, starting with sites and drives shared with everyone in the organization, anyone with the link, or external users, and use the vendor's oversharing report where the tenant has one. Effort M to L. Tier B.
- Publish a sensitivity label taxonomy and the assistant-side rule that reads it, so labelled items can be kept out of grounded answers. Effort M. Tier B.
- While the permissions review runs, restrict what the assistant can discover on the riskiest sites, using the vendor's documented interim control, and record which sites are restricted and why so the restriction is lifted once they are fixed. Effort S per site. Tier B.

The owner is the collaboration-suite administrator, with data owners holding the permission fixes. What follows names the vendor pages; it does not assume the organization runs either platform.

## Why this matters

Both large suite vendors state the same mechanism in their own words. Microsoft says Copilot "only surfaces organizational data to which individual users have at least view permissions" and tells customers to use the permission models in SharePoint and the other services to get access right (Tier B, Microsoft Learn, "Data, Privacy, and Security for Microsoft Copilot", read 2026-11-10). Google says "Gemini only retrieves relevant content in Workspace that the user has access to" (Tier B, Generative AI in Google Workspace Privacy Hub, read 2026-11-10). So what the assistant adds is less a new exposure than the loss of the obscurity that used to hide an old one, which is why the fix lives in the permissions on the source content. On S1, where AI is embedded in a SaaS product, the same question becomes what content the feature's OAuth grant or connector can reach.

CoSAI names the risk as Sensitive Data Disclosure and notes that agentic systems "may be granted privileged access to a user's email, files" (Tier A, CoSAI risk map `risks.yaml` at `622605a1`). The nearest controls at that commit are Agent Permissions, whose components include RAGContent and Memory and which asks that a system "share only contextually appropriate information", and User Data Management, which covers prompts and logs (Tier A, `controls.yaml` at `622605a1`). Neither prescribes a permissions review of grounding sources, and I read that absence as part of the gap rather than as a reason to skip the practice.

## Vendor controls by signal

| Signal | Platform family | Control | Default | Where the record lands | last-checked |
|---|---|---|---|---|---|
| grounding-permissions-unreviewed | Microsoft 365 | Purview DSPM for AI default data risk assessment: weekly, top 100 SharePoint sites by usage, results after a four-day first delay, 200,000 items per location; documented on the classic page, which Microsoft says a new DSPM replaces | runs with no activation | DSPM for AI, Data risk assessments; export to Excel, CSV, JSON or TSV | 2026-11-10 |
| grounding-permissions-unreviewed | Google Workspace | Gemini app access to Workspace apps (Calendar, Docs, Drive, Gmail, Keep, Tasks, Classroom); changes take up to 24 hours and need conversation history on | on (Classroom only for Education tenants) | Gemini for Workspace log events (named on Google's log events page; the setting page names no log) | 2026-11-10 |
| sensitivity-labels-absent | Microsoft 365 | DLP policy, location Microsoft 365 Copilot and Copilot Chat, condition sensitivity labels; the item still appears in citations; updates take up to four hours | no policy until created | Purview DLP alerts | 2026-11-10 |
| sensitivity-labels-absent | Microsoft 365 | Encrypting sensitivity labels; Copilot returns data from an item only when the user holds the EXTRACT usage right | no labels published until created | label metadata on the item | 2026-11-10 |
| sensitivity-labels-absent | Google Workspace | DLP for Gemini rule on Drive content (conditions include classification labels; actions Block data access or Audit only) | no rule until created | rule event logged (log name not stated on the page) | 2026-11-10 |
| restricted-search-unset | Microsoft 365 | Restricted Content Discovery, per site; changes discoverability, not permissions; not supported for OneDrive; sites over 500,000 items can take more than a week | off per site; needs a Copilot licence and SharePoint Advanced Management | Purview audit (enable, disable, justification) | 2026-11-10 |
| restricted-search-unset | Microsoft 365 | Restricted SharePoint Search, an allow list of up to 100 sites; retiring, with new enablement blocked from 2026-07-31 | off | none named | 2026-11-10 |
| restricted-search-unset | Google Workspace | No direct scope-restriction equivalent found; the nearest levers are the Workspace apps setting and DLP for Gemini above | not applicable | not applicable | 2026-11-10 |

Two points from the vendor text change how a review should read these rows. Microsoft documents both interim controls as temporary and says neither changes permissions, so a user who already has access keeps it and an open document can still be summarised (Tier B, Restricted Content Discovery page, read 2026-11-10). And because Restricted SharePoint Search can no longer be newly enabled, a "No" on `restricted-search-unset` in a Microsoft tenant now points at Restricted Content Discovery and the licence it needs.

The fuller rows (console paths, licence wording, routing to a SIEM) will be in the Microsoft 365 Copilot, Microsoft Purview and Google Workspace pages of the forthcoming ai-config-pointers set, a separate repository that is not yet public and is not linked here until it is.

## What this does not mean

It does not mean the assistant leaks data a user could not otherwise open, since both vendors document grounding as bounded by the user's own access. It does not mean a restriction or a label rule is a security boundary either, which Microsoft says plainly of its search restriction, so the end state is corrected permissions rather than a growing restricted list. The oversharing report finds what Microsoft says it finds within its documented scope of the top 100 sites; how much oversharing it misses in a given tenant is a question of efficacy that the vendor page does not answer and this repo has not measured.

## Gaps

- **Gap: assistant oversharing controls, measured**. No public, re-runnable measurement shows whether these controls keep planted content out of grounded answers, and the repo has no lab run on the family. **Needs**: an sdw-lab-benchmarks run in a Microsoft 365 developer tenant and a Google Workspace trial tenant that plants an overshared file, a labelled file and a file on a restricted site, then records for a set of prompts whether each assistant returns, cites or omits each item under each control state, with the propagation delay timed; plus a read of the connector permission documentation for the standalone enterprise assistants, which this stub does not cover.

## Notes

- Convergence stays `single-source` because no published standard at the pinned commit prescribes a grounding-source permissions review; the CoSAI controls are adjacent, not prescriptive.
- No `measurement-claims` rows, because the family has no lab result; the vendor defaults above are dated table rows, not re-runnable claims.
- `revalidate-by` is about four months out because one row is a control Microsoft is retiring, with new enablement already blocked, the DSPM row is documented on a classic page that Microsoft says a new DSPM replaces, and vendor defaults move on release cycles.

## Sources

Tier A
- CoSAI, secure-ai-tooling `risk-map/yaml/controls.yaml` and `risks.yaml` at commit `622605a1`, https://github.com/cosai-oasis/secure-ai-tooling (controlAgentPluginPermissions, controlUserDataManagement, riskSensitiveDataDisclosure).

Tier B (vendor documentation of what a feature does; all read 2026-11-10)
- Microsoft Learn, "Data, Privacy, and Security for Microsoft Copilot", https://learn.microsoft.com/en-us/copilot/plan/microsoft-365-copilot-privacy
- Microsoft Learn, "Restrict discovery of SharePoint sites and content", https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
- Microsoft Learn, "Restricted SharePoint Search", https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search
- Microsoft Learn, "Microsoft Purview DSPM for AI (classic)", https://learn.microsoft.com/en-us/purview/dspm-for-ai
- Microsoft Learn, "Microsoft Purview DLP for Microsoft 365 Copilot and Cowork", https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about
- Microsoft Learn, "Learn about sensitivity labels", https://learn.microsoft.com/en-us/purview/sensitivity-labels
- Google Workspace Admin Help, "Generative AI in Google Workspace Privacy Hub", https://knowledge.workspace.google.com/admin/gemini/generative-ai-in-google-workspace-privacy-hub
- Google Workspace Admin Help, "Control Gemini App access to Workspace services", https://knowledge.workspace.google.com/admin/generative-ai/gemini-app/turn-google-apps-in-gemini-on-or-off
- Google Workspace Admin Help, "About DLP for Gemini", https://knowledge.workspace.google.com/admin/security/about-dlp-for-gemini
- Google Workspace Admin Help, "Gemini for Workspace log events", https://knowledge.workspace.google.com/admin/reports/gemini-for-workspace-log-events
