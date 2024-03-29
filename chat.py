import os
import requests
import openai
import gradio as gr
import time
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv

from embeddings import loadEmbeddings
from chain import loadChain
from helpers import extract_text

#Loading API Keys
load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

class Session():
    def __init__(session):
        session.type = '' # whether the user is chatting with a 'video' or 'playlist'
        session.id = ''  # the video or playlistID, which is used to fetch the content
        session.docsearch = '' # the Chroma Vector database for similarity queries
        session.chain = '' # the langchain function that runs sequential models
        session.embedding_model = OpenAIEmbeddings() #Using ada2-embedding model from OpenAI
        session.llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)# Using gpt-3.5-turbo as the Reasoning Engine

    def chatWithYoutube(session):

        def check_link(extract_func):
            def wrapper(link):
                try:
                    response = requests.get(link)
                    if response.status_code == 200:
                        return extract_func(link)
                    else:
                        return f'Something Went Wrong, Error Code {response.status_code}'
                except requests.exceptions.RequestException:
                    return {
                        link_input: gr.update(placeholder='Sorry, that was an invalid link. Try again!', value='')
                    }
            return wrapper

        def success_message():
            return { 
                link_input: gr.update(placeholder='Success! Chat below👇.', value=''),
                chatBox: gr.update(visible=True)
            }


        @check_link
        def extract_playlistID(link):
            session.type = 'playlist'
            session.id = extract_text(link, 'list=', '&')
            if session.id:
                try: 
                    loadEmbeddings(session=session)
                    loadChain(session=session)
                    return success_message()
                except:
                    return {
                    link_input: gr.update(placeholder='Sorry, there was an error getting playlist content. Please re-enter the URL or try another playlist!', value='')
                }
            else:
                return {
                    link_input: gr.update(placeholder='Please enter a YouTube playlist URL', value='')
                }
        
        @check_link
        def extract_videoID(link):
            session.type = 'video'
            session.id = extract_text(link, 'v=', '&')
            if session.id:
                try:
                    loadEmbeddings(session=session)
                    loadChain(session=session)
                    return success_message()
                except:
                    return { 
                        link_input: gr.update(placeholder='Sorry, there was an error getting the video content. Please re-enter the URL or try another video!', value='') #FAILS on videos without an english transcript
                    }
            else:
                return {
                    link_input: gr.update(placeholder='Please enter a YouTube video URL', value='')
                }

        def chat_response(query):
            def strip_text_before_keyword(text, keyword):
                return text.split(keyword)[-1].strip()
            response = session.chain({'query':query})
            return strip_text_before_keyword(response['answer'], 'Answer:')

        def respond(message, chat_history):
            bot_message = chat_response(message)
            chat_history.append((message, bot_message))
            time.sleep(1)
            return "", chat_history

        # The YouTubeChat Interface
        with gr.Blocks(title="Youtube Chat", theme='soft') as demo:

            gr.Markdown("""
            # YouTube Chat
            Enter a link and chat with the video(s) 💬
            """)
            
            with gr.Box() as linkBox:
                
                link_input = gr.Textbox(type="text", label="URL")
                
                with gr.Box():
                    with gr.Row():
                        vid_button = gr.Button("Video")
                        playlist_button = gr.Button("Playlist")
                
                with gr.Box():
                    gr.Markdown("""
                    **Disclaimer**: YouTubeChat does not work for videos without closed captioning or in languages other than english. *Private* YouTube playlists will not work, either. Please let us know if this is a problem for you at "molus.suibhne@gmail.com". We value your feedback!
                    """)

            with gr.Box(visible=False) as chatBox:
                
                with gr.Box():
                    chatbot = gr.Chatbot()

                    msg = gr.Textbox(label='Questions', placeholder='E.G. can you summarize the main themes discussed in the video(s)?')

                with gr.Box():
                    with gr.Row():
                        submit = gr.Button("Send")
                        clear = gr.Button("Clear")

                examples = [
                "Can you summarize the main themes discussed in the video(s)?",
                "What are the main points of the video(s)?",
                "What are the topics discussed in the video(s)?",
                "What are the most important things to remember from the video(s)?"
                ]

                with gr.Box():
                    gr.Examples(examples, msg, label='Starter Questions')

            interface_outputs = [
                link_input,
                chatBox
            ]

            vid_button.click(fn=extract_videoID, inputs=link_input, outputs=interface_outputs)
            playlist_button.click(fn=extract_playlistID, inputs=link_input, outputs=interface_outputs)
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            submit.click(respond, [msg, chatbot], [msg, chatbot])
            clear.click(lambda: None, None, chatbot, queue=False)
            
        demo.launch(share=True, debug=True)