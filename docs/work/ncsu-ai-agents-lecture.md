# NCSU lecture and companion article

## Brief

Prepare a presentation for NCSU on September 9, 2026, and an in-depth article
about AI agents in CI/CD for PhD students. The lecture runs approximately 40 to
60 minutes, and the companion article should target a similar reading duration
with deeper research, scoped formal arguments, worked examples, and empirical
limitations. Aim for approximately 9,000 to 13,000 substantive words. The
article should develop the companion notes into connected explanations, worked
examples, and references, rather than summarize the slide bullets.

Work is isolated in the `codex/ncsu-ai-agents-lecture` worktree, based on
`2b68a32` and rebased onto `origin/master` at `2fb3f5a` after the other task
completed its integration. Preserve the approved
Astro architecture, GitHub Pages hosting, existing URLs, and editorial design.

## Decisions

- The author requires the original presentation's Red Hat branding and layout
  preserved. The supplied PDF is the authoritative visual input. The original
  PPTX and companion notes are reference material and remain unchanged.
- Serve the original as pre-rendered slide images in a local HTML viewer, with
  the supplied PDF available as a backup. There are 22 slides and no animations.
  This avoids an external viewer or account dependency during the lecture.
- The article is the primary reading adaptation in the website's theme. Keep
  a secondary HTML slide presentation available for comparison, following the
  author's request to try both appearances. Both slide variants use one slide
  at a time, keyboard controls, fullscreen, and direct slide links. The HTML deck must preserve the original content 1:1, including wording,
  slide order, and meaningful visual relationships. Only formatting changes.
  Research expansion and editorial correction belong in the article.
- The chooser makes the original presentation the primary action, alongside
  the long article and the optional HTML slide comparison.
- Reuse the site's typography, colors, theme behavior, and AL branding for the
  chooser and HTML version. Preserve the original slide colors in both themes.
  Provide manual keyboard navigation, visible buttons, fullscreen, slide links,
  an original-slide transcript, and a PDF fallback. The long article is the
  continuous reading view; the themed slides are also a presentation. Do not introduce animation or auto-advance.
- Keep lecture route and asset visibility behind one registry decision. A draft
  is available only when `INCLUDE_DRAFTS=true` and Astro is in development or
  explicit preview mode. Production route generation returns no paths before
  opening local lecture inputs. A production build must work without those inputs.
- Draft PDF, images, and transcript live in ignored `.generated/lecture/`, never
  in `public/`. Do not import draft binary assets into the client bundle. Static
  endpoints emit approved files explicitly. `noindex` supplements exclusion but
  is not a substitute for keeping draft bytes out of production.
- Eventual publication uses reviewed derivatives in
  `presentation-assets/ai-agents-in-ci-cd/`, outside Astro's automatic public
  copying. The original PPTX and companion notes remain private inputs. Do not
  switch the registry to published until the chosen deck and article have their
  required approval and the reviewed asset set exists.
- The article corrects overly broad technical claims where necessary. Do not
  silently edit the original branded presentation to match the article. Private
  provenance records identify those editorial decisions and source limitations.

## Routes and maintenance

| Route | Purpose |
| --- | --- |
| `/talks.html` | Permanent talk index and top-level discovery |
| `/talks/ai-agents-in-ci-cd/original.pdf` | Unlisted presenter notes, one page per slide |
| `/talks/ai-agents-in-ci-cd/presenter.html` | Presenter window with synchronized cues and controls |
| `/talks/ai-agents-in-ci-cd.html` | Choose presentation or reading version |
| `/talks/ai-agents-in-ci-cd/original.html` | Original Red Hat slide presentation |
| `/talks/ai-agents-in-ci-cd/web.html` | Optional website-themed slide adaptation |
| `/talks/ai-agents-in-ci-cd/slides.pdf` | Original PDF backup |
| `/talks/ai-agents-in-ci-cd/slides/1.png` through `22.png` | Explicit slide assets |
| `/blog/2026/ai-agents-in-ci-cd.html` | Long companion article |

The author approved the article and both slide variants on September 6, 2026.
The notes PDF has an intentionally predictable URL: replace `original.html`
with `original.pdf`. It is not linked from site navigation, index pages, feeds,
or the sitemap. Unlisted means absent from discovery surfaces, not access-controlled.
The original slide PDF remains the distinct `slides.pdf` backup.

The lecture registry and web slide copy live in `src/data/lecture.ts`. Shared
visibility and asset lookup belong in `src/lib/lectures.ts`. The article has its
own draft metadata. Both are now approved and production-eligible. Coordinate
both states for future releases so their links resolve.

The explicit local preparation script, `scripts/prepare-lecture.py`, refreshes
the ignored asset set from the PDF and a slide transcript. Prefer the author's
PDF export over a LibreOffice conversion when matching the approved appearance.
Use only the bundled runtime's LibreOffice for optional PPTX conversion. Review
every changed rendered page after replacing source inputs.

```bash
python3 scripts/prepare-lecture.py --source /path/to/approved-slides.pdf --transcript /path/to/reviewed-transcript.json
npm run dev:preview -- --host 127.0.0.1 --port 4347
```

The transcript is an array of objects with `slide` (one-based slide number) and
`text` (an array of strings containing the visible slide text). For this deck,
it contains exactly 22 entries. The preparation script also accepts `--pptx`
to extract slide text alongside a PDF, but that extraction does not include
text on slide masters or explain visual diagrams. Review the transcript against
the rendered PDF. Never supply speaker notes as the transcript.

After article and viewer changes:

```bash
npm run check
npm run build
python3 scripts/verify_site.py --output output
python3 scripts/verify_lecture.py --output output
npm run build:preview
python3 scripts/verify_site.py --output output-preview --preview
python3 scripts/verify_lecture.py --output output-preview --preview
```

`verify_lecture.py` verifies approved lecture routes, source-asset identity,
text parity, and the unlisted presenter PDF in both build modes. Draft visibility
remains a shared registry decision for future material. The general site verifier remains
required for article visibility, links, documentation exclusion, feeds, and the CV.

Run previews on a separate loopback port, such as 4347. Keep both the PDF and
the complete tested local preview available on the presentation laptop as a
fallback for venue connectivity. Do not deploy `output-preview/` to Pages.

## Alternatives considered

- Microsoft supports embedding a PowerPoint stored on OneDrive. This adds an
  external service and public sharing configuration, so it is unnecessary for
  this lecture. See [Microsoft's embed guidance](https://support.microsoft.com/en-gb/office/embed-a-presentation-in-a-web-page-or-blog-19668a1d-2299-4af3-91e1-ae57af723a60).
- A PDF.js viewer is possible but adds a viewer runtime and worker. Pre-rendered
  pages need less runtime code for a fixed presentation. See
  [PDF.js documentation](https://mozilla.github.io/pdf.js/getting_started/).
- A browser's built-in PDF viewer remains a useful backup. The site viewer owns
  the main controls and layout, which differ between browser PDF implementations.
- Astro static endpoints fit GitHub Pages: emitted HTML and asset files require
  no application server. See [Astro endpoints](https://docs.astro.build/en/guides/endpoints/)
  and [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

## Work items

| Owner | Scope | Status |
| --- | --- | --- |
| Astra | Brief, slide adaptation, article editing, design review, integration | Complete; final presenter layout approved in browser |
| Sol / high | Architecture investigation, article research and drafting | Complete |
| Luna / xhigh | Viewer, explicit assets, preparation and verification scripts | Complete |
| Sol / high | Implementation and artifact review | Complete; final review clear |

## Evidence

- Rebased onto `origin/master` at `2fb3f5a` without conflicts.
- Approved article and lecture registry both use `draft: false`. Production and
  preview each contain 73 HTML pages with the presenter route included; both final
  builds and their site/lecture verifiers pass. `npm run check` reported zero errors, warnings,
  and hints. Both site and lecture artifact verifiers passed in both modes.
- Original PDF and all 22 emitted slide images match the approved input hashes.
  Per-slide visible-character counts match the transcript; manual review checks
  ordering and meaningful table/diagram relationships that counts cannot prove.
- Browser checks covered both deck modes, fullscreen, arrow/Page/Home/End keys,
  URL history, transcript focus, all 22 HTML slides at 1280 by 720, and the five
  reported dense slides. The author confirms the slide issues are resolved.
- Desktop and 390-pixel mobile article/Talks layouts were inspected without
  horizontal overflow. No animation or auto-advance was introduced.
- Every page of the 22-page presenter PDF was rendered and visually inspected.
  The updated slide 5 refresher was re-rendered and inspected separately. The
  PDF has one page per slide, with matching titles, readable type, and 22 links
  to canonical article sections. Source PDF is untagged; original HTML transcripts
  and native HTML slides provide a text alternative. The notes PDF is tagged.
- The notes endpoint returned HTTP 200 and `application/pdf`; served bytes matched
  the reviewed notes asset. No notes link or private source reference appeared
  in generated HTML, JS, XML, JSON, or text output. Notes and original slide PDFs
  remain separate assets. The final production and preview artifact checks include the updated slide 5
  PDF and compare both notes assets and all presenter cues.
- Installed from the existing lockfile with `npm ci`. Imported the real public
  CV and PDF from the same canonical private checkout through the existing adapter.
  No dependency or lockfile changes were required.
- Sol's review found stale reading time, insufficient text parity checks, and
  hidden transcript focus. All were corrected and reviewed. The subsequent
  unlisted PDF endpoint review was clear.
- Article research, editorial review, and author approval are complete. Local
  screenshots and authoring materials remain outside tracked/public assets.

## Presenter notes design

The companion article contains the detailed research, technical corrections,
formal assumptions, primary citations, and empirical qualifications. It is
approximately 11,947 visible words, with a 54-minute estimate at 225 words/minute.
The presenter document is a separate 22-page cue book, matching slide numbers
and titles, with one main point, four speaking cues, one key qualification,
timing, and a transition. Its core timing is 49.5 minutes plus six minutes of
questions. Large type and deliberate page breaks make it usable on a second
display. Each page links to the relevant canonical article section.

Keep authoring and audit inputs private. The requested, reviewed PDF derivative
is `presentation-assets/ai-agents-in-ci-cd/presenter-notes.pdf`, served by its
explicit unlisted endpoint. Never expose the source notes, audit ledger, wiki,
or editable authoring materials through that endpoint.

## Release and handoff

The author approved the concrete article and both slide variants after reading
and testing them on September 6, 2026. The unlisted presenter PDF route is also
explicitly requested. Work is prepared locally and production-eligible. On September 6, 2026, the author explicitly authorized integration and a
production push after approving the result. The full commit message follows
the approval requirement in `AGENTS.md`, and commits use `git commit -s`.

The original checkout may advance independently. Review its current changes
before integrating this branch. Never overwrite that task's work. Private
research and user preference records are maintained in the ignored local wiki
and carried forward separately from Git integration. The lecture records,
editable notes, and validation artifacts have been copied to the primary local
checkout, preserving newer wiki entries from other work.

The separate task was integrated by rebasing onto `origin/master` at `2fb3f5a`.
The doctoral reading depth and exact-content deck revisions are complete and
approved. The presenter PDF, its unlisted route, and synchronized presenter view complete
the reading and presentation workflow. The isolated worktree remains the release preparation source until integration.

## Presenter view follow-up

After testing the PDF, the author requested a Google Slides style presenter
window because manually following two documents was cumbersome. Add a separate
presenter window that follows the projected deck's active slide and supports
navigation from either window. Notes should dominate its layout, with current
and next slide previews and timing. Keep it separate from audience fullscreen
content and preserve both original and themed slides unchanged.

Use reviewed structured cues derived from the presenter PDF, outside `public/`.
Never read the private wiki during a site build. The new presenter page is an
operational view, launched from the slide controls, and stays out of the main
navigation, feeds, and sitemap. The PDF remains unlisted at its existing URL.
No backend, hosted slide service, or new runtime dependency is needed.

Slide 5 notes now include a concise refresher on Hardy's 1988 paper: the compiler
had directory permissions for statistics, a caller redirected debugging output
to the billing file, and the compiler used the wrong source of authority. The
capability solution and AI analogy complete the cue. This changes notes only.

### Presenter synchronization contract

The audience deck owns the active slide. A per-session `BroadcastChannel`
connects it to a presenter window launched by a user gesture. The random session
identifier, slide, and deck variant are held in the fragment. Validate messages
before applying them; treat session identifiers as collision isolation, not
access control. A ready handshake and periodic state messages recover startup
races. Presenter commands route through the same slide setter used by buttons,
keyboard, and URL history, so there is one state authority and no feedback loop.

A presenter reload rejoins its session. Reloading or leaving the audience deck
ends that session, and the notes show that they are standalone. A delayed
heartbeat alone must remain recoverable, since hidden browser tabs can delay
timers; retain the channel and resynchronize when an authoritative state arrives. Closing and
reopening the popup starts a fresh session. Separate deck tabs must never
advance one another. If the browser blocks a popup or synchronization is
unavailable, offer a usable standalone notes view with explicit status. Browser
preferences determine whether the separate surface opens as a window or tab;
positioning it on the second display is a presenter action.

The presenter route keeps the site's metadata, system-aware theme, analytics,
and accessibility shell while omitting regular navigation and footer. It never
requests fullscreen. Original source images provide current and next previews
for both deck variants, labeled accordingly. Manual elapsed timing is advisory;
per-slide allocation and cumulative target derive from the cue data. Validate
and keep timer persistence local to the presenter session.

The reviewed `presenter-cues.json` asset supplies only presentation fields and
public article section links. Validate slide count, numbering, required text,
four cues per slide, positive duration, and internal article targets when reading
it during the build. Render text through Astro escaping; emit no raw cue JSON
endpoint. The 22 cue records and PDF pages were compared after the Hardy update.

### Final presenter evidence

- The author tested the presenter UI in the browser and approved its appearance.
  The original branded deck remains the primary presentation, with the same
  presenter workflow also verified for the themed deck.
- Isolated Chrome tests using the bundled Playwright runtime verified launch from
  original slide 5, bidirectional buttons and keyboard navigation, ten rapid
  right-arrow presses, Home/End bounds, popup reload/reconnection, and idle
  synchronization beyond the heartbeat watchdog interval. No dependency was added.
- Two simultaneous sessions, one original and one HTML, remained independent.
  Repeated launch focused the existing popup. Timer Start/Pause/Reset and reload
  persistence passed without double counting or cross-session state.
- The original deck entered fullscreen while the notes window remained ordinary;
  advancing from the notes updated the fullscreen audience slide. Reloading or
  closing the deck switched notes to explicit, usable standalone mode.
- Invalid fragment input retained a visible cue page. Keyboard navigation moved
  focus from an outgoing note link to the incoming notes section. Source previews
  loaded correctly. Desktop and 390-pixel mobile/light/dark screenshots were
  inspected, with no horizontal overflow. Smaller windows can scroll vertically.
- A simulated blocked popup exposed a working standalone link in a new tab while
  retaining the audience slide. Missing BroadcastChannel support also produced
  usable standalone notes. With JavaScript disabled, all 22 cue sections remained
  readable. Final browser runs reported no page errors.
- One fullscreen navigation test timed out during ongoing code edits; repeating
  against the stable implementation passed. The
  deliberate session-end behavior on deck reload was separately verified.
- `npm run check`, both builds, both site verifiers, both lecture verifiers, and
  `git diff --check` pass. Sol's final implementation review is clear. Release preparation uses `codex/ncsu-ai-agents-lecture`, based on `2fb3f5a`,
  with production push authorized by the author after review. Git history and
  the private release record identify the eventual release revision.

### Local handoff

The canonical checkout's existing wiki was merged selectively, preserving newer
unrelated records and adding the lecture context and approval. Lecture research,
cue authoring material, editable notes, rendered document checks, and browser
screenshots were retained outside the temporary worktree. Approved new website
files and presentation derivatives are part of the release commit. Dependency
installations, Astro caches, build output, and Python bytecode are regenerated
rather than copied over another checkout's local state. Private wiki and generated
files remain ignored and are never staged or deployed.
