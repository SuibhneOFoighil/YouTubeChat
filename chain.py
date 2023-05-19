import openai
from langchain import PromptTemplate
from langchain.chains import RetrievalQA, LLMChain, SequentialChain

from prompt import get_qa_prompt, get_interpreter_prompt

def get_qa_chain(llm, docsearch):
    prompt_template = get_qa_prompt()
    
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
    template = get_interpreter_prompt()

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