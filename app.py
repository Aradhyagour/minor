import os
print("RUNNING APP FROM:", os.path.abspath(__file__))


from flask import Flask, render_template, request
import torch, random, json
from model import NeuralNet
from nltk_utils import tokenize, bag_of_words

app = Flask(__name__)
chat_history = []

# Load intents
with open("intents.json") as f:
    intents = json.load(f)

# Load trained model
data = torch.load("data.pth")
model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"])
model.load_state_dict(data["model_state"])
model.eval()

all_words = data["all_words"]
tags = data["tags"]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        msg = request.form["message"]

        sentence = tokenize(msg)
        X = bag_of_words(sentence, all_words)
        X = torch.from_numpy(X).float().unsqueeze(0)

        output = model(X)
        probs = torch.softmax(output, dim=1)
        confidence, predicted = torch.max(probs, dim=1)

        tag = tags[predicted.item()]

        response = "Sorry, I didn't understand that."

        if confidence.item() > 0.75:
            for intent in intents["intents"]:
                if tag == intent["tag"]:
                    response = random.choice(intent["responses"])
                    break

        chat_history.append(("user", msg))
        chat_history.append(("bot", response))

    return render_template("base.html", chat=chat_history)

if __name__ == "__main__":
    app.run()

