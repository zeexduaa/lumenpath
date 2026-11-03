# Roadmap

Where Lumenpath is going. Sizes are rough guesses (S = a few hours, M = about a day,
L = several days, XL = a week or more). Order may change as I play-test.

## ✅ v0.1: the core puzzle (released)

- Beam tracing with turnable and fixed mirrors, walls, crystals and multiple emitters
- 10 hand-made levels, each checked by the solver (solvable, not pre-solved, correct par)
- Undo, restart, hints, saved progress and best scores
- Plain-text level format and `--levels` for custom level folders

## v0.2: feel and polish

- [ ] **Animations**: mirrors rotate smoothly, beams sweep out from the emitter, crystals pulse when lit (M)
- [ ] **Sound effects** for turning, lighting a crystal and solving, with a mute key (M)
- [ ] **Level select screen** showing solved levels, best moves and stars (M)
- [ ] **Star ratings**: 3 stars at par, 2 within +2, 1 for any solve (S)
- [ ] **Resizable window** and scaling for small and high-DPI screens (M)
- [ ] **Colour-blind friendly palette** and shapes, not just colours, for lit and unlit crystals (S)

## v0.3: new mechanics

- [ ] **Coloured light**: emitters of different colours, crystals that need a specific colour (L)
- [ ] **Filters** that only let one colour through (M)
- [ ] **Beam splitters** that send light two ways at once (M)
- [ ] **Portals** that move a beam across the board (M)
- [ ] **Mirrors with 4 positions** (`/`, `\`, `-`, `|`) and sliding blocks (L)
- [ ] A 25-level campaign that introduces each mechanic one at a time (L)

## v0.4: making levels

- [ ] **In-game level editor**: paint tiles, test-play, save to `.txt` (XL)
- [ ] **Faster solver**: search along the beam instead of trying every mirror combination, so big levels solve instantly (L)
- [ ] **Level generator**: create random levels, then use the solver to keep only interesting ones (unique solution, par within a range) (L)
- [ ] **Daily puzzle** generated from the date, so everyone gets the same one (M)
- [ ] Level pack format (folder + metadata) and `lumenpath --pack` (S)

## v1.0: release

- [ ] **Browser version** with pygbag, playable on itch.io and GitHub Pages (L)
- [ ] **Standalone downloads** for Windows, macOS and Linux built in CI (PyInstaller) (M)
- [ ] **Publish to PyPI** with trusted publishing on tagged releases (S)
- [ ] **Controller and keyboard-only play** (move a cursor, turn with a key) (M)
- [ ] Settings screen: volume, colours, animation speed (M)

## Ongoing quality

- [ ] Type-checking (mypy) and linting (ruff) in CI
- [ ] Screenshot tests: render each level headlessly and compare against saved images
- [ ] Property-based tests for beam tracing (Hypothesis)
- [ ] Play-testing notes for each level: difficulty curve, where people get stuck
