"""
Web server that runs to generate recommendations from current model.
"""

from flask import Flask, request, jsonify

from model_v0 import model, preprocessing, recommender


app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    """
    Main entrypoint into server. 
    """
    payload = request.json
    input_description = payload['description']

    processed_input = preprocessing.preprocess_input_text(input_description)
    embedding = model.generate_sentence_embeddings(processed_input)

    recommended_technologies = recommender.cosine_similarity_recommendations(input_dataset, embedding)

    return jsonify({
        "body": {
            "recommendations": recommended_technologies
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
