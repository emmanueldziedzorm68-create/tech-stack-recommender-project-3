# Requirements audit — Artificial Intelligence Project 3

Source: the user-supplied `Artificial_Intelligence_Project_3_Word (1).docx`, containing 26 slide images. Page numbers below refer to those images in document order. The user selected the Tech Stack Recommender, rather than adapting the retail spreadsheet.

## Page-by-page assessment

| Page | Document content | Classification and implementation |
| --- | --- | --- |
| 1 | Project title and training-kit context | Context; no software requirement. |
| 2 | Match user profiles to item attributes through similarity logic | Implemented with explicit skill vectors and cosine similarity. |
| 3 | Complete Project 3 and verify quality | Automated checks implemented; evidence recorded separately. Badge or instructor verification is external to the software. |
| 4 | Take preferences, match them, display recommendations | Implemented in the browser and Python CLI. |
| 5 | Digital matchmaker introduction | Context, not another deliverable. |
| 6 | Predict useful recommendations from user needs | Implemented as deterministic similarity ranking; no claim of calibrated prediction accuracy. |
| 7 | Input → process → top-N output | Implemented. Click history is an example of possible input, not a required tracking feature. |
| 8 | Project focuses exclusively on content-based filtering | Implemented. Collaborative filtering is a comparison, not a required second engine. |
| 9 | Shared vocabulary and vector mapping | Implemented using whole skill phrases, normalization, and explicit aliases. |
| 10 | Binary overlap and Jaccard limitations | Teaching comparison. A separate Jaccard engine is not required. |
| 11 | TF-IDF feature weighting | Implemented. Each unique skill is one feature. |
| 12 | TF=count/total; IDF=log(N/df) | Aligned to the displayed formula using natural logarithms. Initial smoothed IDF was replaced. |
| 13 | Compare the user vector with all items | Implemented for every role in the catalogue. |
| 14 | Euclidean-distance limitations | Teaching comparison. A Euclidean engine is not required. |
| 15 | Cosine similarity formula | Implemented with safe handling of zero vectors. |
| 16 | Non-negative TF-IDF and similarity interpretation | Scores displayed on a 0–1 scale, explicitly not hiring probabilities. |
| 17 | Ingestion, scoring, sorting, filtering | All four stages implemented. |
| 18 | At least three inputs and scoring of every item | Requires three distinct normalized current skills/interests; calculates every role's similarity. |
| 19 | Descending ranking and top-N truncation | Returns the top three positive matches, fewer if fewer exist. Alphabetical tie-break gives repeatable ordering. |
| 20 | User and item cold starts | Addressed through initial explicit preferences and supplied role metadata; unknown inputs and zero-score profiles receive guidance. |
| 21 | Surveys, popularity fallbacks, metadata inference | Uses initial preference collection. The other listed strategies are alternatives; no historical popularity or demographic dataset was supplied. |
| 22 | Tech Stack Recommender: skills/career goals → roles/tools/platforms | Implemented; optional desired skill tags express career goals. Role-associated tools/platforms are shown. Uses an authored, labelled sample CSV. The wording refers to datasets “like” raw_skills.csv, not a mandatory supplied file. |
| 23 | Three skills, TF-IDF, cosine, top three career paths | Implemented. Diagram/example roles are illustrative, not fixed expected answers for any catalogue. |
| 24 | Apply the concepts across domains | Context; this project remains focused on technology roles. |
| 25 | Practice, experiment, optional ratings/similarity extensions | Recommendations already expose similarity scores. A rating system is a suggested experiment, not mandatory. |
| 26 | Contact details | No implementation or contact action required. |

## Decisions and qualifications

- **Dataset:** 18 authored sample roles, 34 distinct canonical skill features. This is suitable for demonstrating the algorithm, not evidence of labour-market validity. No claim is made that the data came from the training provider. The supplied order spreadsheet is intentionally excluded.
- **Career goals:** optional desired skills enter the same shared vocabulary, with equal per-skill weight before IDF. They do not replace the minimum three current inputs. Goal matches are distinguished from current-skill matches.
- **Exact formula:** natural log is used. Changing log base uniformly rescales TF-IDF vectors and does not alter their cosine similarity. Universal features receive zero IDF; this edge case has a test.
- **Top three:** no unrelated zero-score roles are inserted merely to fill three slots.
- **Meaning of scores:** mathematical similarity within the authored catalogue; not job readiness, hiring probability, or an evaluated career outcome.
- **Quality evidence:** 11 Python checks and browser/Python comparison across 6,009 profiles passed. Real headless Chrome 151 checks also passed, with four screenshots and no runtime exceptions. Desktop and mobile-emulation images were visually reviewed. See `evidence/browser-checks.json`; other browsers and physical devices were not tested.

The source document does not specify a report template, submission website, deployment requirement, neural model, or separate evaluation dataset. The accompanying report is a supporting deliverable prepared at the user's request. Instructor acceptance and badge approval cannot be established by local tests.
