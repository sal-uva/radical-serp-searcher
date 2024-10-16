# Radical SERP Searcher
- Extract questions from imageboards.
- Transform them into queryable phrases.
- Search these questions on different search engines
- Take screenshots of the SERP via [4CAT](https://github.com/digitalmethodsinitiative/4cat/). 

Departs from a "platform perspectivist" approach: studying one platform through the lens of another.

## Install and run
1. Install dependencies:

`pip install -r requirements.txt`

2. Copy-paste `config-example.py`, rename it to `config.py`, and insert the required variables:
   - OpenAI API key
   - Google Cloud Platform API key
   - 4CAT API token
   - URL to a 4CAT server that runs the [Screenshot Generator extension](https://github.com/digitalmethodsinitiative/4cat_web_studies_extensions).

3. Set other config options (like `TEMPERATURE` or `MIN_TOXICITY`).
4. Run `start.py`. Do this over time to keep track of emerging questions posed  
