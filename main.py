from fastapi import FastAPI
from pydantic import BaseModel
from chat_service import process_chat, load_history

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"status": "API is running"}


@app.post("/chat")
def chat(req: ChatRequest):
    return process_chat(req.message)


@app.get("/history")
def history():
    return load_history()