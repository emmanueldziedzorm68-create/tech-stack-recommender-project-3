# Project 3: Tech Stack Recommender

This project implements the capstone in the supplied Artificial Intelligence Project 3 document: take at least three skills, use content-based TF-IDF and cosine similarity, and return the top three matching career paths with associated tools.

## Run

Open `index.html` directly in a modern browser to use the standalone app. The skill catalogue and matching logic are embedded: no running server or API connection is required. Static previews also work.

The Python CLI and optional local server require Python 3.10 or newer. No third-party packages are needed.

From this project folder:

```powershell
python app.py
```

Open http://127.0.0.1:8000 in a browser. Stop the server with Ctrl+C. If the port is busy, use `python app.py --port 8001` and open that port instead.

For a command-line demonstration:

```powershell
python recommender.py --skills "Python, Cloud Computing, Automation"
python recommender.py --skills "SQL, Statistics, Data Analysis" --json
python -m unittest -v
```

Run `python recommender.py` without arguments for an interactive prompt.

## Data provenance and scope

`raw_skills.csv` is an authored educational sample containing 18 technology roles. It was created for this demonstration; it is not the missing source dataset mentioned in the assignment, a verified job-market dataset, or extracted from the supplied spreadsheet. The attached retail-order spreadsheet is not used, following the decision to pursue the tech stack capstone.

The CSV has four columns: `role`, semicolon-separated `skills`, semicolon-separated `tools`, and `description`. Tools and descriptions are displayed to explain results; only skills affect ranking. Replace or extend this file to use an approved skills dataset with the same schema. Role names must be unique, and every role needs skills.

After editing the CSV, aliases in `recommender.py`, or `browser_engine.js`, run `python build_page.py` to refresh the embedded browser catalogue and engine. Reload the page afterward. The browser uses the same IDF weights as Python. Equal per-vector TF factors cancel in its cosine calculation, giving equivalent scores.

## How it works

1. **Ingestion:** accept comma-separated skills; normalize whitespace and case; map a small explicit alias dictionary to canonical terms; remove duplicates. At least three distinct normalized inputs are required.
2. **Feature extraction:** treat a whole skill phrase (such as `cloud computing`) as one feature. Build the vocabulary exclusively from role skills. Both user profiles and role profiles use that same vocabulary.
3. **TF-IDF:** TF is the feature count divided by the total recognized feature count in a profile. IDF is `ln(N / df)`, where N is the number of roles and df is the number containing the skill. This follows page 12 of the assignment. IDF is fitted to the catalogue once, never refitted to each user. A skill present in every role has zero weight; zero-vector comparisons safely return zero.
4. **Scoring:** multiply TF by IDF, then calculate `dot(user, role) / (norm(user) * norm(role))`. A zero vector receives score zero. Inputs and role skills are deduplicated, so repeating a skill cannot increase its weight.
5. **Sorting and filtering:** sort descending by full-precision similarity, breaking ties alphabetically by role name. Return up to three positive-score roles. No-overlap roles are omitted instead of filling results with unrelated suggestions.
6. **Explanation:** display matching skills, illustrative tools, and additional catalogue skills to explore. These additional skills are a set difference, not an assessment of what the user actually lacks.

Unknown skills are disclosed and excluded from the shared vector space. If fewer than three current inputs are recognized, a limited-profile message accompanies any results. If neither current inputs nor goal inputs produce a nonzero profile, no recommendations are returned. The interface's skill list and example profiles help users provide initial preferences without requiring historical user data.

Optional career goals are expressed as skills the user wants to develop. Recognized goal skills are merged with current skills, with equal per-skill weight before IDF; duplicates do not add weight. At least three current skills or interests are still required. Goal matches are displayed separately, and additional role skills are compared against the current-skill input. A recognized goal may produce results even when current skills are outside the catalogue. This is an explicit preference mechanism, not free-text career counselling.

```powershell
python recommender.py --skills "Python,Cloud Computing,Automation" --goals "Machine Learning"
python verify_project.py
node audit_browser.js
```

`verify_project.py` requires Node.js for cross-language checks. `audit_browser.js` uses a local headless Chrome installation and writes screenshots to `evidence`; set `AUDIT_BROWSER` to a compatible browser executable if necessary.

## Example walkthrough

For `Python, Cloud Computing, Automation`, the engine creates one profile with those three skill features. It compares that profile with every role, including DevOps Engineer, Cloud Engineer, and Systems Administrator. Shared rare skills contribute more weight than very common skills. Role length also affects the cosine denominator, so ranking is not merely a count of matching skills. Run the example command to inspect the actual scores and ranking.

## Files

- `recommender.py`: reusable matching engine and command-line interface.
- `app.py`: local HTTP server and JSON API, bound to the local computer.
- `index.html`: responsive browser interface with accessible form controls and text-safe result rendering.
- `browser_engine.js`: browser matching logic embedded in the standalone page.
- `build_page.py`: rebuilds the embedded catalogue and matching script.
- `test_browser.js`: exercises the standalone form without network access and supports Python/browser score comparisons; requires Node.js for development checks.
- `raw_skills.csv`: clearly labelled sample role catalogue.
- `test_recommender.py`: mathematical, ranking, input-handling, and HTTP integration checks.

## Limits

This is an explainable educational content-based recommender. It does not learn from other users, train a neural network, or measure proficiency. Career goals and interests are expressed as supported skill tags. Scores express similarity within this small catalogue, not hiring probability, career suitability, or job readiness. Catalogue choices and aliases affect results. Unsupported synonyms and free-form sentences are not semantically inferred. The browser server is intended for local demonstrations.

## Submission materials

See `REQUIREMENTS_AUDIT.md` for the page-by-page review. `Project_3_Report.docx` and `Project_3_Report.html` contain the project report and four real-browser screenshots; `PROJECT_REPORT.md` is the report source. Run `python export_report.py` to regenerate the report exports. `Project_3_Submission.zip` contains the application, source, tests, documentation, and evidence. Open `index.html` after extracting the ZIP.

All 11 Python tests and 6,009 cross-language profile comparisons passed. Real Chrome desktop/mobile-emulation checks passed, and screenshots were visually reviewed. Browser screenshots and the check record are in `evidence`. The Word report package was checked for valid XML and included images; its pagination has not been reviewed in Microsoft Word.
