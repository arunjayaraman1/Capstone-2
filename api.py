from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastapi
import json
import asyncio
from pydantic import BaseModel
from automation.intent_parser import parse_intent
from automation.browser_agent import run_browser_agent

app= FastAPI()

# Add CORS middleware to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query:str

@app.post("/query")
async def add_to_cart(request:QueryRequest):
    try:
        intent = parse_intent(request.query)
        # Run browser agent with timeout protection (15 minutes max)
        res = await asyncio.wait_for(
            run_browser_agent(intent),
            timeout=900.0  # 15 minutes timeout
        )
        
        # Check if res is a CartResult (Pydantic model) or has structured_output
        if res:
            # If res is already a CartResult model, use it directly
            if isinstance(res, dict):
                cart_data = res
            elif hasattr(res, 'structured_output'):
                cart_data = res.structured_output
            elif hasattr(res, 'model_dump'):
                # It's a Pydantic model
                cart_data = res.model_dump()
            elif hasattr(res, 'dict'):
                # Older Pydantic version
                cart_data = res.dict()
            else:
                cart_data = res
            
            return {
                "success":True,
                "intent":intent.model_dump() if hasattr(intent, 'model_dump') else intent.dict() if hasattr(intent, 'dict') else intent,
                "cart":cart_data
            }
        return {
            "success":False,
            "error":"Failed to add to cart - no result returned"
        }
    except json.JSONDecodeError as e:
        return {
            "success":False,
            "error":f"JSON parsing error: {str(e)}"
        }
    except asyncio.TimeoutError:
        return {
            "success":False,
            "error":"Request timed out - browser automation took too long. Please try again with a simpler query."
        }
    except Exception as e:
        import traceback
        return {
            "success":False,
            "error":f"Error: {str(e)}"
        }