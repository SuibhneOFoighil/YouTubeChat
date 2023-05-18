import openai
from langchain import PromptTemplate
from langchain.chains import RetrievalQA, LLMChain, SequentialChain

def get_qa_chain(llm, docsearch):
    prompt_template = """Use the following pieces of Context to Answer the Question. Use only the relevant information and do not rewrite the Context, verbatim. If the Context is not relevant, do not try to answer. 
    Context: {context}
    Question: {question}
    Answer:"""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain_type_kwargs = {"prompt": PROMPT}

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=docsearch.as_retriever(),
        chain_type_kwargs=chain_type_kwargs,
        output_key='result',
        return_source_documents=True
    )

    return qa_chain

def get_interpreter_chain(llm):
    template = """You are reformatting and citing the answers of a Question-Answer Model. Use the Context to find where in the Answer to put the Citations. Do not write 'N/A' but use full sentences. Follow the example below:
    Question: What are the key points?
    Answer: The key points of the are that Fruits are delicious and good for you because they are high in fiber
    Context: [Document(page_content="Fruits are very delicious", metadata={{'id': 'L_Guz73e6fw-t4127.46', 'vidid': 'L_Guz73e6fw', 'citation': 'https://youtu.be/L_Guz73e6fw?t=4127'}})], [Document(page_content="Fruits are very good for you - they are high in fiber", metadata={{'id': 'L_Guz73e6fw-t4150.49', 'vidid': 'L_Guz73e6fw', 'citation': 'https://youtu.be/L_Guz73e6fw?t=4150'}})]
    Citations: [(1)](https://youtu.be/L_Guz73e6fw?t=4127), [(2)](https://youtu.be/L_Guz73e6fw?t=4150)
    Citted Answer: The key points of the are that Fruits are delicious [(1)](https://youtu.be/L_Guz73e6fw?t=4127) and good for you because they are high in fiber [(2)](https://youtu.be/L_Guz73e6fw?t=4150)
    Question: {query}
    Answer: {result}
    Context: {source_documents}
    Citations:"""

    prompt_template = PromptTemplate(input_variables=["query", 'result', 'source_documents'], template=template)

    interpreter_chain = LLMChain(llm=llm, prompt=prompt_template, output_key='answer')

    return interpreter_chain

def loadChain(session):
    
    #Define Question-Answer Model
    qa_chain = get_qa_chain(session.llm, session.docsearch)

    # Define the 'Interpreter' Model, which formats the QA Model's Output
    interpreter_chain = get_interpreter_chain(session.llm)

    # This is the overall chain where we run the QA and Interpreter in sequence.
    overall_chain = SequentialChain(
        chains=[qa_chain, interpreter_chain],
        input_variables=["query"],
        output_variables=["result", "answer"] #The output of the QA chain and the Interpreter chain
    )

    session.chain = overall_chain