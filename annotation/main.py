from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from annotation.evaluator.tree import EvaluatorTree
from common.loader import load_folktales, load_hierarchies
from annotation.tools.place_extractor import extract_places
import os

def get_model(temperature: float, remote: bool=False) -> BaseChatModel:
    if remote:
        model = ChatGroq(
            # api_key=os.environ.get("GROQ_API_KEY"),
            model="llama-3.1-8b-instant",
            temperature=temperature,
            timeout=5.0,
            max_retries=2
        )
    else:
        model = ChatOllama(
            base_url=os.environ.get("OLLAMA_HOST"),
            model="llama3.1:8b",
            num_gpu=-1,
            validate_model_on_init=True,
            temperature=temperature
        )
    return model

def main():
    load_dotenv()

    model = get_model(temperature=0.7,
                      remote=True)

    hierarchies = load_hierarchies()
    event_hierarchy = hierarchies["event"]

    evaluator_tree = EvaluatorTree(event_hierarchy)
    evaluator_tree.print()

    folktales = load_folktales()
    momotaro = folktales.iloc[0]["text"]
    extract_places(model, momotaro)

if __name__ == "__main__":
    main()