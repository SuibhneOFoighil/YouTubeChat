# YouTubeChat
Finish your learning backlog: chat with any YouTube video or playlist!

## Quick Start
Install Dependencies
```shell
pip install -r requirements.txt
```
Rename `example.env` to `.env` and edit the variables appropriately.
```
MODEL_TYPE: supports LlamaCpp or GPT4All
PERSIST_DIRECTORY: is the folder you want your vectorstore in
LLAMA_EMBEDDINGS_MODEL: (absolute) Path to your LlamaCpp supported embeddings model
MODEL_PATH: Path to your GPT4All or LlamaCpp supported LLM
MODEL_N_CTX: Maximum token limit for both embeddings and LLM models
```
Run it!
```shell
python YouTubeChat.py
```
