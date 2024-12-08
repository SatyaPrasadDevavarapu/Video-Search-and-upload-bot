import os
import requests
import instaloader
import cohere
import json
import asyncio
import aiohttp
from tqdm import tqdm

# Replace with your Cohere API key
COHERE_API_KEY = "g6WqGnL6XZVDQURCNwy2xtCTqEiihXr7nIZhL2UV"
# Replace with your Flic-Token API key
FLIC_TOKEN = "flic_7effa44a3930ef571dfdafee4148db8fbd2a15fd1506d1848474d37a33138f74"
def get_hashtags_from_query(query):
    prompt = f"""
    Generate relevant hashtags based on the following query for Instagram:
    {query}
    """
    
    # Use the cohere API directly (updated way of using the API)
    response = cohere.chat(
        model="command-r", 
        messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                  {"role": "user", "content": prompt}],
        temperature=0
    )

    hashtags = response['text'].strip().split()
    return [hashtag.lower() for hashtag in hashtags]

# Function to download videos from Instagram using hashtags
def download_videos(hashtags):
    L = instaloader.Instaloader()

    # Create the video folder if it doesn't exist
    if not os.path.exists("videos"):
        os.makedirs("videos")

    downloaded_files = []
    for hashtag in hashtags:
        print(f"Searching for videos with #{hashtag}")
        try:
            for post in instaloader.Hashtag.from_name(L.context, hashtag).get_posts():
                if post.is_video:
                    video_url = post.video_url
                    file_name = os.path.join("videos", f"{hashtag}_{post.shortcode}.mp4")

                    # Download the video
                    with requests.get(video_url, stream=True) as r:
                        r.raise_for_status()
                        with open(file_name, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)

                    downloaded_files.append(file_name)
                    print(f"Downloaded video: {file_name}")
                    if len(downloaded_files) >= 5:  # Limit to top 5 videos for each hashtag
                        break
        except Exception as e:
            print(f"Error downloading videos for #{hashtag}: {e}")
    return downloaded_files

# Function to get upload URL
async def get_upload_url():
    headers = {
        "Flic-Token": FLIC_TOKEN,
        "Content-Type": "application/json"
    }
    url = "https://api.socialverseapp.com/posts/generate-upload-url"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()

# Function to upload video
async def upload_video(file_path, upload_url):
    headers = {
        "Flic-Token": FLIC_TOKEN,
        "Content-Type": "application/json"
    }
    with open(file_path, 'rb') as f:
        file_data = f.read()

    async with aiohttp.ClientSession() as session:
        async with session.put(upload_url, headers=headers, data=file_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

# Function to create a post
async def create_post(title, hash, category_id):
    headers = {
        "Flic-Token": FLIC_TOKEN,
        "Content-Type": "application/json"
    }
    url = "https://api.socialverseapp.com/posts"
    body = {
        "title": title,
        "hash": hash,
        "is_available_in_public_feed": False,
        "category_id": category_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as response:
            return await response.json()

# Function to delete local files after uploading
def delete_local_files(file_paths):
    for file_path in file_paths:
        try:
            os.remove(file_path)
            print(f"Deleted {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

# Main function to run the script
async def main():
    query = "Best destinations in Europe for photography"  # Example query
    hashtags = get_hashtags_from_query(query)

    # Download videos based on hashtags
    downloaded_files = download_videos(hashtags)

    if downloaded_files:
        # Get upload URL
        upload_url_response = await get_upload_url()
        if upload_url_response:
            upload_url = upload_url_response.get('upload_url')

            # Upload videos asynchronously
            upload_tasks = []
            for file_path in downloaded_files:
                upload_tasks.append(upload_video(file_path, upload_url))

            upload_responses = await asyncio.gather(*upload_tasks)

            # Upload status check
            for i, response in enumerate(upload_responses):
                if response:
                    print(f"Video {downloaded_files[i]} uploaded successfully.")
                else:
                    print(f"Failed to upload {downloaded_files[i]}.")

            # Create posts after successful upload (You can customize category_id)
            category_id = 1  # Replace with a valid category ID
            post_tasks = []
            for file_path in downloaded_files:
                title = os.path.basename(file_path)
                hash = file_path.split('_')[-1].split('.')[0]  # Example: extract shortcode as hash
                post_tasks.append(create_post(title, hash, category_id))

            post_responses = await asyncio.gather(*post_tasks)
            for post_response in post_responses:
                if post_response:
                    print(f"Post created: {post_response['title']}")
                else:
                    print(f"Failed to create post.")

            # Delete local video files after uploading and posting
            delete_local_files(downloaded_files)
        else:
            print("Failed to get upload URL.")
    else:
        print("No videos downloaded.")

if __name__ == "__main__":
    asyncio.run(main())