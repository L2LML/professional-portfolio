# Vendo-Matic 800 — Process Documentation

Two Lean process maps that translate a working piece of software into standard process-improvement documentation — demonstrating the same shape-language, decision-mapping, and value-stream thinking used in client-facing DMAIC work, applied to a codebase instead of a business process.

The underlying software is a Java CLI vending machine simulator (Tech Elevator Module 1 capstone) that accepts money, dispenses inventory, makes change, and writes an audit trail. These two documents map it two different ways.

## What's in this folder

| File | Maps |
|---|---|
| [`operational-flow.html`](./operational-flow.html) | **The software's behavior.** Every customer-facing path through the machine — home menu, purchase sub-process, all three guard conditions on a sale (invalid code, sold out, insufficient funds), and the three points where a transaction gets written to an audit log. Standard flowchart shapes (start/end, process, decision) plus a custom "system record" shape for each audit/log event. |
| [`build-timeline.html`](./build-timeline.html) | **The build sequence.** The ten stages the software was actually constructed in, each tied to its concept and deliverable, plus a callout for a mid-build refactor (pulling change-calculation logic into its own class specifically to make it unit-testable). |

Both are self-contained HTML — open either directly in a browser, no server required.

## Why two maps

A process map of *what the software does* and a timeline of *how it got built* answer different questions for different audiences: the first is the kind of document a business stakeholder or QA reviewer would want, the second is the kind of document useful for onboarding another developer or documenting a training/mentorship engagement.

## Skills demonstrated

Process mapping · decision/guard-condition documentation · translating source code into business-readable process flow · value-stream style data-capture point tracking · technical documentation design.
