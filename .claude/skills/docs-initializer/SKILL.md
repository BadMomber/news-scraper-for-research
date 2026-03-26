---
name: docs-initializer
description: Documentation bootstrap for the article crawler project. Use when creating or organizing a `documentation/` folder and iteratively filling topics by coordinating with the tech-writer skill and asking the user for missing domain knowledge.
---

# Docs Initializer

## Overview

Create a maintainable documentation structure for the article crawler (searching taz.de, zeit.de, heise.de for keyword-matched articles) and populate it iteratively using tech-writer guidance and user input.

## Domain Context

The project is a Python crawler that:

- Searches three German news websites (taz.de, zeit.de, heise.de) using their built-in search functions
- Uses 17 keyword pairs across 3 categories (Grok-Skandale, Intersektion KI & Grok, Meta-Diskurs)
- Restricts results to a specific date range
- Extracts article metadata (date, link, title, author, character count)
- Deduplicates results by article title and combines search terms
- Handles paywalls with a multi-stage fallback strategy
- Outputs a UTF-8 encoded CSV

## Tech Stack

- **Language:** Python >= 3.10
- **HTTP:** requests / httpx
- **Parsing:** BeautifulSoup / lxml
- **Testing:** pytest
- **Output:** CSV (stdlib)

## Workflow

1. **Detect documentation state.**
   - If `documentation/` does not exist, create it.
   - If it exists, assess gaps and structure quality.
2. **Discover topics with tech-writer.**
   - Use tech-writer to identify required topics: architecture, site-specific crawling strategies, paywall handling, data pipeline.
   - Prioritize site-specific search mechanics and paywall strategies.
3. **Ask the user for domain knowledge.**
   - Inquire about domain rules and constraints not derivable from code.
   - Ask about search behavior expectations, deduplication edge cases, and desired error handling.
4. **Define documentation structure.**
   - Use clear, stable sections and avoid deep nesting.
   - Keep it simple — this is a focused tool, not a large application.
5. **Populate topics iteratively.**
   - For each topic, consult tech-writer to draft content.
   - Adjust structure as new information emerges.
6. **Validate completeness.**
   - Documentation is ready when all important topics are covered in sufficient detail.

## Excluded Topics

- **Project structure / file layout** — Developers can navigate the codebase directly.
- **Dependency version lists** — These belong in `requirements.txt` or `pyproject.toml`.
