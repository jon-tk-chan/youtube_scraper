from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import json
import credentials

DEVELOPER_KEY = credentials.API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)

search_query="why I quit my job"
total_videos = 50

def get_video_metadata(query="Why I quit my job", results_total=250):
    """Returns a list of results_total number of video responses
        Each item returned is from youtube.search().list(q=query)      
        input:
            query: str
            results total: int of number of videos to do
    """
    responses_list =[] #list of pages of responses
    results_total += 1
    for i in range(0,results_total,50):
        if i ==0:
            next_token=None
            prev_token = None
        search_response = youtube.search().list(
            q=query, type="video", pageToken=next_token,
            order = 'relevance',part="id,snippet",maxResults=results_total,
            location=None, locationRadius=None).execute()
        responses_list.append(search_response)

        #Get next page and previous page of videos, update tokens
        if 'nextPageToken' in search_response.keys():
            next_token=search_response['nextPageToken']
        else:
            next_token=None
        if 'prevPageToken' in search_response.keys():
            prev_token=search_response['prevPageToken']
        else:
            prev_token=None
    video_list = []
    for response in responses_list:
        videos_list = response['items']
        for item in videos_list:
            video_title=item['snippet']['title']
    #         desc = item['snippet']['description'] #only gives snippet of desc - add when getting transcripts
            video_id = item['id']['videoId']
            channel_id = item['snippet']['channelId']
            published_at = item['snippet']['publishedAt']
            video_dict = {"videoId": video_id,
                "videoTitle": video_title,
                "channelId": channel_id,
                'publishedAt': published_at}
            video_list.append(video_dict)
    # print(f"COMPLETED - NUMBER OF VIDEO RESPONSES: {len(video_list)}")
    return video_list

def get_video_stats(video_list):
    """Return a dictionary of lists containing the info for each video in video_list"""
    title = []
    channelId = []
    channelTitle = []
    categoryId = []
    publishedAt=[]
    videoId = []
    viewCount = []
    likeCount = []
    dislikeCount = []
    commentCount = []
    favoriteCount = []
    category = []
    tags = []
    videos = []
    descriptions=[]
    i = 0
    for video in video_list:
        videoId.append(video['videoId'])
        title.append(video['videoTitle'])
        publishedAt.append(video['publishedAt'])
        stats = youtube.videos().list(
            part='statistics, snippet',
            id=video['videoId']).execute()
        #values for each video stored for <GIVEN FIELD>: 
        #stats['items'][0]['statistics'][<GIVEN FIELD>] OR stats['items'][0]['snippet'][<GIVEN FIELD>]
        channelId.append(stats['items'][0]['snippet']['channelId']) 
        channelTitle.append(stats['items'][0]['snippet']['channelTitle']) 
        categoryId.append(stats['items'][0]['snippet']['categoryId']) 
        favoriteCount.append(stats['items'][0]['statistics']['favoriteCount'])
        #fill remaining lists from stats['items'][0]['statistics'] OR stats['items'][0]['snippet']
        try:
            viewCount.append(stats['items'][0]['statistics']['viewCount']) 
        except:
            viewCount.append("Not available") 
        try:
            likeCount.append(stats['items'][0]['statistics']['likeCount'])
        except:
            likeCount.append("Not available")
        try:
            dislikeCount.append(stats['items'][0]['statistics']['dislikeCount'])     
        except:
            dislikeCount.append("Not available")
        if 'commentCount' in stats['items'][0]['statistics'].keys():
            commentCount.append(stats['items'][0]['statistics']['commentCount'])
        else:
            commentCount.append(0)
        if 'tags' in stats['items'][0]['snippet'].keys():
            tags.append(stats['items'][0]['snippet']['tags'])
        else:
            tags.append("No Tags")
        if 'description' in stats['items'][0]['snippet'].keys():
            descriptions.append(stats['items'][0]['snippet']['description'])
        else:
            tags.append("No Description")
        i += 1
    #write JSON to store video information for all
    youtube_dict = {'tags':tags,'channelId': channelId,'channelTitle': channelTitle,
                    'categoryId':categoryId,'publishedAt': publishedAt,'title':title,'videoId':videoId,
                    'viewCount':viewCount,'likeCount':likeCount,'dislikeCount':dislikeCount,
                    'commentCount':commentCount,'favoriteCount':favoriteCount,
                   "description": descriptions}
    # print(f"DONE - NUMBER OF VIDEOS PROCESSED: {len(youtube_dict['channelId'])}")
    return youtube_dict

def add_youtube_transcripts(youtube_dict):
    """return a copy of youtube_dict with list of transcript strings and 
    list of raw transcripts (list of list of cleaned strings)

    Note: some youtube videos to not have transcript available - write 'None' type when YoutubeTranscriptApi cannot access
    """
    final_dict = youtube_dict.copy()
    transcripts_sents = []
    transcripts_strings = []
    transcripts_parsed = []
    for i, video_id in enumerate(youtube_dict['videoId']):
        transcript_sentlist = []
        #use YouTubeTranscriptApi.get_transcript() and write "NONE" if no transcripts exist
        try:
            eng_transcript = YouTubeTranscriptApi.get_transcript(video_id,languages=['en'])
            transcript_sentlist = [str(x['text']).replace("\xa0", "") for x in eng_transcript]
            transcript_joined = " ".join(transcript_sentlist)
        except:
            transtript_sentlist = None
            transcript_joined = None
        transcripts_sents.append(transcript_sentlist)
        transcripts_strings.append(transcript_joined)
    final_dict['transcripts_raw'] = transcripts_sents
    final_dict['transcript_strings'] = transcripts_strings
    # print(f"DONE - NUMBER OF VIDEOS PROCESSED: {len(final_dict['transcript_strings'])}")
    return final_dict

def main():
    """main executable function - calls scraper functions in order, saves to predefined filepath"""
    print(f"start - collecting urls for given search query: {search_query}")
    video_list = get_video_metadata(search_query,total_videos)
    print(f"Scraped number of videos: {len(video_list)}")
    youtube_dict = get_video_stats(video_list)
    print(f"Scraped stats for videos: {len(youtube_dict['channelId'])}")
    print("collecting transcripts - time intensive task")
    try:
        final_dict = add_youtube_transcripts(youtube_dict)
        print(f"Scraped transcripts for videos: {len(final_dict['transcript_strings'])}")

        # print("FIRST 5 of each column")
        # for key, dict_items in final_dict.items():
        #     # dict_item = final_dict[key][0:5]
        #     dict_examples = dict_items[0:5]
        #     print(f"************** {key} *********************")
        #     print(dict_examples)
        #     print(type(dict_examples))
        #     print("----")
        filename="data/youtube_stats_and_transcripts.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_dict, f, ensure_ascii=False, indent=4)
    except:
        print("issue - add_youtube_transcripts()")

if __name__ == "__main__":
    main()