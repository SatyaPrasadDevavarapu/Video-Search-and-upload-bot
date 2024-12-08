import cohere

# Replace with your actual API key
COHERE_API_KEY = "g6WqGnL6XZVDQURCNwy2xtCTqEiihXr7nIZhL2UV"

def generate_hashtags(query):
    """Generates relevant hashtags based on a query using Cohere API."""
    co = cohere.Client(COHERE_API_KEY)
    prompt = f"""Based on the user's search query, generate a list of Instagram hashtags in lowercase. 
The hashtags should be relevant, engaging, and effective for discoverability, including a mix of popular and niche tags.

Search Query: {query}

Output the hashtags in a comma-separated format, all in lowercase."""

    response = co.generate(
        model="command-r",
        prompt=prompt,
        max_tokens=100,
        temperature=0.5,
        stop_sequences=["\n"]
    )

    return response.generations[0].text.strip()

