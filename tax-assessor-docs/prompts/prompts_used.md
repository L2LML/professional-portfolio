# Prompts Used — Tax Assessor Doc Skill

> Full prompt documentation for the Tax Assessor Doc Skill.
> Part of the [@L2LML](https://github.com/L2LML) Claude AI project portfolio.

---

## Skill Trigger Description (SKILL.md frontmatter)

```
Use this skill whenever the user uploads or mentions ANY document, photo, estimate,
receipt, invoice, contract, or bill related to home repairs, damage, or a tax appeal
— even if they just say "here's another one", "I found the quote", "adding a document",
or "scan this". Also triggers for phrases like "I found the driveway quote",
"here's the fireplace estimate", "sunroom receipt", or any mention of submitting
documents to the assessor.
```

**Why it works:** Broad casual-language triggers prevent the skill from missing
uploads phrased informally. Users in the middle of a task say "here's another one"
— not "please process this document."

---

## Prompt 1: Document Extraction (PDF / typed)

```
Read this document and extract:
- Vendor or contractor name and contact info
- Date of document
- Document type: estimate / invoice / contract / receipt / insurance doc
- Dollar amount(s)
- Scope of work — what damage or repair does it describe?

Present a one-line confirmation before logging:
"[Vendor] — $[Amount] — [Type] → Logging as Exhibit [X]. Correct?"
```

**When to use:** Any PDF, typed estimate, invoice, or contract upload
**Why it works:** Structured extraction + confirmation step prevents silent errors
and builds trust in the automation
**Variables:** `[Vendor]`, `[Amount]`, `[Type]`, `[Exhibit Letter]`

---

## Prompt 2: Photo Damage Analysis

```
Examine this photo and identify:
- Is this a damage photo or a document photo?
- If damage: describe what the damage shows — be specific and factual
- Note which area of the property it depicts (basement, roof, driveway, etc.)
- Rate relevance for a property value appeal: HIGH / MEDIUM / LOW
```

**When to use:** Any uploaded image that may show property damage
**Why it works:** Forces factual, specific description rather than vague output.
"Structural cracking in fireplace surround with visible separation from wall"
is far more useful in an appeal than "picture of fireplace."

---

## Prompt 3: Email Generation

```
Generate the exact ready-to-send email for this document submission.
Use this format:
- Standard subject line with appeal reference
- Exhibit letter and document name
- One sentence describing what the document proves for the appeal
- Professional closing with contact info

Output as copy-paste ready text only — no explanation needed.
```

**When to use:** After every successful document log
**Why it works:** Copy-paste ready output removes friction between
"I have this document" and "I sent this document." Friction kills follow-through.

---

## Prompt 4: Running Total Update

```
After logging this document, update and display the running damage total table.
Show each damage category, its documented cost range, and submission status.
Always show the updated TOTAL at the bottom.
```

**When to use:** After every document log
**Why it works:** Making the cumulative damage amount visible after each upload
motivated finding more documents. Concrete numbers change behavior.

---

## Iteration History

| Version | Change | Reason |
|---------|--------|--------|
| v1 | Initial skill with basic extraction | First working version |
| v2 | Added casual language triggers | Skill wasn't firing on informal uploads |
| v3 | Added duplicate detection | Same docs were being logged multiple times across sessions |
| v4 | Added running total display after every log | User wasn't seeing the cumulative picture |
| v5 | Separated photo vs PDF logic paths | Photos were getting PDF-style extraction which produced poor results |

---

*Part of [@L2LML](https://github.com/L2LML)'s Claude AI project portfolio*
