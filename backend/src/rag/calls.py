from .langchain_client import LangChainClient


# Initialize the LangChain client
langchain_client = LangChainClient()

rag_chain = langchain_client.rag_chain

def get_response(question: str, context: str = "capital of funsuk is wangdu"):
    response = rag_chain.invoke({"question": question, "context": context})
    return response