import pandas as pd
import numpy as np
import os
import faiss
import requests
import re
from collections import Counter
from flask import Flask, jsonify, request

port = int(os.environ.get("PORT", 8080))

app = Flask(__name__)

# Load the valid API keys for authentication
API_KEYS = {
    "userx":"XXXXXXXX",
    "usery":"YYYYYYYY"
}

#Load the pre-created ok cupid vector database of profiles
vector_compressed_pd = pd.read_csv("vector_compressed.txt", header=None)
vector_compressed = np.array(vector_compressed_pd)

# Define the dimensionality of the embeddings
dimension = vector_compressed.shape[1]

# Create a FAISS index (L2 Distance Search)
index = faiss.IndexFlatL2(dimension)

# Add embeddings to the FAISS index
index.add(vector_compressed)

#Define function that tokenises the user input to search the vector database
def tokeniser(sentence):
  filtered = re.sub(r'[^a-zA-Z ]', '', sentence) #get only characters
  splitted=filtered.replace("-"," ").split(" ")
  splitted= [n for n in splitted if n!='']
  return splitted

#Load the unique vocabulary of the ok cupid profiles to create term frequency
with open("unique_vocab.txt", "r") as f:
    unique_vocab = (f.read()) # read the profiles as plain text

unique_vocab = unique_vocab.split(",")

#Term frequency function that vectorizes user input
def tf(tokenised_profile):
  profile_count = Counter(tokenised_profile)
  #Creates a vector that counts occurances compared to the whole vocabulary
  vector={word: 1 + np.log10(profile_count[word]) if profile_count[word] > 0 else 0 for word in unique_vocab}
  return [m for n,m in vector.items()]

#Takes the user input and runs the aftermentioned functions to create a vector
def convert_input_to_tf(user_input):
    input_vector = tf(tokeniser(user_input))
    tf_vector = np.array(input_vector)
    input_compressed = tf_vector.reshape(263, 57).sum(axis=1) # compressing the vector for better performance
    return input_compressed.reshape(1,263)

#Read the profiles as plain text
with open('profiles.txt', 'r') as f:
    read_profiles=(f.read()) # read the profiles as plain text

okcupid_profiles = read_profiles.split('||')

@app.route("/")
def hello_world():
    return """Welcome to date finder!"""

@app.route('/date-search', methods=['POST'])
def receive_data():
    # Authenticate the request using API key
    api_key = request.headers.get('X-API-KEY')

    # Check if the API key is valid
    if not api_key or api_key not in API_KEYS.values():
        return jsonify({"error": "Invalid API key"}), 401
    
    #Error handling for empty data
    data = request.json  # Get JSON payload
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    user_input = data.get("user_input")
    query = convert_input_to_tf(user_input)
    
    #Searching the FAISS vector database for the closest three matches.
    k = 3  # Number of results to retrieve
    distances, indices_cupid = index.search(query, k)

    # Get top 3 matches based on user input query
    matches = {f"Match_{x}": okcupid_profiles[i] for x,i in enumerate(indices_cupid[0])}

    # Return the results
    return jsonify({"response": matches}), 200

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = port)
