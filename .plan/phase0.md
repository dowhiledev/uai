# Phase 0: Repository Scaffold — Detailed Considerations

This document outlines all considerations, decisions, and best practices for scaffolding the Unified Agent Interface (UAI) Python package. Use this as a checklist and reference before starting implementation.

---

## 1. Directory Structure
- Use `src/uai/` as the main package directory to avoid import conflicts and support editable installs.
- Create submodules:
  - `adapters/` for framework-specific adapters
  - `core/` for core abstractions and utilities
  - `__init__.py` in each directory for proper module discovery
- Add top-level directories:
  - `tests/` for unit and integration tests
  - `examples/` for usage demonstrations and sample scripts
  - `.plan/` for planning and design docs

## 2. pyproject.toml & Metadata
- Use PEP 621-compliant `pyproject.toml` for build system and metadata
- Specify dependencies (e.g., CrewAI, LangChain, FastAPI, etc.) as extras or optional
- Set up project name, description, authors, license, and versioning
- Configure entry points for plugin registry (update to match package name)
- Use `hatchling` as build-backend (see pyproject.toml)
- Use `uv` for dependency management and installation
- Package name is `unified-agent-interface` (not `uai`)

## 3. README.md
- Clearly state project purpose, scope, and usage
- Include quickstart example for `wrap_agent()`
- Document supported frameworks and extensibility
- Add badges for build status, license, and PyPI (if applicable)

## 4. Version Control & .gitignore
- Add `.gitignore` for Python, virtualenv, and editor artifacts
- Consider `.gitattributes` for consistent line endings
- Use semantic commit messages and conventional branching (e.g., `main`, `dev`, feature branches)

## 5. Testing Infrastructure
- Set up `pytest` as the default test runner
- Add initial test files for core abstractions
- Consider coverage tools (e.g., `pytest-cov`)
- Plan for CI integration (GitHub Actions, etc.)

## 6. Example Scripts & Notebooks
- Provide minimal examples for each supported framework (CrewAI, LangChain, etc.)
- Add sample notebook for interactive exploration
- Document how to run examples and tests

## 7. Documentation Planning
- Decide on documentation generator (e.g., mkdocs, Sphinx)
- Plan for API reference, usage guides, and extensibility docs
- Structure docs for incremental updates as new adapters are added

## 8. Licensing & Compliance
- Choose a permissive license (e.g., MIT, Apache-2.0) and include in root
- Document third-party dependencies and their licenses
- Add copyright notice to source files

## 9. Extensibility Hooks
- Scaffold plugin registry via `entry_points` in `pyproject.toml`
- Plan for external adapter discovery and registration

## 10. Initial Milestones
- Ensure all scaffolding is in place before starting Phase 1
- Validate imports, test discovery, and editable install (`pip install -e .`)
- Confirm CI passes with initial empty package

---

## Checklist
- [x] Directory structure created
- [x] pyproject.toml written
- [x] README.md drafted
- [x] .gitignore and version control set up
- [x] Initial tests and CI configured
- [ ] Example scripts added
- [ ] Documentation plan outlined
- [x] License included
- [ ] Plugin registry scaffolded
- [ ] Milestones validated

---

## Notes
- Keep the initial commit minimal and focused on structure
- Avoid adding framework-specific code until abstractions are ready
- Use this document to guide and review the initial repo setup
- Dependency management is handled via `uv` (see https://github.com/astral-sh/uv)
- Package name is `unified-agent-interface` throughout all configs and docs
