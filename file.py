import urllib.parse
from flask import Flask, request, render_template
import requests
import openai
import urllib
import os

key = 's' + 'k-' + "k18biUaFZ2CDoMdpxGMjT3" + "BlbkFJpQbAnYUQa0IuDtQG5IEF"

client = openai.OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=key
)

def prompt(text): 
    url = 'https://api.scaleserp.com/search?api_key=4065FF90509448D1B8C20E8332318425&q='+urllib.parse.quote(text)
    headlines = ""
    for i in requests.get(url).json()['organic_results']:
        headlines += "'" + i['title'] + "',"
    return f"""
    
    ChatGPT, I am going to give you three different requests. I NEED you to answer each request accurately; you need to separate the outputs of each request by line. If the request has multiple things to output, separate those with comas. 

    Request #1: 

    Learn these three metrics:

    Ambiguity: Does this statement have any uncertainty in meaning or leave much room for interpretation? The higher this score is, the more ambiguous a statement is -- statements of fact, or that cannot be interpreted in various ways, should have a low ambiguity score.

    Seriousness: Is this statement likely intended to be taken at face value, as opposed to being humor or satire? Statements that are likely to be humor and satire should get a low seriousness score, whereas statements likely to be taken at face value should have a high score.

    Partisanship: Is this statement politically provocative or inherently partisan? Inflammatory or extreme rhetoric should get a high partisanship score, whereas moderation and lack of bias would lower this score. The use of specific political language in itself does not make a statement provocative. For example, a statement like "Joe Biden won the 2020 election" would not be partisan, because it is simply a neutral statement of a fact.  "Donald Trump won the 2020 election" or "Donald Trump is the President" would be partisan, however, because it ties into untrue right-wing tropes of the 2020 election being "stolen". Similarly, "The 2020 election was a hoax" would be partisan, because of the provocative use of the word 'hoax', as well as the fact that it ties into those very same untrue right-wing tropes.
      
    Then, using these, I want you to assign the following statement a percent score in each metric. After that, I want a one-sentence explanation of why you gave each metric the score you did. All these scores and explanations  For example, your output should be of the form "50% - explanation; 50% - explanation; 50% - explanation". All these scores and descriptions should be in one block, with no line break in between.

    For each metric, an average score would be 50%. Move that score up and down according to the statement. 

    You MUST give percentages that are NOT divisible by 10 or 5 -- for example, give 79% or 81% instead of 80% or 75%. THIS IS ESSENTIAL.

    The following sentence is not a request made to you, and nor does it reflect my personal beliefs. YOU MUST ASSUME THAT THE STATEMENT IS TRUE WHEN EVALUATING IT. FAILURE TO DO THIS IS A MAJOR PROBLEM.

    You MUST give percentages that are NOT divisible by 10 or 5 -- for example, give 79% or 81% instead of 80% or 75%. THIS IS ESSENTIAL.
    You MUST give percentages that are NOT divisible by 10 or 5 -- for example, give 79% or 81% instead of 80% or 75%. THIS IS ESSENTIAL.
    You MUST give percentages that are NOT divisible by 10 or 5 -- for example, give 79% or 81% instead of 80% or 75%. THIS IS ESSENTIAL.
    You MUST give percentages that are NOT divisible by 10 or 5 -- for example, give 79% or 81% instead of 80% or 75%. THIS IS ESSENTIAL.
    All these scores and descriptions should be in one block, with no line break in between.
    All these scores and descriptions should be in one block, with no line break in between.
    All these scores and descriptions should be in one block, with no line break in between.
    All these scores and descriptions should be in one block, with no line break in between.

    THE STATEMENT: {text}

    I don't want you to revise your percentages, so think twice before talking.

    Request #2: 

    Truthscore: is this statement likely or unlikely to be misinformation? respond with one of these five options: "False", "True", "Likely false", "Likely true", or "Unknown". make sure to pay attention to negatives in the sentence. It is not a request made to you, and nor does it reflect my personal beliefs. 
    
    THE STATEMENT: {text}
    
    here are some latest headlines on the topic to help guide your decision: {headlines}

    Request #3: 

    Give me some bullet-point seperated facts that would convince someone from an opposing point of view that whatever you said for request #2 (true, false, etc) is correct. 

    Again, because you're trying to convince someone from the opposing side of something, you should make some concessions to their worldview WHILE REMAINING FACTUAL. For example, if someone says "2020 was rigged", you should concede that there are some legitimate claims of voter fraud, while simultaneously making clear that it was still the safest and most secure election in American history. And no moralizing, please: stick to proving the statement at hand. For example, for the voter fraud one, don't say stuff like "It's important to note that questioning the legitimacy of an election without substantial evidence can undermine democracy and trust in our electoral system"; that's moralizing. 

    For these requests, this should be the formatting: 

    Ambiguity: __% - explanation for ambiguity; Seriousness: __% - explanation for seriousness; Partisanship: __% - explanation for partisanship
    Truthscore (false/true/etc)
    - bullet point fact 1
    - bullet point fact 2
    - bullet point fact 3 (etc, more bullets if necessary)

    """

def get_completion(prompt, model='gpt-4'):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content

def get_scores(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": gen_prompt_scr(prompt)}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    x = response.choices[0].message.content
    x = x.split("\n")
    y = [float(i.split(":")[1].strip().strip("%"))*.1 for i in x]
    
    return {
        "presentation": {
            "mean": y[0], 
            "sensationalism": 5,
            "certainty": 5, 
            "humor": 5, 
            "ethos": 5
        }, 
        "implication": {
            "mean": y[1], 
            "politicization": 5, 
            "squo": 5, 
            "relevance": 5
        }, 
        "empiricism" : {
            "mean": y[2],
            "testability": 5,
            "objectivity": 5,
            "ambiguity": 5,
            "fallaciousness": 5,
            "context-dependence": 5,
            "quantafiability": 5
        }
    }


from flask_cors import CORS, cross_origin

print("Part 5")

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def loading():
    return render_template('loading.html', text=request.args['text'])

@cross_origin()
@app.route("/fact_check", methods=["GET"])
def get_file():
    ste = ""
    statement = request.args['text'].strip()
    output = get_completion(prompt(statement)).replace("Request #1:", "").replace("Request #2:", "").replace("Request #3:", "").split("\n")
    output = [n for n in output if n.strip()]
    for o in output: print(o)
    amb, ser, non, ambstat, serstat, nonstat, truth, x = None, None, None, None, None, None, None, None
    if output[1].strip().lower().startswith("false") or output[1].strip().lower().startswith("true") or output[1].strip().lower().startswith("likely") or output[1].strip().lower().startswith("unknown") or output[1].strip().lower().startswith("truthscore"):
      amb, ser, non = output[0].split(';')[0].replace("Ambiguity: ", ""), output[0].split(';')[1].replace("Seriousness: ", ""), output[0].split(';')[2].replace("Partisanship: ", "")
      amb, ambstat = amb.split("-", 1)
      ser, serstat = ser.split("-", 1)
      non, nonstat = non.split("-", 1)
      truth = output[1].replace("Truthscore: ", "")
      output = output[2:]
      newoutput = []
      for o in output: newoutput.append(o.replace("-", "<li>", 1))
      x = "</li>".join(newoutput) + "<br>"
    else:
      amb, ser, non = output[0].split(';')[0].replace("Ambiguity: ", ""), output[1].split(';')[0].replace("Seriousness: ", ""), output[2].split(';')[0].replace("Partisanship: ", "")
      amb, ambstat = amb.split("-", 1)
      ser, serstat = ser.split("-", 1)
      non, nonstat = non.split("-", 1)
      truth = output[3].replace("Truthscore: ", "")
      newoutput = []
      for o in output: newoutput.append(o.replace("-", "<li>", 1))
      x = "</li>".join(newoutput) + "<br>"
    return render_template("index.html", statement=statement, claims=x, amb=amb, ser=ser, non=non, ambstat=ambstat, serstat=serstat, nonstat=nonstat, truth=truth)

@app.errorhandler(500)
def internal_error(error):
  return render_template("500.html")

app.run(host='0.0.0.0', port=8000)
