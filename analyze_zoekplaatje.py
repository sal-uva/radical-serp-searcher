"""
Process a questions file and zoekplaatje csv and output various statistics
"""
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from urllib.parse import unquote

questions_file = "data/questions.csv"
zp_file = "C:/Users/shagen/surfdrive/UvA/work/2024_bing-content-moderation/data/zoekplaatje-export-google.com-2024-11-13T160209.csv"
df_q = pd.read_csv(questions_file)
df_zp = pd.read_csv(zp_file)

print(f"Loaded in {len(df_q)} questions")

# print(df_q.info())
# print(df_zp.info())

# DROP UNKNOWN ELEMENTS FROM ZOEKPLAATJE RESULTS
# Remove unknowns; these are, upon closer inspection invisible elements or highly irregular ones.
original_len = len(df_zp)
print("Dropping unknown elements from zoekplaatje list")
df_in = df_zp[~df_zp["type"].str.contains("unknown")]
print(f"Dropped {original_len - len(df_in)} Zoekplaatje rows from {len(df_in)} rows")

# ADD ZOEKPLAATJE ELEMENTS TO QUESTIONS DF
# list of tuples with (element, section) values
di_zp_elements = {}

df_q.index = df_q["question_simplified_contextualized"].str.lower()
df_q["all_elements"] = [[] for n in range(len(df_q))]
df_q["only_snippets"] = [[] for n in range(len(df_q))]
df_q["board"] = [''] * len(df_q)
count_cols = ["4chanpol_count","4chanint_count","4chanlgbt_count","4chanb_count","4chank_count","4chanfit_count","leftypol_count"]

for i, row in df_zp.iterrows():
	q_clean = unquote(row["query"])
	df_q.loc[q_clean, "all_elements"].append((row["type"], row["section"]))
	# Also add a column with non-organic results
	# We see this as the "enrichment"
	if "organic" not in row["type"]:
		df_q.loc[q_clean, "only_snippets"].append((row["type"], row["section"]))

for i, row in df_q.iterrows():
	for count_col in count_cols:
		if row[count_col] > 0:
			df_q.loc[i, "board"] = count_col.replace("_count", "")

old_len = len(df_q)
#df_with_snips = df_q[df_q["all_elements"].map(len) > 0]
df_with_snips = df_q[df_q["only_snippets"].map(len) > 0]
print(f"Removed {old_len - len(df_with_snips)} rows without snippets, kept {len(df_with_snips)}")

# SUBQUESTION 1:  Is there a correlation between question toxicity and the amount of snippets shown?
# Let's visualise this as a scatter plot!
# (Or a matrix?)
cmap = {
	"4chanpol": "brown",
	"4chanint": "blue",
	"4chanlgbt": "pink",
	"4chanb": "green",
	"4chank": "purple",
	"4chanfit": "yellow",
	"leftypol": "orange"
}
colors = [cmap[b] for b in df_with_snips["board"]]
x_values = df_with_snips["TOXICITY"]
y_values = df_with_snips["only_snippets"].map(len).tolist()
plt.clf()
plt.title("Do toxic questions get more or less enriched by Google?")
plt.xlabel("Perspective API toxicity score")
plt.ylabel("Number of non-organic SERP snippets")
plt.grid(alpha=.2)
legend_labels = [mpatches.Patch(color=v, label=k) for k, v in cmap.items()]
plt.scatter(x_values, y_values, s=df_with_snips["replies"], c=colors, alpha=0.4)
plt.legend(handles=legend_labels, loc="upper right", title="boards")
plt.show()

# Step 1:




# SUBQUESTION 2: Are different topics differently enriched?
# Let's visualise this as box plots per board, with the boxes denoting the mean + deviation of the amount of
#  non-organic snippets

# Step 1: