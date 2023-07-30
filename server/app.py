"""
Web server that runs to generate recommendations from current model.
"""

from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    """
    Main entrypoint into server. 
    """
    # Get the JSON payload from the request
    payload = request.json

    recommendations = ["python", "ansible", "docker"]

    return jsonify({
        "body": {
            "recommendations": recommendations
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
