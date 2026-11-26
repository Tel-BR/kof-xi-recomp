# Release readiness review — 2026-11-26

Reviewed against `b55b1f4` and GitHub issues #1–#18. This is a triage snapshot, not a release certification. The local `main` and `fix/black-screen` point to that commit; publishing the integrated branch is a separate step.

## Owner decisions — tracker synchronization

The owner reviewed these issues on 2026-11-26. The requested reopenings, closures and updates were synchronized to GitHub after approval. Complementary spec #19 and tickets #20–#28 cover the new native-experience work; joystick verification was added to #10.

- #1: retain complete fight and rollback-ready architecture.
- #2: keep closed.
- #3: keep closed; validate symbol export during the clean rebuild.
- #4: reopen to require a clean GPU rebuild.
- #5: reopen and require comparison against the Reference Emulator for the current GPU runtime.
- #6: retain rollback, synctest, and unlock requirements.
- #7: investigate whether the interim IOP fixes apply to the current runtime.
- #8: update acceptance criteria for the current Fixer-based GPU architecture; retain relevant verification and attribution criteria after review.
- #9: review SPU2 criteria and establish what remains with the current runtime.
- #10: retain and verify all controller and memory-card criteria.
- #11: retire the existing replay as a current-build verification artifact and record a new replay for the current build. Verify whether the reported formatting warnings reproduce with it; do not delete the old recording without a separate decision.
- #12: keep closed; this concerns the character-selection screen after selecting ARCADE PLAY.
- #13: close; the owner accepts the existing replay as sufficient for this issue. It does not establish separate capture-gated keyboard coverage.
- #14: close at the owner's direction; the owner accepts the current visuals without requiring the previously specified comparison for this issue.
- #15: close at the owner's direction; the owner accepts current audio without requiring the previously specified scene-by-scene checks for this issue.
- #16: retain the integrated test. The transition after fighter-order selection should match the PS2 duration and be skippable with a button. Measure the reference duration rather than choosing a fixed value without evidence; track this transition request separately from the test gate.
- #17: close at the owner's direction; create a separate issue to complete and verify a fight using a joystick. The existing replay does not independently prove the original keyboard acceptance gate.
- #18: keep open for the reported visual defect: the circular THE KING OF FIGHTERS text appears below the emblem and should appear above it. Investigate layer/depth ordering and verify against the owner's expected result; do not assume the previously noted depth observation is the cause.

The issue summaries below record the original review and can differ from these subsequent owner decisions.

| Issue | Review |
| --- | --- |
| #1 | Open: the complete-fight and rollback-ready specification is not yet demonstrated end to end. Some implementation details in the original specification predate the GPU runtime. |
| #2 | Closed: extraction and validation were delivered; revalidate the clean setup path before release. |
| #3 | Closed: symbol export was delivered. The code boundary has since changed; validate a clean export as part of a clean rebuild. |
| #4 | Closed: the original runtime milestone was delivered. The GPU build has been rebuilt incrementally; a clean GPU rebuild remains unverified. |
| #5 | Closed, but its earlier completion comment should not be taken as proof of GPU runtime parity with the reference. The latest milestone explicitly says a full state-hash or frame-exact comparison was not performed. Review the original acceptance criteria and verify or reopen as appropriate. |
| #6 | Open: snapshot/restore, rollback synctest and unlock requirements remain to be demonstrated. |
| #7 | Open: the interim fixes targeted an older runtime path. Reassess applicability and acceptance against the current Fixer build rather than assuming the old branch is integrated. |
| #8 | Open: the current build uses the Fixer hardware GS, but the issue specifies a narrower port, renderer isolation, a guard, measurements and attribution. Reconcile those criteria with the adopted architecture. |
| #9 | Open: the current Fixer has SPU2 and the milestone records substantial audio progress; the issue's remaining technical and measurement criteria still need checking. |
| #10 | Open: replay evidence covers both ports synthetically; two-player interactive input, once-per-frame sampling, module loading and memory-card behavior remain to be verified. |
| #11 | Open: the milestone reports late guest `vfprintf` warnings; verify the play configuration and the original no-error criterion. |
| #12 | Closed: mode screen visibility was verified by the tracked loop; retain regression coverage. |
| #13 | Open: the full reference replay reached a fight, but this does not establish the requested keyboard-driven, capture-gated trio/order/preload milestones. |
| #14 | Open: replay reached a fight, but stage and opening parity and the requested reference comparison are not certified by that fact. |
| #15 | Open: the latest milestone reports 47/47 active seconds, high audio correlation and owner listening confirmation. Check menu, attract and fight scenes, effects, synchronization and the end-to-end gate before closure; the original intermittent-audio baseline is historical. |
| #16 | Open: the single end-to-end gate through preload, including graphics, audio and performance, has not been certified. |
| #17 | Open: replaying a fight is not a keyboard-driven completed-fight certification; verify the result screen and all gate criteria. |
| #18 | Open: geometry was restored and validated; same-moment palette comparison and the remaining parity checklist still require review. Its comment already records the partial result. |

## Release preparation

- Reproduce the GPU build from a fresh configured checkout using only the user's disc; preserve all generated material and captures under `private/`.
- Complete the applicable open issues and reconcile obsolete architecture-specific criteria before closing them.
- Run the full playable-loop gate, including keyboard fight completion, visuals, audio, performance and reference comparisons, and record the evidence without publishing game data.
- Confirm licensing and third-party attribution for the actual distributed components, and verify the repository and release package contain no game data.
- Publish the integrated branch only after reviewing the exact commits and the intended remote destination.
