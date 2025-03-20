import os
import yaml
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class LangChainClient:
    """Singleton class to manage LangChain client connections and configuration."""
    _instance = None
    _config = None
    _llm = None
    _embedding_model = None
    _rag_chain = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangChainClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize LangChain configuration and clients."""
        # Load environment variables
        load_dotenv(override=True)
        
        # Load configuration
        with open("backend/config.yaml", "r") as file:
            self._config = yaml.safe_load(file)
            
        # Set up LangChain environment variables
        os.environ['LANGCHAIN_TRACING_V2'] = self._config['langchain']['tracing_v2']
        os.environ['LANGCHAIN_ENDPOINT'] = self._config['langchain']['endpoint']
        os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
        os.environ['LANGCHAIN_PROJECT'] = os.getenv("LANGCHAIN_PROJECT")
        
        # Initialize models
        endpoint = self._config['llm']['endpoint']
        model_name = self._config['llm']['model']
        embedding_model_name = self._config['llm']['embedded_model']
        
        try:
            self._llm = ChatOpenAI(
                api_key=os.getenv("GITHUB_TOKEN"), 
                model_name=model_name, 
                base_url=endpoint, 
                temperature=0
            )
        except Exception as e:
            raise Exception(f"LLM initialization failed: {str(e)}")
        
        try:
            self._embedding_model = OpenAIEmbeddings(
                api_key=os.getenv("GITHUB_TOKEN"), 
                base_url=endpoint, 
                model=embedding_model_name
            )
        except Exception as e:
            raise Exception(f"Embedding model initialization failed: {str(e)}")
        
        # Set up default RAG chain
        template = """Answer the question based only on the following context:
        {context}

        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        self._rag_chain = prompt | self._llm | StrOutputParser()
        
        self._instance = self
            
        return self._instance
    
    @property
    def llm(self):
        """Get the LLM instance."""
        return self._llm
    
    @property
    def embedding_model(self):
        """Get the embedding model instance."""
        return self._embedding_model
    
    @property
    def rag_chain(self):
        """Get the default RAG chain."""
        return self._rag_chain
    
    @property
    def config(self):
        """Get the configuration."""
        return self._config
    
if __name__ == "__main__":
    langchain_client = LangChainClient()
    rag_chain = langchain_client.rag_chain
    
    question = "What is the capital of funsuk?"
    context = "capital of funsuk is wangdu"
    response = rag_chain.invoke({"question": question, "context": context})
    print(response)