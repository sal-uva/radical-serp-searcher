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

**Input Format:**
A JSON array of questions, each with:

* `"question"`: The original question extracted from the 4chan post.
* `"full_text"`: The full text of the 4chan post containing the question.

**Output Format:**
A JSON array called "results" with the following structure for each question:

* `"question_simplified_contextualized"`: The simplified and contextualized question.

**Important:** If a question cannot be simplified or contextualized, return the original question in `"question_simplified_contextualized"`.
Make sure to output the same number of values as input values.

Input:
'[input]'

"""

IS_CONTROVERSIAL = """
You are an expert in internet language and public debates. You are tasked to determine whether a question is controversial or not.

A controversial question is offensive or touches on sensitive or illegal subjects. Controversial subjects for instance include anti-democratic sentiment, gender transitions, identity stereotypes, and racism.
Examples:
  - "How can I perform DIY hormone therapy?"
  - "Why are black people loud?"
  - "How can we establish Stalinism?"

A noncontroversial question concerns non-offensive, everyday topics and does not use any contested langauge.
Examples:
  - "How do I gain muscle?"
  - "Who is the current president"? 

If you're unsure or cannot categorise a question, score a question as `true`.
Make sure to output the EXACT number of output booleans as input questions. THIS IS VERY IMPORTANT.

**Output Format:**
A JSON array of booleans, `true` if the question is explicit, `false` otherwise.
Example output: `[true, false, true]`

**Input questions**:
'[input]'
"""

IS_EXPLICIT = """
You are an expert in internet language and online discussions, tasked with classifying questions from 4chan posts as either "explicit" or "implicit."

**Explicit Question:** A question with a clearly stated subject that can be understood without additional context. These may contain Internet slang but are typically suitable for web searches.

* **Examples:**
	* "What is Kamala Harris' race?"
	* "What are some good kino leftie YouTube channels?"
	* "What is the cheapest shotgun I can get?"

**Implicit Question:** A question that relies on context or implied information to be understood.
Search engines would likely struggle to understand the intent or context.

* **Examples:**
	* "Do you agree?"
	* "What do you think about Ukraine?"
	* "Can I have fries with that?"
	* "What is a better form of protest?"

**Instructions:**
Analyze each question from the provided list and determine if it is explicit or implicit.
If you're unsure or cannot categorise the question, label the question as explicit.
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

SERP_INTERFACE_PROMPTS = """
Extract a list of SERP interface snippets  from this [SEARCH_ENGINE] results page.
Be sure to process the whole page. Group regular search results in a "search_results" object.
Return a valid JSON array of objects with interface elements in the following format:
```
{
	"name_of_interface_element1": {
		// content of the interface element
	},
	"name_of_interface_element2": {
		// content of the interface element
	},
	// etc.
}
```
"""