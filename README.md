# IELTS Reading Review Assistant

An offline-first reading review tool that helps IELTS learners turn a passage and their mistakes into organised study material.

This repository is a Software Engineering course project developed by **D1-Team10** at Macau University of Science and Technology. The first release focuses on transparent, rule-based processing that can run without an AI service or API key.

## The Problem

IELTS learners often review vocabulary, difficult sentences, answer keys, and notes in separate places. This makes it hard to decide which words deserve attention, preserve useful sentence notes, and discover recurring causes of mistakes.

The project brings these activities into one passage-centred workspace.

## Core Features

### 1. Priority Vocabulary and Wordbook

After the learner pastes an English passage, the system can:

- recommend up to **20** words worth reviewing;
- merge case variants and count occurrences;
- filter common basic words and words marked as mastered;
- show the source sentences and a clear recommendation reason;
- display Chinese meanings from a local dictionary;
- save words to a personal wordbook;
- edit personal meanings and update mastery status.

The recommendations are learning priorities selected by rules. They are not guaranteed IELTS examination words.

### 2. Long-Sentence Reading Hints

The planned sentence module will:

- select up to **5** potentially difficult sentences;
- show each sentence's location and selection reason;
- highlight common connectives such as `although`, `because`, and `which`;
- provide punctuation- and connective-based reading segments;
- let learners save translations and reading notes.

The reading hints are aids rather than verified grammatical analyses or generated translations.

### 3. Mistake Records and Review Advice

The planned mistake-review module will:

- store a question, the learner's answer, and one or more acceptable answers;
- compare answers using explicit rules;
- keep optional choices, source evidence, reasoning, and notes together;
- let learners select a cause such as vocabulary, sentence understanding, evidence location, or overlooked qualifiers;
- map the selected cause to prepared review advice;
- count confirmed causes and show the learner's most frequent issues.

The first release will not infer mistake causes automatically. The learner confirms the category.

## Current Status

The repository currently contains the shared project scaffold and course documentation. A working vocabulary prototype has been developed locally and is being prepared for integration. The sentence and mistake-review modules remain planned work.

| Area | Status |
| --- | --- |
| Requirements and project documents | In progress |
| Vocabulary recommendation rules | Prototype implemented |
| Local English-Chinese dictionary lookup | Prototype implemented |
| Wordbook and mastery tracking | Prototype implemented |
| Long-sentence reading hints | Planned |
| Mistake records and review advice | Planned |
| Integrated application and user evaluation | Planned |

## Vocabulary Prototype Design

The vocabulary prototype uses:

- **Python** for text processing and application logic;
- **Streamlit** for the local web interface;
- **SQLite** for passages, wordbook entries, source sentences, and mastery states;
- [ECDICT](https://github.com/skywind3000/ECDICT) for offline English-Chinese dictionary data.

The first recommendation algorithm is deliberately simple and explainable:

1. Extract English tokens while retaining internal apostrophes.
2. Normalise tokens to lowercase and merge case variants.
3. Count occurrences and retain their source sentences.
4. Remove basic words and learner-mastered words.
5. Rank by passage frequency, using first occurrence to break ties.
6. Return at most 20 eligible words.

Different word forms are not comprehensively merged in the first release. For example, `study` and `studies` may remain separate entries.

## Planned Project Structure

```text
.
├── frontend/                  # User interface
├── backend/                   # API and application services
├── analysis/
│   ├── vocabulary/           # Vocabulary recommendation
│   ├── sentences/            # Long-sentence selection and hints
│   ├── error-review/         # Answer comparison and mistake records
│   └── recommendations/      # Rule-based review suggestions
├── tests/                     # Unit, integration, and evaluation tests
└── docs/                      # Proposal, requirements, design, and planning
```

The structure will evolve as the local prototypes are integrated.

## Development Workflow

- `main`: stable project baseline and releases;
- `develop`: integration of reviewed work;
- feature branches: isolated implementation work merged into `develop` through pull requests.

New work should normally start from `develop`. A feature should be tested and reviewed before it is merged.

## First-Release Boundaries

- Single-user, device-local storage
- Pasted English text as the primary input
- Maximum input: 50,000 characters and 5,000 English words per passage
- Maximum output: 20 vocabulary recommendations and 5 sentence candidates
- No AI key or external language model required
- No automatic translation, grammatical parsing, pronoun-reference resolution, or mistake-cause inference
- No cloud synchronisation or cross-device account support in the first release

## Team Responsibilities

The three members of D1-Team10 take primary ownership of the vocabulary and wordbook module, the long-sentence reading-hints module, and the mistake-review module respectively. All members participate in requirements analysis, design, implementation, testing, documentation, and presentation.

## Data and Limitations

Dictionary meanings may contain multiple senses, so learners should choose the meaning that fits the source sentence. Missing entries must be shown explicitly rather than replaced with generated definitions.

The vocabulary exclusion list is a project-maintained baseline, not an official IELTS word list. Rule-selected vocabulary must not be presented as guaranteed examination vocabulary or as a score-improvement guarantee.

Third-party datasets and libraries will retain their original notices and licences when added to this repository.

## Documentation

Project materials are maintained in [`docs/`](docs/):

- [Project proposal](docs/proposal.md)
- [User requirements](docs/requirements.md)
- [System design](docs/design.md)
- [Project plan](docs/project-plan.md)
- [Test plan](docs/test-plan.md)

## Licence

A project licence has not yet been selected. Until a licence file is added, no permission to copy, modify, or redistribute the project source code is granted. Third-party resources remain subject to their own licences.
