from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Olá, Alfredo, Bernardo e Nuno! O nosso projeto Flask está vivo!</h1>"

if __name__ == "__main__":
    app.run(debug=True)