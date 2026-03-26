---
name: tech-writer
description: Technical documentation maintenance for the article crawler project. Use when updating documentation after implementation changes, keeping `documentation/` organized, and logging documentation decisions.
---

# Tech Writer

## Overview

Maintain accurate, structured documentation across `documentation/` and keep it in sync with the implementation.

## Workflow

1. **Gather the final implementation details.**
   - Validate behavior, constraints, data flow, limitations, and trade-offs.
   - For site-specific changes: check search URL construction, result parsing, pagination, and paywall handling.
2. **Update documentation.**
   - Add missing content, fix outdated sections, and remove obsolete material.
   - When crawling strategies or paywall approaches change, update the relevant sections.
3. **Evaluate whether a decision record is needed** (see below).
4. **Keep structure and terminology consistent.**
   - Use consistent terminology: Keyword-Paar, Suchbegriff, Artikelmetadaten, Deduplizierung, Character Count.
5. **Refactor documentation over time.**
   - Extract shared concepts, reduce duplication, and improve navigation.

## Decision Records

After updating documentation for a significant change, evaluate whether a decision record should be created. A record is warranted when:

- A new library or tool is introduced
- A site-specific crawling strategy changes significantly
- A paywall bypass approach is added or removed
- A non-obvious design decision with meaningful trade-offs is made

Create decision records in `documentation/decisions/` with the naming convention `NNNN-short-title.md`.

## Formats

- Use Markdown as the primary format.
- Use Mermaid diagrams for data flow or architecture visualization where helpful.
