from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vector import get_retriever
import time


llm = OllamaLLM(model="llama3")

template = """
You are answering questions about Wyrd Media Labs using the company wiki.

Use ONLY the provided context.
If the answer is not in the context, say "I could not find that in the wiki."

Context:
{context}

Question:
{question}

Answer clearly using the information in the context.
"""

prompt_template = ChatPromptTemplate.from_template(
    template
)

def main():
    retriever = get_retriever()

    while True:
        query = input("\nAsk a question (type exit): ")

        if query.lower() == "exit":
            break

        relevant_docs = retriever.invoke(query)

        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        prompt = prompt_template.invoke({
            "context": context,
            "question": query
        })
        
        start = time.time()
        response = llm.invoke(prompt)
        response = StrOutputParser().invoke(response)
        end = time.time()

        print(f"\nResponse generated in {end - start:.6f} seconds.")

        print("\nAnswer:\n", response)


if __name__ == "__main__":
    main()