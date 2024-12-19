from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from pydantic import BaseModel
import os
from openai import OpenAI
from groq import Groq

app = FastAPI()

# Configure API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
client = OpenAI(api_key=openai_api_key)
client_groq = Groq(api_key=groq_api_key)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class RequestModel(BaseModel):
    prompt: str

message_temp = """You are a expert chef . Have knowledge about many dishes including indian , japnees ,chinees and many more . keep your answer within 20-30 words only. and dont talk about any other topic."""

@app.post("/recipe")
async def generate_recipe(request: RequestModel):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": message_temp},
                {"role": "user", "content": request.prompt}
            ]
        )
        return {"recipe": completion.choices[0].message["content"]}
    except Exception as e:
        return {"error": str(e)}


@app.post("/recipe_groq")
async def recipe_groq(request: RequestModel):
    print({'aa': request.prompt})
    try:
        completion = client_groq.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": message_temp},
                {"role": "user", "content": request.prompt}
            ],
            temperature=1,
            max_tokens=512,
            top_p=1,
            stream=True,
        )
        
        async def stream_response():
            response_content = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                response_content += content
                yield content 
                await asyncio.sleep(0) 
        
        return StreamingResponse(stream_response(), media_type="text/plain")
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=3000, reload=True)
