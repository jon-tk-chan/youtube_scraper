# youtube_scraper
Python script for scraping Youtube video statistics and transcript text. Saves a file containing video statistics (view count, channel title, etc.). To change query `search_query` and number of videos to scrape `total_videos`. 

Assumes credential file `credential.py` contains your API key - [instructions](https://developers.google.com/youtube/registering_an_application).

Requires:
- Google API Python client and Youtube Transcript API - install using `pip install -r requirements.txt`

Resources:
- [Youtube Data API Overview](https://developers.google.com/youtube/v3/getting-started)
- [Sudharsan Asaithambi - Youtube Data in Python (Medium Article)](https://medium.com/greyatom/youtube-data-in-python-6147160c5833)
- [Python - Downloading captions from Youtube](https://www.geeksforgeeks.org/python-downloading-captions-from-youtube/)