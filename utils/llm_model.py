from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

embed_model = OpenAIEmbedding(model_name="text-embedding-ada-002")

llm=OpenAI(model="gpt-4-1106-preview", temperature=0, max_tokens=350)