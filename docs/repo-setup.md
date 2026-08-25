# How this repo is set up

Notes to myself, written the first time I set a project up from scratch instead
of inheriting one. Two parts: what's in here and why, then what the bigger
machinery is for and when it would start to matter.

## The pieces

| File | What it does |
|---|---|
| `.github/workflows/ci.yml` | On every PR: builds the site, checks every internal link. This is the gate. |
| `.github/workflows/deploy.yml` | On every push to `main`: builds and publishes to GitHub Pages. |
| `.github/dependabot.yml` | Opens a PR monthly when a dependency has a new version. |
| `scripts/check-links.mjs` | Walks `dist/` and fails if any internal link points at a page that doesn't exist. |
| `.nvmrc` | Pins Node 24 (the current LTS). CI reads this file, so CI and my laptop can't drift apart. |
| `package-lock.json` | Pins the exact version of every dependency, including transitive ones. |

### What counts as a "test" here

There's no unit test suite, because there's almost no logic to unit-test. The
things that actually break on a content site are different, and `npm test`
covers them:

- **The build fails** if a post's frontmatter is malformed — a bad date, a
  missing title, `seriesPart` as a string instead of a number. That validation
  is the Zod schema in `src/content.config.ts`, and it runs on every build for
  free. It's a real test; it just doesn't look like one.
- **The link checker fails** if an internal link 404s. This is the one that
  earns its place: posts cross-link to each other, and renaming a file silently
  breaks every link pointing at its old slug. Nothing else would catch that
  until a reader hit it.

Run it locally the same way CI does:

```
npm ci        # exactly what the lockfile pins, not "whatever resolves today"
npm test      # build + link check
```

`npm ci` vs `npm install` is worth internalizing: `install` is allowed to pick
newer versions and rewrite the lockfile, `ci` installs exactly what's pinned and
errors if the lockfile disagrees with `package.json`. Locally you want
`install`; in CI you always want `ci`, or you're not testing the same tree twice.

## Two things to click, once

**1. Point Pages at Actions.** Settings → Pages → Source → **GitHub Actions**.
If it says "Deploy from a branch" instead, `deploy.yml` runs, goes green, and
publishes nothing — a genuinely confusing failure mode because nothing errors.

**2. Protect `main` with a ruleset.** Settings → Rules → Rulesets → New ruleset
→ New branch ruleset. Target the default branch, then enable:

- **Require a pull request before merging** — approvals required: 0. Solo, there
  is nobody to approve. The point isn't review, it's that a PR is what gives CI
  something to run against before the change lands.
- **Require status checks to pass** → add `build and check links`. The check has
  to have run at least once before it shows up in that search box, so open a
  throwaway PR first if it isn't there.
- **Block force pushes** — on by default, leave it.

One honest caveat: this locks you out of pushing straight to `main`. If that
turns out to be more friction than it's worth for a typo fix, add **Repository
admin** to the ruleset's bypass list. You keep the guardrail as the default path
and can still step around it deliberately. That's a reasonable place for a solo
repo to land — the rule exists to stop accidents, not to stop you.

Rulesets are the current version of this feature; you'll see older docs and
tutorials talking about "branch protection rules," which are the previous
generation. GitHub is migrating existing ones over. Use rulesets for anything new.

## The day-to-day loop

```
git checkout -b fix-the-radiator-table
# edit, then:
npm test                      # catch it before CI does
git commit -am "Fix radiator area at 127C"
git push -u origin fix-the-radiator-table
gh pr create --fill           # or click the link the push prints
```

CI runs, goes green, you merge, `deploy.yml` publishes. About a minute end to end.

## The machinery you've used but never set up

Everything above is what a one-person repo actually needs. Here's what the rest
of it is for, since you'll keep running into it.

**Required status checks** — you now have these. The idea generalizes: a big
repo has ten or twenty, and the interesting question becomes which ones are
*required* (block the merge) versus merely reported. Required checks are a
budget: every one you add is time every PR waits.

**Merge queue** — **not available to you.** It needs an organization-owned
repository; yours is user-owned, so the setting won't appear regardless of plan.
Worth understanding anyway, because it's the thing those `1-merge-queue`-style
names come from. The problem it solves: CI tested your PR against `main` as it
was when you opened it. If four PRs merge in between, the tree you tested no
longer exists, and two individually-green changes can combine into a red `main`
— "semantic conflict." A merge queue re-tests each PR against the *actual*
tree it's about to land on, batching where it can. That only pays for itself
when PRs land faster than CI takes to run. On a repo with one author it is pure
overhead: your PR is always tested against the current `main`, because nothing
else moves.

**CODEOWNERS** — a file mapping paths to people, so touching `src/lib/` auto-
requests review from whoever owns it. Solves "who do I even ask about this."
Needs more than one person to mean anything.

**Tags and releases** — a tag is a permanent name for a commit; a Release is a
tag plus notes and downloadable artifacts. They exist because consumers need to
pin a version — `astro@^7.2.6` in `package.json` works because Astro tags
releases. Nothing consumes this site, so the deployed commit is always just the
tip of `main` and tags would be decoration. If you ever want one anyway:

```
git tag -a v1.0.0 -m "First two posts published"
git push origin v1.0.0
```

The `v1.0.0` shape is semver: major.minor.patch, where major means "I broke
something you depended on." That contract is between a library and its users,
which is why it doesn't map cleanly onto a blog.

**Environments** — `deploy.yml` already declares `environment: github-pages`.
In a bigger setup an environment carries secrets and approval gates, so
deploying to prod requires a human to click. Here it's just where Pages hangs
its URL.

The pattern in all of these: they're coordination tools. They solve problems
created by *other people* changing the same code at the same time. Adopting them
on a solo repo doesn't make it more rigorous, it just makes it slower. The two
that pay off at any size are the ones you now have — the build has to pass, and
`main` is never edited by accident.
