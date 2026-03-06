# Execution Scripts

This folder contains deterministic Python scripts that perform the actual work.

## Convention

Each script should:
- Accept inputs via CLI args or environment variables
- Be independently runnable and testable
- Be well-commented
- Handle its own errors and exit with a non-zero code on failure

## Rules

- Check here first before writing a new script — reuse existing ones.
- Scripts are invoked by the orchestration layer (Claude), not run manually unless testing.
- Keep scripts focused on a single responsibility.
