# Talks and lecture maintenance

Operational reference for the talk pages. Approval history lives outside the repository.

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


## Presenter synchronization contract

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
endpoint.
