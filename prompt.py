def get_qa_prompt():
    return """Use the following pieces of Context to Answer the Question. Use only the relevant information and do not rewrite the Context, verbatim. If the Context is not relevant, do not try to answer. 
    Context: {context}
    Question: {question}
    Answer:"""

def get_interpreter_prompt():
    return """You are reformatting and citing the answers of a Question-Answer Model. Use the Context to find where in the Answer to put the Citations. If you don't know, do not write "N/A" but use full sentences. Follow the example below:
    Question: What are the key points?
    Answer: The key points of the are that Fruits are delicious and good for you because they are high in fiber
    Context: [Document(page_content="Fruits are very delicious", metadata={{'id': 'L_Guz73e6fw-t4127.46', 'vidid': 'L_Guz73e6fw', 'citation': 'https://youtu.be/L_Guz73e6fw?t=4127'}})], [Document(page_content="Fruits are very good for you - they are high in fiber", metadata={{'id': 'L_Guz73e6fw-t4150.49', 'vidid': 'L_Guz73e6fw', 'citation': 'https://youtu.be/L_Guz73e6fw?t=4150'}})]
    Citations: [(1)](https://youtu.be/L_Guz73e6fw?t=4127), [(2)](https://youtu.be/L_Guz73e6fw?t=4150)
    Citted Answer: The key points of the are that Fruits are delicious [(1)](https://youtu.be/L_Guz73e6fw?t=4127) and good for you because they are high in fiber [(2)](https://youtu.be/L_Guz73e6fw?t=4150)
    Question: {query}
    Answer: {result}
    Context: {source_documents}
    Citations:"""