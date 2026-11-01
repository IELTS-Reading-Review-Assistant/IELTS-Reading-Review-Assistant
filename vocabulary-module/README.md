# Vocabulary Module — Version 3.0.0

This is the working vocabulary and wordbook module for D1-Team10's IELTS Reading Review Assistant. It was designed and developed by **Liu Yudan**. The module uses transparent rules and runs locally without an AI API key after the dictionary has been installed.

## Features

- Paste an English passage and recommend up to 20 learning-priority words.
- Merge case variants, count occurrences, and retain source sentences.
- Filter project-defined basic words and words marked as mastered.
- Display offline Chinese definitions from ECDICT, or show a missing-definition notice.
- Save words, edit personal meanings, and update mastery status.
- Save and reopen passages using device-local SQLite storage.

The recommendations are learning priorities, not guaranteed IELTS examination words. Different word forms are not comprehensively merged, and dictionary meanings are not automatically disambiguated from context.

## Windows Setup

Install Python 3.10 or later, open PowerShell in this directory, and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

The setup script creates a virtual environment, installs Streamlit, downloads ECDICT, and builds the local dictionary database. The downloaded CSV and generated databases are excluded from Git.

## Start

Double-click `start.bat`, or run:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

## Test

After setup, run:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tests\check_ui.py
```

## Main Files

- `app.py`: Streamlit user interface.
- `vocabulary.py`: rule-based recommendation logic, independent of the UI.
- `storage.py`: SQLite learning records and dictionary lookup.
- `data/basic_words.txt`: project-maintained exclusion list.
- `CHANGELOG.md`: staged development history.

`recommend(text, mastered)` returns each word, its count, the recommendation reason, and its source sentences. This interface can be reused when the vocabulary module is integrated with the sentence-analysis and mistake-review modules.

## Local Data and Boundaries

Learning records are stored in `data/learning.db`. The first release is single-user and device-local, with no account separation or cloud synchronisation. Passage input is limited to 50,000 characters and 5,000 English words; personal meanings are limited to 2,000 characters.

ECDICT is distributed under the MIT licence retained in `third_party/ECDICT-LICENSE.txt`. The project-maintained basic-word list is not an official IELTS vocabulary list.
