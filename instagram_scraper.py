import os
import requests
import instaloader
from typing import List

# Constants
VIDEO_DIR = './videos'

def download_videos_by_hashtag(hashtag: str) -> List[str]:
    """Downloads videos from Instagram using a hashtag."""
    loader = instaloader.Instaloader()

    # Create directory if it doesn't exist
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)

    # List to store downloaded video paths
    downloaded_videos = []

    # Search posts using the hashtag
    for post in instaloader.Hashtag.from_name(loader.context, hashtag).get_posts():
        if post.is_video:
            video_url = post.video_url
            video_filename = os.path.join(VIDEO_DIR, f"{hashtag}_{post.shortcode}.mp4")

            # Download the video
            response = requests.get(video_url)
            with open(video_filename, 'wb') as f:
                f.write(response.content)
                downloaded_videos.append(video_filename)
                print(f"Downloaded video: {video_filename}")

        # Optional: limit the number of posts
        if len(downloaded_videos) >= 5:  # download top 5 videos
            break

    return downloaded_videos
