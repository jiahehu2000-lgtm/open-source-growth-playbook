---
name: github-project-outreach
description: Improve a GitHub project's discoverability and chances of earning voluntary Stars through evidence-based positioning, README edits, real demos, relevant launch materials, and measurement. Use for open-source outreach, project launch posts, README onboarding, or GitHub Star-growth planning; it is not a tool for collecting stars automatically.
---

# GitHub Project Outreach｜开源项目传播与点星优化

Help the intended audience understand, try, and revisit a real project. Optimize the route from useful content to a voluntary Star; do not promise a particular growth result.

## Establish what is real

Read the actual repository, docs, install commands, license, and available demo. Identify the intended reader, one concrete problem solved, prerequisites, and the strongest verifiable output. When changing badges, releases, Topics or public demo links, verify their public state or label it unverified. Preserve scientific data, reported results, and functional code when the request is about presentation.

If asked about current hot directions, collect dated primary evidence. Distinguish cumulative repository Stars, GitHub Trending gains for a stated period, and votes/comments on a separate platform. Present an editorial selection as a selection, not an official ranking. Prefer comparable projects; a large general AI framework is a poor conversion benchmark for a small scientific plotting utility.

## Improve the useful path

Prioritize changes that remove a demonstrated obstacle:

- Unclear purpose: lead with who benefits and the concrete outcome.
- Invisible value: show a real output or runnable example, labeling synthetic data and diagrams accurately.
- Hard to start: give the shortest verified route to the first result; expose dependencies and limits near it.
- Hard to revisit: add relevant search terms, clear navigation, accurate badges, and a brief optional Star invitation.
- Unsupported promises: replace them with bounded claims supported by evidence; compare alternatives fairly.

Scale the work to the request. A focused README repair need not become a full campaign. Use [content-patterns.md](references/content-patterns.md) for launch formats and channel-specific decisions. Preserve a supplied template or language preference.

## Prepare channel-appropriate material

For the selected community, check its current self-promotion, link and posting rules first. Except for the HN restriction below, draft concise titles, demonstration captions, and a post explaining the actual problem, what was built, how to try it, and its present limits. Adapt the content to readers rather than copying a popular post's wording. Link to relevant docs and ask for useful feedback.

For Hacker News, read the current [HN guidelines](https://news.ycombinator.com/newsguidelines.html) and [Show HN criteria](https://news.ycombinator.com/showhn.html). They currently prohibit generated/AI-edited text and automated posting; Show HN also excludes lists and blog posts. Provide a factual preparation brief or review, not a ready-to-submit HN post. The author writes their own final text.

Repo editing authorization does not authorize submitting to other communities, sending messages, or leaving promotional comments. Prepare those materials unless the human separately authorizes the specific external action. Do not buy Stars, coordinate fake engagement, gate downloads behind Stars, or automate starring.

## Measure without inventing success

Use [measurement.md](references/measurement.md) when asked to track growth or diagnose traffic. Save a timestamped baseline before a change and compare the same repository and an explicit observation window. A single snapshot establishes current counts, not growth or causal impact.

The bundled helper reads public repository metadata without credentials. It requires Python 3.10+ and only the standard library; it was tested on Python 3.12. Check its offline entry point with `python scripts/github_snapshot.py --help`:

```text
python scripts/github_snapshot.py capture owner/repo --output outputs/baseline.json
python scripts/github_snapshot.py capture owner/repo --output outputs/later.json
python scripts/github_snapshot.py compare outputs/baseline.json outputs/later.json --output outputs/change.json
```

These paths are relative to this Skill folder. Network failures remain explicit errors, not zero Stars. Existing output files are not overwritten. Do not request, print, or save access tokens; use existing authorized tooling if private traffic metrics are needed.

## Deliver a reviewable result

Summarize the evidence, the specific changes or patches, usable material, verification performed, and a proportionate next measurement step. Distinguish “prepared,” “published,” and “growth observed.” Publish repo changes only within the user's authorized scope; do not infer a recurring monitor or social-posting campaign.
