from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from gpt4all import GPT4All

app = FastAPI()

# Load the GPT4All model (make sure the model exists at this path)
model = GPT4All("mistral-7b-openorca.Q2_K.gguf", model_path="./models", allow_download=False)

class QueryRequest(BaseModel):
    user_query: str
    retrieved_docs: list[str]

@app.post("/generate/")
async def generate_response(request: QueryRequest):
    if not request.retrieved_docs:
        raise HTTPException(status_code=400, detail="No documents provided for context.")

    try:
        documents = "\n\n".join(doc.strip() for doc in request.retrieved_docs if doc.strip())
        prompt = f"""
You are a knowledgeable and concise financial assistant.
Respond to the user's question using only the information provided in the retrieved documents.
If the answer is not present in those documents, clearly respond with:
"I'm sorry, I couldn't find that information in the provided data."
Keep your answers natural, well-structured, and easy to understand. Use full sentences and avoid listing raw data unless it's relevant to the user’s query.

Documents:
{documents}

User Query:
{request.user_query}

Answer:
"""

        output = model.generate(prompt, max_tokens=300, temp=0.4)
        return {"response": output.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
