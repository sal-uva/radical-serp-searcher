# What imageboard catalogs we should take into account
CATALOGS = {
	"leftypol": "https://leftypol.org/leftypol/catalog.json",
	"4chan/pol/": "https://a.4cdn.org/pol/catalog.json"
}

# What search engines we should consider
SEARCH_ENGINES = ["google", "bing"]

# Question filtering
QUESTION_THRESHOLD = 20  	# How many times a question should be encountered before screenshots are generated
MIN_REPLIES = 100			# The minimum number of replies the OP must have received
MUST_BE_EXPLICIT = True		# Whether the question should be labeled as 'explicit' by the LLM
MIN_TOXICITY = 0.2			# Threshold for toxicity score
MAX_QUESTION_LENGTH = 500	# How many characters a single question may be (long questions are expensive and maybe not worth it

# LLM / OpenAI stuff
MODEL = "gpt-4o-mini"		# See https://platform.openai.com/docs/models/
OPENAI_KEY = "XXX"
TEMPERATURE = 0.1
MAX_OUTPUT_TOKENS = 4096
CHUNKS = 3					# Smaller is more reliable but more expensive.
MAX_OPENAI_RETRIES = 5		# How many times we retry the prompt if the input and output length are not the same.

# Google Perspective API key
GOOGLE_KEY = "XXX"

# 4CAT token
TOKEN_4CAT = "XXX"

# URL to a 4CAT server.
# Server needs to have the screenshot datasource, available as extension from:
# https://github.com/digitalmethodsinitiative/4cat_web_studies_extensions/tree/main
URL_4CAT = "XXX"

DEBUG_LENGTH = 0			# Only process this many questions for debugging. Set to 0 or False to skip.
