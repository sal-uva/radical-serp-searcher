"""
LLM prompts to be used in the pipeline.
"""

SIMPLIFY_AND_CONTEXTUALISE = """
You are an expert in grammar and internet culture, specializing in simplifying questions from online forums like 4chan for clarity and searchability.

Your task is to analyze a list of questions extracted from 4chan posts and perform the following:

1. **Simplify:** Condense each question to be more concise and explicit.
Slang and Internet jargon (like 'normie') should be retained, but irrelevant words should be removed.
Expand all contractions, like "isn't" to "is not".
The resulting question should be suitable for use in a search engine like Google.

* **Example 1:**
	* **Original:** "So /pol/, how'd you really think Kamala Harris became black?"
	* **Simplified:** "How did Kamala Harris become black?"
* **Example 2:**
	* **Original:** "Is there actually a reason to believe that QAnon is true?"
	* **Simplified:** "Is there a reason to believe QAnon is true?"

2. **Contextualize:** Resolve any implicit references and pronouns by referring to the provided "full_text", which includes the surrounding post content. If you are unsure, retain the original text.

* **Example:**
	* **Question:** "Do you think they are black?"
	* **Full Text:** "Let's talk about Indians. Do you think they're black?"
	* **Simplified:** "Do you think Indians are black?"

3. **Subject extraction:** Extract the grammatical *subject* for each simplified question.

**Input Format:**
A JSON array of questions, each with:

* `"question"`: The original question extracted from the 4chan post.
* `"full_text"`: The full text of the 4chan post containing the question.

**Output Format:**
A JSON array called "results" with the following structure for each question:

* `"question_simplified_contextualized"`: The simplified and contextualized question.
* `"subject"`: The subject of the question.

**Important:** If a question cannot be simplified or contextualized, return the original question in `"question_simplified_contextualized"`.
Make sure to output the same number of values as input values.

Input:
'[input]'

"""

IS_EXPLICIT = """
You are an expert in internet language and online discussions, tasked with classifying questions from 4chan posts as either "explicit" or "implicit."

**Explicit Question:** A question with a clearly stated subject that can be understood without additional context. These may contain Internet slang but are typically suitable for web searches.

* **Examples:**
	* "What is Kamala Harris' race?"
	* "What are some good kino leftie YouTube channels?"

**Implicit Question:** A question that relies on context or implied information to be understood. Search engines would likely struggle to understand the intent.

* **Examples:**
	* "Do you agree?"
	* "What do you think about Ukraine?"
	* "Can I have fries with that?"
	* "What's a better form of protest?"

**Instructions:**
Analyze each question from the provided list and determine if it is explicit or implicit.
If you're unsure or cannot categorise the question, return an empty string.
Make sure to output the EXACT number of output values as input values. THIS IS VERY IMPORTANT.

**Input Format:**
A newline-separated list of questions.

**Output Format:**
A JSON array with the value:

* `"explicit"`:  `true` if the question is explicit, `false` otherwise.

**Example Output:**
{"results": [{ "question": "What is the capital of France?", "explicit": true }, { "question": "Is it true?", "explicit": false } ]}

Input:
'[input]'
"""