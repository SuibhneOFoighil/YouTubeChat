import os
import googleapiclient
import requests

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from youtube_transcript_api import YouTubeTranscriptApi

def parse_video(data, vidid, window=70, stride=67):
    docs = []
    for i in range(0, len(data), stride):
        i_end = min(len(data)-1, i+window)
        text = ' '.join([ data[i]['text'] for i in range(i, i_end) ])
        # create the new merged dataset
        meta_data = {
            'citation': f"https://youtu.be/{vidid}?t={int(data[i]['start'])}"
        }
        doc = Document(page_content=text, metadata=meta_data)
        docs.append(doc)
    return docs

def loadEmbeddings(session):

    # Reset vector database
    session.docsearch = ''
    videoIDs = [session.id]

    # Retreive VideoIDs for playlist
    if session.type == 'playlist':
        load_dotenv()
        youtube_api_key = os.environ['YOUTUBE_DATA_API_KEY']
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=youtube_api_key)
        try:
            request = youtube.playlistItems().list(
                part="contentDetails",
                maxResults=50,
                playlistId=session.id
            )
            results = request.execute() #problematic line?
            videoIDs = [ x['contentDetails']['videoId'] for x in results['items'] ]
        except Exception as e:
            return e
        # else:
        #     return 'the YouTube API failed: check your ".env" file or use the "video" tab'

    # Retreive YouTube Transcripts
    video_transcripts = []
    transcript_ids = []
    for vidid in videoIDs:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(vidid, languages=['en'])
            video_transcripts.append(transcript)
            transcript_ids.append(vidid)
        except:
            pass
    
    #Parse the Transcripts
    new_data = [ parse_video(data, vidid) for data, vidid in zip(video_transcripts, transcript_ids) ]
    docs = [item for sublist in new_data for item in sublist]

    #Embedding Documents for Question-Answer Model
    embeddings = session.embedding_model 
    session.docsearch = Chroma.from_documents(docs, embeddings)