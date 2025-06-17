from flask import Flask
from flask_cors import CORS
from routes import api_blueprint

app = Flask(
    __name__,
    static_folder="output",
    static_url_path="/output"
)
CORS(app)  # Enables Cross-Origin requests for frontend

# Register the route handlers from routes.py
app.register_blueprint(api_blueprint)

@app.route("/")
def index():
    return "Flask backend is running."

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
