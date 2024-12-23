import tweepy
from flask import current_app
import requests
import base64
import io

def post_to_twitter(article_title, article_id, image_url=None):
    try:
        print("\n=== Twitter Posting Debug ===")
        print(f"Attempting to post article: {article_title}")
        print(f"Article ID: {article_id}")
        
        # Initialize Twitter client with both v1 and v2 access
        auth = tweepy.OAuth1UserHandler(
            current_app.config['TWITTER_API_KEY'],
            current_app.config['TWITTER_API_SECRET'],
            current_app.config['TWITTER_ACCESS_TOKEN'],
            current_app.config['TWITTER_ACCESS_TOKEN_SECRET']
        )
        api = tweepy.API(auth)  # v1 API for media upload
        client = tweepy.Client(  # v2 API for tweeting
            consumer_key=current_app.config['TWITTER_API_KEY'],
            consumer_secret=current_app.config['TWITTER_API_SECRET'],
            access_token=current_app.config['TWITTER_ACCESS_TOKEN'],
            access_token_secret=current_app.config['TWITTER_ACCESS_TOKEN_SECRET']
        )
        
        # Upload image if available
        media_id = None
        if image_url and image_url.startswith('data:image/png;base64,'):
            try:
                # Extract base64 data
                image_data = image_url.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                
                # Create file-like object
                image_io = io.BytesIO(image_bytes)
                
                # Upload to Twitter
                print("Uploading image to Twitter...")
                media = api.media_upload(filename='article_image.png', file=image_io)
                media_id = media.media_id
                print(f"Successfully uploaded image with media_id: {media_id}")
            except Exception as img_error:
                print(f"Error uploading image: {str(img_error)}")
        
        # Create the tweet text
        base_url = current_app.config['BASE_URL']
        article_url = f"{base_url}/article/{article_id}"
        
        tweet_text = f"""{article_title}

Read more: {article_url}

#SourceTrustMeBro"""

        print("\nPrepared tweet text:")
        print(tweet_text)
        print(f"Tweet length: {len(tweet_text)} characters")
        
        # Post the tweet with media
        print("\nAttempting to post tweet...")
        if media_id:
            response = client.create_tweet(text=tweet_text, media_ids=[media_id])
        else:
            response = client.create_tweet(text=tweet_text)
        
        print("Tweet posted successfully!")
        print(f"Tweet ID: {response.data['id']}")
        
        return {
            'success': True,
            'tweet_id': response.data['id']
        }
        
    except Exception as e:
        print("\n=== Twitter Error ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("Full error details:", e)
        print("===================")
        return {
            'success': False,
            'error': str(e)
        } 