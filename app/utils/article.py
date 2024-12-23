from flask import current_app
import anthropic
import requests
import json
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from stability_sdk import client
import base64
from ..models import db, Article
from .twitter import post_to_twitter

def generate_image_with_stability(prompt):
    try:
        stability_api = client.StabilityInference(
            key=current_app.config['STABILITY_KEY'],
            verbose=True,
        )
        
        answers = stability_api.generate(
            prompt=prompt,
            seed=992446758,
            steps=30,
            cfg_scale=8.0,
            width=768,
            height=512,
            samples=1,
            sampler=generation.SAMPLER_K_DPMPP_2M
        )

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    return {
                        'success': False,
                        'error': 'NSFW content detected'
                    }
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img_data = artifact.binary
                    img_base64 = base64.b64encode(img_data).decode()
                    return {
                        'success': True,
                        'url': f"data:image/png;base64,{img_base64}"
                    }
                    
        return {
            'success': False,
            'error': 'No image generated'
        }
        
    except Exception as e:
        print(f"Stability AI error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def generate_article_with_claude(topic, style, tone):
    try:
        client = anthropic.Anthropic(
            api_key=current_app.config['ANTHROPIC_API_KEY']
        )

        prompt = f"""You are writing an EXTREMELY FUNNY, SATIRICAL article for "Trust Me Bro News". 
        
        YOUR TASK:
        Write a hilarious, over-the-top satirical news article about: "{topic}"
        
        Style Guide:
        - Make it ABSURDLY funny, like The Onion's best articles
        - Use ridiculous quotes from made-up experts with silly names
        - Include outlandish statistics and "studies"
        - Add absurd plot twists
        - Make fun of stereotypes and common behaviors
        - Use internet culture and memes when relevant
        - Keep it lighthearted and playful
        
        Examples of good headlines:
        - "Time Traveler from 2089 Says Dogecoin Will Replace All World Currencies"
        - "Local Bitcoin Maximalist Emerges from Basement, Shocked World Hasn't Collapsed"
        - "Putin Found Running Underground Cheeki Breeki Dance Studio"
        - "Biden's Secret Plan to Replace All Stairs with Ice Cream Slides"
        - "Xi Jinping Bans Letter 'W' Because It Looks Like Winnie Walking Away"
        
        Write your article following this structure:
        1. Write ONLY the headline and article content
        2. DO NOT include any introductory text like "Here is an article about..."
        3. Start directly with your headline
        4. Follow with the article body
        5. Use quotes and absurd details throughout
        
        Remember:
        - Make it ACTUALLY FUNNY
        - Don't hold back on the absurdity
        - Use internet humor and meme references
        - Keep it satirical but not mean-spirited
        - DO NOT include any meta text or explanations
        """

        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=3000,
            temperature=0.9,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        content = message.content[0].text
        
        # Parse the content
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Find the headline and clean up content
        title = None
        body_lines = []
        content_started = False
        
        for line in lines:
            # Skip HTML-like content and metadata
            if any(x in line.lower() for x in ['<div', '<h1', '</div', '</h1', 'class=', '08:58', 'entertainment']):
                continue
            
            if line.startswith('HEADLINE:'):
                title = line.replace('HEADLINE:', '').strip()
                content_started = True
            elif not title and line:
                title = line
                content_started = True
            elif content_started:
                body_lines.append(line)
        
        # Clean up title and body
        title = title.strip().replace('<h1>', '').replace('</h1>', '')
        body = '\n'.join(body_lines)
        
        # Convert body text into HTML paragraphs
        paragraphs = []
        current_paragraph = []
        
        for line in body.split('\n'):
            line = line.strip()
            # Skip any lines that contain HTML tags
            if '<' in line and '>' in line:
                continue
                
            if line:
                if line.startswith('"') and line.endswith('"'):
                    if current_paragraph:
                        paragraphs.append(f"<p>{''.join(current_paragraph)}</p>")
                        current_paragraph = []
                    paragraphs.append(f'<div class="quote"><strong>{line}</strong></div>')
                else:
                    current_paragraph.append(line + ' ')
            elif current_paragraph:
                paragraphs.append(f"<p>{''.join(current_paragraph)}</p>")
                current_paragraph = []
                
        if current_paragraph:
            paragraphs.append(f"<p>{''.join(current_paragraph)}</p>")
        
        # Create the final formatted HTML without duplicate h1
        formatted_body = f'''{''.join(paragraphs)}'''
        
        # Generate image with more specific prompt
        image_prompt = f"""Create a photorealistic news photograph about: {title}
        Style: Professional photojournalism
        Requirements:
        - High resolution
        - Clear focus
        - Realistic lighting
        - News photography style
        - Associated Press or Reuters style
        - No text or watermarks
        - Dramatic composition
        """
        
        try:
            image_result = generate_image_with_stability(image_prompt)
            image_url = image_result.get('url') if image_result.get('success') else None
        except Exception as img_error:
            print(f"Image generation error: {str(img_error)}")
            image_url = None
        
        # Create the article in database
        article = Article(
            title=title,
            content=formatted_body,
            image_url=image_url
        )
        db.session.add(article)
        db.session.commit()
        
        # Post to Twitter
        twitter_result = post_to_twitter(title, article.id, image_url=image_url)
        if not twitter_result['success']:
            print(f"Failed to post to Twitter: {twitter_result.get('error')}")
        
        return {
            'success': True,
            'title': title,
            'content': formatted_body,
            'image_url': image_url
        }
            
    except Exception as e:
        print(f"Article generation error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }