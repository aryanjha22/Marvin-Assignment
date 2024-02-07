from flask import Flask, request, make_response
import wikipedia
from collections import Counter

app = Flask(__name__)

# Initialized a list to store search history
search_history = []

def get_word_frequency(text, n):

    """
    Get the frequency of the top 'n' words in the given text.
    Args:
    - text (str): Input text.
    - n (int): Number of top words to retrieve.
    Returns:
    - list: List of tuples containing top words and their frequencies.
    """

    words = text.split()
    word_count = Counter(words)
    top_words = word_count.most_common(n)
    return top_words

def search_wikipedia(topic, n):

    """
    Search Wikipedia for the given topic and return the top 'n' words from the content.
    Args:
    - topic (str): Wikipedia topic to search.
    - n (int): Number of top words to retrieve.
    Returns:
    - list or str: List of tuples containing top words and their frequencies,
                  or an error message if there's an issue with the search.
    """

    try:
        # Retrieve Wikipedia page for the given topic
        page = wikipedia.page(topic)
        text = page.content
        # Get the word frequency in the page content
        top_words = get_word_frequency(text, n)
        return top_words
    except wikipedia.exceptions.DisambiguationError as e:
        options = e.options
        # Handling DisambiguationError by returning options
        return f"DisambiguationError: {options}"
    except wikipedia.exceptions.PageError as e:
        # Handling PageError by returning an error message
        return f"PageError: {e}"

# Define an endpoint for word frequency analysis
@app.route('/word-frequency-analysis', methods=['GET'])
def word_frequency_analysis():

    """
    Endpoint for analyzing word frequency in Wikipedia articles.
    Usage: /word_frequency_analysis?topic=<topic>&n=<n>
    - topic (str): Wikipedia topic to analyze.
    - n (int, optional): Number of top words to retrieve (default is 10).
    Returns:
    - str: Response containing the top 'n' words and their frequencies,
           or an error message if there's an issue with the request.
    """

    # Get parameters from the request
    topic = request.args.get('topic')
    n = int(request.args.get('n', 10))

    # Check if the 'topic' parameter is provided
    if not topic:
        return make_response('Error: Topic parameter is required', 400, {'Content-Type': 'text/plain'})

    try:
        # Search Wikipedia for the given topic and retrieve top words
        top_words = search_wikipedia(topic, n)

        if isinstance(top_words, list):
            # Format the response with the top words and their frequencies
            response_text = f'Topic: {topic}\n\nTop {n} Words:\n'
            for i, (word, count) in enumerate(top_words, start=1):
                response_text += f"{i}. {word}: {count}\n"
        else:
            # Handle DisambiguationError or PageError
            response_text = top_words

        # Save search history
        search_history.append({'topic': topic, 'top_words': top_words})

        return make_response(response_text, 200, {'Content-Type': 'text/plain'})
    except Exception as e:
        # Log the exception
        app.logger.error(f"Error processing request for topic '{topic}': {str(e)}")
        return make_response('Internal Server Error', 500, {'Content-Type': 'text/plain'})

# Define an endpoint for accessing search history
@app.route('/search-history', methods=['GET'])
def search_history_endpoint():

    """
    Endpoint for accessing the search history.
    Usage: /search_history
    Returns:
    - str: Response containing the search history in reverse order.
    """
    
    # Reverse the order of the search history
    reversed_history = search_history[::-1]
    # Format the search history as plain text
    plain_text_history = '\n\n'.join([f"Topic: {entry['topic']}\nResult: {entry['top_words']}" for entry in reversed_history])
    response_text = f'Search History:\n\n{plain_text_history}\n\n'
    return make_response(response_text, 200, {'Content-Type': 'text/plain'})

# Run's the Flask application
if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000)
