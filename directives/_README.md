# Directives

This folder contains SOPs (Standard Operating Procedures) for the CloudPulse agent.

## Convention

Each directive is a Markdown file that defines:
- **Objective** — what the task accomplishes
- **Inputs** — required parameters or data
- **Tools/Scripts** — which `execution/` scripts to call
- **Outputs** — expected results or deliverables
- **Edge Cases** — known failure modes and how to handle them

## Rules

- Directives are living documents — update them as you learn from errors or API changes.
- Do NOT delete or overwrite a directive without user approval.
- Name files descriptively: `scrape_website.md`, `generate_report.md`, etc.
