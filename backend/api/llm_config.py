import os
import yaml
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import WebBaseLoader

# Reload the environment variables
USER_AGENT = os.getenv("USER_AGENT")
load_dotenv(override=True)

# Load the configuration file
with open("backend/config.yaml", "r") as file:
    config = yaml.safe_load(file)

# ------------CONSTANTS------------
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ['LANGCHAIN_PROJECT'] = "rag-finance"

ENDPOINT = config['llm']['endpoint']
MODEL_NAME = config['llm']['model']
EMBEDDING_MODEL_NAME = config['llm']['embedded_model']


# ------------INITIALIZE MODELS------------
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

llm = ChatOpenAI(api_key=os.getenv("GITHUB_TOKEN"), model_name=MODEL_NAME, base_url=ENDPOINT, temperature=0)
embedding_model = OpenAIEmbeddings(api_key=os.getenv("GITHUB_TOKEN"), base_url=ENDPOINT, model=EMBEDDING_MODEL_NAME)
rag_chain = prompt | llm | StrOutputParser()
# ---------------------------------

class PromptRewriter:
    def __init__(self, llm: ChatOpenAI):
        system = """You a question re-writer that converts an input question to a better version that is optimized \n 
            for vectorstore retrieval. Look at the input and try to reaso   n about the underlying semantic intent / meaning."""
        re_write_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                (
                    "human",
                    "Here is the initial question: \n\n {question} \n Formulate an improved question.",
                ),
            ]
        )
        self.question_rewriter = re_write_prompt | llm | StrOutputParser()
    
    def getRewriter(self):
        return self.question_rewriter
    
class NewProductExtractor:
    def __init__(self, llm: ChatOpenAI, products: list):
        system_prompt = f"""
        You are an expert at identifying products that are not present in a predefined list.
        Given a question about a product, you need to extract the product name if it is not found in the following known products list: {products}.
        
        Instructions:
        - If the question mentions a product not included in the list {products}, extract and return the new product's name.
        - If all products mentioned in the question are part of {products}, return 'No new product found'.
        - Assume the products are Amazon products.
        """
        
        self.product_extractor_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "Here is the question: \n\n {question} \n Identify any new product not present in the list.",
                ),
            ]
        )
        self.product_extractor = self.product_extractor_prompt | llm | StrOutputParser()

    def extractNewProduct(self):
        # Call the LLM to process the question and extract the new product
        return self.product_extractor
    
class VectorStore:
    def __init__(self, vector_store_name: str, vector_store_path: str):
        self.vector_store = Chroma(vector_store_name, vector_store_path)
    
    def getVectorStore(self):
        return self.vector_store
    
def get_response(question: str, context: str = "capital of funsuk is wangdu"):
    response = rag_chain.invoke({"question": question, "context": context})
    return response

if __name__ == "__main__":
    question = "What is the capital of funsuk?"
    context = "capital of funsuk is wangdu"
    response = rag_chain.invoke({"question": question, "context": context})
    print(response)