from typing import Optional
import requests
from bs4 import BeautifulSoup
import urllib.parse
import random
import re
from fastapi import HTTPException

def search_meal_image(meal_name: str) -> Optional[str]:
    """
    Search for a meal image by scraping Google Images.
    Returns the URL of a random image from the first few results, or None if no results found.
    """
    try:
        # Construct the search URL
        query = urllib.parse.quote(f"{meal_name} food")
        url = f"https://www.google.com/search?q={query}&tbm=isch"
        
        # Send request with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find image URLs using common Google Images patterns
        images = []
        for img in soup.find_all('img'):
            if 'src' in img.attrs:
                src = img['src']
                if src.startswith('http') and not src.startswith('https://www.google.com'):
                    images.append(src)
        
        # Also try to find encoded image URLs in the page source
        encoded_images = re.findall(r'https://[^"\']*?\.(?:jpg|jpeg|png|gif)', response.text)
        images.extend(encoded_images)
        
        # Remove duplicates and filter out very small images (likely icons)
        images = list(set(images))
        images = [img for img in images if not img.endswith(('.ico', 'favicon.ico'))]
        
        # Return a random image from the first few results
        if images:
            return random.choice(images[:5])
        
        return None
        
    except Exception as e:
        print(f"Error searching for image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error searching for image")
