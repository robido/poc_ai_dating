# Agent Guidelines

This project strives for a clean, maintainable codebase that stays manageable for
limited-context AI agents even as the code grows. Contributors should:

- Keep files focused and small, favoring single responsibility per module.
- Follow DRY (Don't Repeat Yourself) principles and avoid duplication.
- Write unit tests whenever feasible to validate new behavior or guard against
  regressions.
- Prioritize simple, scalable architecture so modules remain easy to load within
  small context windows.

These practices help maintain long-term quality and keep the codebase easy to
navigate for both humans and AI.

## Business Context

TalkMatch is an AI-assisted dating app prototype that replaces swiping with a
single, continuous chat. An "AI ambassador" greets users, learns preferences,
and transitions conversations toward real human matches. This repository hosts
the Phase 0 local proof of concept: a simple Python GUI demo with fake personas
and basic matchmaking to validate the concept and gather early feedback.

## Repository Overview

- `AGENTS.md` – project guidelines.
- `README.md` – specification and instructions for the demo.
- `requirements.txt` – Python dependencies.
- `main.py` – launches the control-panel GUI.

### talkmatch package
- `talkmatch/__init__.py` – package marker.
- `talkmatch/ai.py` – OpenAI chat client wrapper.
- `talkmatch/ambassador_role.txt` – system prompt for the ambassador persona.
- `talkmatch/build_profile.txt` – prompt template for updating user profiles.
- `talkmatch/chat.py` – conversation state management and message routing.
- `talkmatch/fake_user.py` – scripted fake user replies.
- `talkmatch/greeting_template.txt` – template used to greet personas.
- `talkmatch/matcher.py` – compute and store compatibility scores.
- `talkmatch/personas.py` – load persona descriptions and generate system prompts.
- `talkmatch/profile.py` – backward-compatible import exposing `ProfileStore`.

#### GUI
- `talkmatch/gui/__init__.py` – GUI package marker.
- `talkmatch/gui/chat_box.py` – chat window interface for a persona.
- `talkmatch/gui/control_panel.py` – control panel managing sessions and matching.

#### Storage
- `talkmatch/storage/__init__.py` – data directory setup and export of stores.
- `talkmatch/storage/chats.py` – persist chat histories.
- `talkmatch/storage/match_matrix.py` – persist match score matrix.
- `talkmatch/storage/message_counts.py` – track message counts between users.
- `talkmatch/storage/profiles.py` – build and store user profiles.

#### Persona descriptions
- `talkmatch/persona_descriptions/*.txt` – text files describing each persona.

### Tests
- `tests/test_ai_client.py` – tests the AI client wrapper.
- `tests/test_chat_session.py` – tests chat session logic and persistence.
- `tests/test_matcher.py` – tests compatibility scoring and persistence.
- `tests/test_profile_store.py` – tests profile store prompts.

Run `pytest` to execute the test suite.
