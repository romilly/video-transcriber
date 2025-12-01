# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**video-transcriber** - A Python project following TDD principles.

## Core Architecture

### Key Components
- **video_transcriber/main.py** - Main application logic

## Development Approach

**Strict Test-Driven Development (TDD)** - All development follows the Red-Green-Refactor cycle:

1. **Red**: Write a failing test for new functionality
2. **Green**: Write minimal code to make the test pass
3. **Commit**: Commit the passing test and implementation
4. **Refactor** (if needed): Improve test or code while keeping tests green
5. **Retest**: Ensure all tests still pass after refactoring
6. **Commit**: Commit the refactored code
7. **Repeat**: Go back to step 4 for further refactoring or step 1 for next feature

### TDD Workflow Commands

```bash
# Install package in editable mode (required for development)
pip install -e .

# Install with test dependencies
pip install -e .[test]

# TDD Cycle Commands
# 1. Write test, verify it fails
pytest tests/test_new_feature.py::test_specific_function -v

# 2. Run specific test during development
pytest tests/test_new_feature.py::test_specific_function -v

# 3. Run all tests to ensure no regressions
pytest

# 4. Commit after each passing test
git add . && git commit -m "Add feature X with passing test"

# Other useful test commands
pytest -v
pytest -k "test_name_pattern" -v
```

### TDD Guidelines

- **Write the simplest test that can fail first**
- **Write only enough code to make the test pass**
- **Refactor after each green test while keeping all tests passing**
- **Commit after every successful test cycle**
- **One test per commit** - keeps git history clean and focused
- **Test file naming**: `test_[feature_name].py`
- **Test method naming**: `test_[specific_behavior]`

## Testing Structure

Test data in `tests/data/`, output in `tests/output/`.

## Key Dependencies

- **pytest** (>=7.0.0) - Testing framework