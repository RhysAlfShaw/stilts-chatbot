# app.py
# main fast api application file
from bs4 import BeautifulSoup
import numpy as np
import re

# --- Core RAG Pipeline Logic ---

class SimpleRAGPipeline:
    """
    A simple implementation of a Retrieval-Augmented Generation pipeline's retrieval component.
    """
    
    def __init__(self, document_path='src/static/doc/sun256.html'):
        self.vector_store = []
        self._initialize_vocabulary()
        # The main pipeline initialization call is now simpler
        self._initialize_pipeline_with_semantic_chunks(document_path)

    # ... (_initialize_vocabulary remains the same) ...

    # REMOVE the old _initialize_pipeline, _parse_html, and _chunk_text methods.
    # REPLACE them with the two methods below.
    def _create_semantic_chunks(self, html_content, max_chunk_size=500):
        """
        Parses HTML and chunks it based on semantic tags like <p>, <h1>, etc.,
        while keeping track of the source element. This version correctly handles
        sub-chunking and boundary generation.

        Args:
            html_content (str): The raw HTML content.
            max_chunk_size (int): The maximum size for a text chunk.

        Returns:
            list[dict]: A list of chunks, each with its text and location metadata.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li', 'pre'])
        
        # Define boundary length once for consistency
        BOUNDARY_LENGTH = 30

        def get_boundary(text, length=BOUNDARY_LENGTH):
            # Cleans up whitespace and gets a slice of the text
            return re.sub(r'\s+', ' ', text).strip()

        all_chunks = []
        for i, element in enumerate(elements):
            text = element.get_text(separator=' ', strip=True)
            if not text:
                continue

            # If the element's text fits within a single chunk
            if len(text) <= max_chunk_size:
                all_chunks.append({
                    "text": text,
                    "location": {
                        "element_index": i,
                        "tag": element.name,
                        "prefix": get_boundary(text[:BOUNDARY_LENGTH]),
                        "suffix": get_boundary(text[-BOUNDARY_LENGTH:])
                    }
                })
            # If the element's text is larger, sub-chunk it by sentences
            else:
                sentences = re.split(r'(?<=[.!?])\s+', text)
                current_sub_chunk = ""
                for sentence in sentences:
                    # Check if adding the next sentence would exceed the max size
                    if len(current_sub_chunk) + len(sentence) + 1 > max_chunk_size:
                        # If there's content in the current sub-chunk, store it
                        if current_sub_chunk:
                            chunk_text = current_sub_chunk.strip()
                            all_chunks.append({
                                "text": chunk_text,
                                "location": {
                                    "element_index": i,
                                    "tag": element.name,
                                    "prefix": get_boundary(chunk_text[:BOUNDARY_LENGTH]),
                                    "suffix": get_boundary(chunk_text[-BOUNDARY_LENGTH:])
                                }
                            })
                        # Start a new sub-chunk with the current sentence
                        current_sub_chunk = sentence
                    else:
                        # Otherwise, add the sentence to the current sub-chunk
                        current_sub_chunk += (" " if current_sub_chunk else "") + sentence
                
                # Add the final remaining sub-chunk to the list
                if current_sub_chunk:
                    chunk_text = current_sub_chunk.strip()
                    all_chunks.append({
                        "text": chunk_text,
                        "location": {
                            "element_index": i,
                            "tag": element.name,
                            "prefix": get_boundary(chunk_text[:BOUNDARY_LENGTH]),
                            "suffix": get_boundary(chunk_text[-BOUNDARY_LENGTH:])
                        }
                    })
        
        return all_chunks

    def _initialize_pipeline_with_semantic_chunks(self, document_path):
        """
        Initializes the RAG pipeline using the semantic chunking method.
        """
        print(f"Initializing pipeline with document: {document_path}")
        try:
            with open(document_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Create chunks with their location metadata in one step
            chunks_with_location = self._create_semantic_chunks(html_content)
            print(f"Document parsed into {len(chunks_with_location)} semantic chunks.")
            
            self.vector_store = [
                {
                    "text": item["text"],
                    "embedding": self._create_embedding(item["text"]),
                    "location": item["location"] # Store the rich location data
                }
                for item in chunks_with_location
            ]
            print(f"Pipeline ready. Document processed into {len(self.vector_store)} chunks.")
        except FileNotFoundError:
            print(f"Error: Document not found at path: {document_path}")
            self.vector_store = []
        except Exception as e:
            print(f"An error occurred during pipeline initialization: {e}")
            self.vector_store = []

    # ... (keep _create_embedding and _cosine_similarity) ...

    # And finally, update retrieve_context to pass the location info
    def retrieve_context(self, query, top_k=3):
        # This method is the same as in Approach 1
        if not query or not self.vector_store:
            return []

        query_vector = self._create_embedding(query)
        
        scored_chunks = [
            {
                "text": item["text"],
                "score": self._cosine_similarity(query_vector, item["embedding"]),
                "location": item["location"] # Pass the location through
            }
            for item in self.vector_store
        ]
        
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_chunks[:top_k]

    def _initialize_vocabulary(self):
        """Sets up the character-to-index mapping for embedding."""
        self.vocabulary = list("abcdefghijklmnopqrstuvwxyz0123456789 ")
        self.vocab_map = {char: i for i, char in enumerate(self.vocabulary)}
        self.vector_dimension = len(self.vocabulary)
        print("Vocabulary initialized.")

    # ... (keep imports and SimpleRAGPipeline class definition) ...



    def _parse_html(self, html_content):
        """
        Parses HTML content to extract clean, readable text.
        
        Args:
            html_content (str): The HTML content of the document.
        
        Returns:
            str: The extracted plain text.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text



    def _create_embedding(self, text):
        """
        Creates a numerical vector embedding from text using character frequency.
        This is a simplified simulation of a real embedding model.
        
        Args:
            text (str): The text to embed.
        
        Returns:
            np.ndarray: A normalized numerical vector.
        """
        vector = np.zeros(self.vector_dimension)
        lowercased_text = text.lower()
        for char in lowercased_text:
            if char in self.vocab_map:
                vector[self.vocab_map[char]] += 1
        
        # Normalize the vector (L2 normalization)
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def _cosine_similarity(self, vec_a, vec_b):
        """
        Calculates the cosine similarity between two vectors.
        
        Args:
            vec_a (np.ndarray): The first vector.
            vec_b (np.ndarray): The second vector.
        
        Returns:
            float: The cosine similarity score.
        """
        # Assumes vectors are already normalized, so dot product is sufficient.
        return np.dot(vec_a, vec_b)


# # --- Flask Web Server ---

# app = Flask(__name__)

# # Initialize the RAG pipeline with the source document
# Make sure 'document.html' is in the same directory as this script.

# try:
#     rag_pipeline = SimpleRAGPipeline('../data/sun256.html')
# except Exception as e:
#     print(f"Failed to initialize RAG Pipeline: {e}")
#     rag_pipeline = None

# @app.route('/')
# def index():
#     """A simple welcome message for the API root."""
#     return "<h1>RAG Pipeline Backend</h1><p>Use the /api/query endpoint to interact with the pipeline.</p>"

# @app.route('/api/query', methods=['POST'])
# def handle_query():
#     """
#     API endpoint to handle a user query.
#     Expects a JSON payload with a "query" key.
#     """
#     if not rag_pipeline:
#         return jsonify({"error": "RAG Pipeline is not initialized."}), 500

#     data = request.get_json()
#     if not data or 'query' not in data:
#         return jsonify({"error": "Missing 'query' in request body"}), 400
    
#     query = data['query']
#     print(f"Received query: {query}")
    
#     try:
#         results = rag_pipeline.retrieve_context(query)
#         return jsonify(results)
#     except Exception as e:
#         print(f"An error occurred during query processing: {e}")
#         return jsonify({"error": "An internal error occurred."}), 500
