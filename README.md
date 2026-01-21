# Amazon Cart Automation System

A comprehensive natural language shopping automation system that uses LangChain and browser automation to search for products on Amazon, apply filters, and add items to cart based on user queries.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [File Structure](#file-structure)
4. [Detailed File Explanations](#detailed-file-explanations)
   - [automation/models.py](#automationmodelspy)
   - [automation/intent_parser.py](#automationintent_parserpy)
   - [automation/browser_agent.py](#automationbrowser_agentpy)
   - [api.py](#apipy)
   - [ui.py](#uipy) 5 links
   - [test.py](#testpy)
5. [Setup and Installation](#setup-and-installation)
6. [Usage](#usage)
7. [Example Queries](#example-queries)

---

## Project Overview

This system allows users to interact with Amazon through natural language queries. It:
- Parses natural language queries to extract shopping intent
- Automates browser interactions to search for products
- Applies filters (price, rating, brand, color, sort)
- Selects the best matching product
- Adds the product to the Amazon cart
- Returns the result to the user

**Why**: Provides a human-like shopping experience where users can simply describe what they want in natural language instead of manually browsing and filtering.

---

## Architecture

```
User Query → UI (Streamlit) → API (FastAPI) → Intent Parser (LangChain) → Browser Agent (browser-use) → Amazon → Cart Result
```

**Why this architecture**:
- **UI**: Provides an intuitive interface for users
- **API**: Separates frontend from backend logic, allows for easy API integration
- **Intent Parser**: Uses LLM to extract structured data from natural language
- **Browser Agent**: Handles actual browser automation using Playwright
- **Modular Design**: Each component can be tested and modified independently

---

## File Structure

```
2-Capstone/
├── automation/
│   ├── __init__.py
│   ├── models.py           # Data models (Pydantic)
│   ├── intent_parser.py    # Natural language parsing
│   └── browser_agent.py    # Browser automation logic
├── api.py                  # FastAPI backend server
├── ui.py                   # Streamlit frontend
├── test.py                 # Test suite
└── README.md               # This file
```

---

## Detailed File Explanations

### automation/models.py

**Purpose**: Defines data models using Pydantic for type safety and validation.

**Why Pydantic**: Ensures data integrity, provides automatic validation, and enables better IDE support.

```python
from pydantic import BaseModel
from typing import List, Optional
```
- **Line 1**: Import BaseModel from Pydantic - base class for all data models
- **Line 2**: Import typing utilities for optional fields and lists
- **Why**: Type hints improve code readability and catch errors early

```python
class ProductIntent(BaseModel):
    product: str
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    sort_by: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
```
- **Line 4-12**: ProductIntent model represents parsed user query
- **product** (str): Required - the product name user wants to buy
- **max_price** (Optional[float]): Maximum price constraint (e.g., "under ₹500")
- **min_price** (Optional[float]): Minimum price constraint (e.g., "above ₹100")
- **min_rating** (Optional[float]): Minimum rating constraint (e.g., "4 stars and above")
- **max_rating** (Optional[float]): Maximum rating constraint (rarely used)
- **sort_by** (Optional[str]): Sort preference - "price_asc", "price_desc", "rating_desc", "rating_asc", or None
- **color** (Optional[str]): Color preference (e.g., "black", "white")
- **brand** (Optional[str]): Brand preference (e.g., "prestige", "samsung")
- **Why Optional**: Not all queries specify these constraints - defaults to None

```python
class ProductItem(BaseModel):
    name: str
    price: Optional[float] = None
    rating: Optional[float] = None
    url: str
```
- **Line 14-18**: ProductItem model represents a single product
- **name** (str): Required - full product name
- **price** (Optional[float]): Product price (may not always be available)
- **rating** (Optional[float]): Product rating (may not always be available)
- **url** (str): Required - complete Amazon product URL
- **Why**: Standardizes product data structure returned from Amazon

```python
class CartResult(BaseModel):
    items: List[ProductItem]
```
- **Line 20-21**: CartResult model represents the final result
- **items** (List[ProductItem]): List of items added to cart
- **Why List**: Currently supports one item, but structure allows for multiple items in future

---

### automation/intent_parser.py

**Purpose**: Parses natural language queries into structured ProductIntent objects using LangChain and OpenAI.

**Why LangChain**: Provides a structured way to work with LLMs, handles prompts, and manages responses.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from automation.models import ProductIntent
import json
import re
from dotenv import load_dotenv 
load_dotenv()
```
- **Line 1**: ChatOpenAI - LangChain's OpenAI integration
- **Line 2**: ChatPromptTemplate - Template system for prompts
- **Line 3**: Import ProductIntent model we defined
- **Line 4-5**: JSON parsing and regex utilities for response processing
- **Line 6-7**: Load environment variables (OpenAI API key from .env file)
- **Why dotenv**: Keeps API keys secure, not hardcoded in source code

```python
llm = ChatOpenAI(model="gpt-4o-mini")
```
- **Line 9**: Initialize LLM with GPT-4o-mini model
- **Why GPT-4o-mini**: Good balance of accuracy and cost for structured extraction tasks

```python
prompt = ChatPromptTemplate.from_template("""...""")
```
- **Line 11-124**: Define the prompt template for intent extraction
- **Why template**: Allows dynamic insertion of user query while keeping prompt structure consistent

The prompt includes:
1. **Product name extraction**: Removes action words ("add", "buy") and extracts base product
2. **Brand extraction**: Identifies brand names (e.g., "prestige", "samsung")
3. **Color extraction**: Identifies color preferences (e.g., "black", "white")
4. **Price constraints**: Extracts min/max price from phrases like "under ₹500"
5. **Rating constraints**: Extracts rating requirements from phrases like "4 stars and above"
6. **Sort preferences**: Maps phrases like "cheapest" to sort_by values
7. **Examples**: Shows LLM expected output format
- **Why detailed rules**: Ensures consistent extraction across different query formats

```python
def parse_intent(query: str) -> ProductIntent:
    """
    Parse natural language query into structured ProductIntent using LangChain.
    Handles various query formats like:
    - "add pen with price less than 20 rs"
    - "add pen with more user rating"
    - "add laptop under 50000 with good rating"
    """
```
- **Line 126-133**: Function to parse user query
- **query** (str): Natural language query from user
- **Returns**: ProductIntent object with extracted data
- **Why docstring**: Documents function purpose and examples

```python
    response = llm.invoke(prompt.format(query=query))
    content = response.content.strip()
```
- **Line 134-135**: Invoke LLM with formatted prompt and get response
- **Why invoke**: Async-capable method that calls the LLM
- **Why strip**: Removes leading/trailing whitespace that might break parsing

```python
    # Remove markdown code blocks if present (```json ... ```)
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove first line (```json or ```)
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        # Remove last line (```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()
```
- **Line 137-146**: Clean markdown code blocks from LLM response
- **Why**: LLMs sometimes wrap JSON in markdown code blocks - need to extract pure JSON

```python
    # Try to parse JSON directly
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # If direct parsing fails, try to extract JSON object using regex
        # Find the first complete JSON object (handles nested braces)
        brace_count = 0
        start_idx = content.find('{')
        if start_idx == -1:
            raise ValueError(f"No JSON object found in response: {content[:200]}")
        
        end_idx = start_idx
        for i in range(start_idx, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
```
- **Line 148-168**: Robust JSON parsing with fallback
- **Why**: LLMs sometimes add extra text before/after JSON - this extracts just the JSON object
- **Why brace counting**: Handles nested JSON objects correctly

```python
        if brace_count != 0:
            # Unbalanced braces, try simple regex as fallback
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                raise ValueError(f"Malformed JSON in response: {content[:200]}")
        else:
            json_str = content[start_idx:end_idx]
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {content[:200]}. Error: {str(e)}")
```
- **Line 170-183**: Final fallback using regex if brace counting fails
- **Why**: Handles edge cases where JSON might be malformed

```python
    # Validate and create ProductIntent
    try:
        return ProductIntent(**data)
    except Exception as e:
        raise ValueError(f"Failed to create ProductIntent from parsed data: {data}. Error: {str(e)}")
```
- **Line 185-189**: Validate and create ProductIntent object
- **Why**: Pydantic automatically validates data types and constraints
- **Why error handling**: Provides clear error messages if LLM returns invalid data

---

### automation/browser_agent.py

**Purpose**: Creates browser automation instructions and runs the browser agent to interact with Amazon.

**Why browser-use**: Provides high-level browser automation using Playwright with LLM-based decision making.

```python
from browser_use import Agent, Browser, ChatOpenAI
from automation.models import CartResult, ProductIntent
from dotenv import load_dotenv 

load_dotenv()
```
- **Line 1**: Import browser automation components
  - **Agent**: Main automation agent that executes tasks
  - **Browser**: Browser instance manager
  - **ChatOpenAI**: LLM for agent decision making
- **Line 2**: Import data models
- **Line 5**: Load environment variables

```python
def build_task(intent: ProductIntent) -> CartResult:
    filters = []
    if intent.max_price:
        filters.append(f"price ≤ {intent.max_price}")
    if intent.min_rating:
        filters.append(f"rating ≥ {intent.min_rating}")
    # ... similar for other filters
```
- **Line 7-16**: Build filter list from intent
- **Why**: Creates human-readable filter description for the agent

```python
    # Build search query - include brand if specified for better results
    search_query = intent.product
    if intent.brand:
        search_query = f"{intent.brand} {intent.product}"
```
- **Line 18-21**: Construct search query
- **Why include brand**: Searching "prestige cooker" instead of just "cooker" gives better results

```python
    # Build filter instructions
    price_filter_instruction = ""
    if intent.min_price and intent.max_price:
        price_filter_instruction = f"Apply price filter: ₹{intent.min_price} - ₹{intent.max_price}"
    elif intent.max_price:
        price_filter_instruction = f"Apply price filter: Under ₹{intent.max_price}"
    elif intent.min_price:
        price_filter_instruction = f"Apply price filter: Over ₹{intent.min_price}"
```
- **Line 23-30**: Build price filter instruction string
- **Why conditional**: Different instructions for different price constraint types

```python
    # Handle sort preferences - Amazon sort dropdown options
    sort_dropdown_option = {
        "price_asc": "Price: Low to High",
        "price_desc": "Price: High to Low",
        "rating_desc": "Avg. Customer Review",
        "rating_asc": "Price: Low to High"  # Fallback, Amazon doesn't have low rating sort
    }.get(intent.sort_by, "Featured")  # Default/relevance
```
- **Line 36-42**: Map sort_by values to Amazon's dropdown options
- **Why dictionary**: Clean mapping between internal representation and Amazon UI
- **Why fallback**: Amazon doesn't have "lowest rating" sort, so fallback to price sort

```python
    return f"""You are shopping on Amazon like a human would..."""
```
- **Line 44**: Return detailed instructions for the browser agent
- **Why long prompt**: Provides step-by-step guidance for human-like behavior

The task prompt includes:

**STEP 1: SEARCH FIRST**
- Navigate to Amazon
- Type search query (includes brand)
- Wait for results to load
- **Why first**: Must search before applying filters

**STEP 2: APPLY FILTERS**
- Apply sort (if specified)
- Apply price filter (if specified)
- Apply rating filter (if specified)
- Wait for filters to apply
- **Why before picking**: Filters reduce search space, makes product selection easier

**STEP 3: BROWSE FILTERED PRODUCTS**
- Extract 30-40 products with complete details
- Request complete URLs, exact prices, exact ratings
- Skip sponsored products
- **Why extract many**: More options increases chance of finding best match

**STEP 4: CHOOSE THE BEST PRODUCT**
- Match ALL requirements (brand, color, price, rating)
- Must NOT be sponsored
- Pick first product meeting all criteria
- **Why strict matching**: Ensures user gets exactly what they asked for

**STEP 5: NAVIGATE TO PRODUCT PAGE**
- Use complete product URL
- Navigate to product detail page
- Verify correct page loaded
- **Why**: Cannot add to cart from search results - must be on product page

**STEP 6: VERIFY PRODUCT MATCHES EXACT INTENT**
- Check brand matches
- Check color matches (select color variant if needed)
- Check price/rating match
- **Why verify**: Double-check before adding to cart

**STEP 7: ADD TO CART**
- Click "Add to Cart" button (ONCE)
- Handle popups (warranty offers, etc.)
- Wait for confirmation
- **Why once**: Prevents duplicate items

**STEP 8: CONFIRM IT WORKED & RETURN RESULT**
- Check for success indicators (cart count, confirmation message, URL change)
- Use "done" action to return CartResult
- Do NOT write files
- **Why done action**: Returns structured data to API, not to file system

```python
async def run_browser_agent(intent: ProductIntent) -> CartResult:
    # Use vision-capable model for better page understanding via screenshots
    # gpt-4o or gpt-4o-mini with vision support can see page screenshots
    agent = Agent(
        browser=Browser(),
        llm=ChatOpenAI(model="gpt-4o-mini"),  # gpt-4o-mini supports vision
        task=build_task(intent),
        output_model_schema=CartResult,
        max_steps=50
    )
    return await agent.run()
```
- **Line 335-345**: Create and run browser agent
- **browser=Browser()**: Creates browser instance (uses Playwright)
- **llm**: LLM for agent decision making (gpt-4o-mini has vision capabilities)
- **task**: Detailed instructions from build_task
- **output_model_schema**: Ensures agent returns CartResult format
- **max_steps=50**: Limits agent steps to prevent infinite loops
- **Why async**: Browser automation is I/O-bound, async improves efficiency
- **Why vision model**: Agent can "see" page screenshots, better understands UI state

---

### api.py

**Purpose**: FastAPI backend server that receives user queries, processes them, and returns results.

**Why FastAPI**: Modern, fast async framework perfect for this use case.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastapi
import json
import asyncio
from pydantic import BaseModel
from automation.intent_parser import parse_intent
from automation.browser_agent import run_browser_agent
```
- **Line 1**: FastAPI framework
- **Line 2**: CORS middleware - allows cross-origin requests
- **Line 4**: Asyncio for async timeout handling
- **Line 6-7**: Import our automation modules

```python
app = FastAPI()

# Add CORS middleware to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
- **Line 10**: Create FastAPI app instance
- **Line 12-19**: Configure CORS middleware
- **Why CORS**: Streamlit UI runs on different port than API, needs CORS to communicate
- **Why allow_origins=["*"]**: Allows requests from any origin (for development; restrict in production)

```python
class QueryRequest(BaseModel):
    query: str
```
- **Line 21-22**: Request model for API endpoint
- **query** (str): User's natural language query
- **Why Pydantic model**: Automatic validation and documentation

```python
@app.post("/query")
async def add_to_cart(request: QueryRequest):
```
- **Line 24-25**: Define POST endpoint for /query
- **Why async**: Browser automation is async, need async endpoint
- **Why POST**: Sending data (query) to server

```python
    try:
        intent = parse_intent(request.query)
```
- **Line 26-27**: Parse user query into structured intent
- **Why try-except**: Handle parsing errors gracefully

```python
        # Run browser agent with timeout protection (15 minutes max)
        res = await asyncio.wait_for(
            run_browser_agent(intent),
            timeout=900.0  # 15 minutes timeout
        )
```
- **Line 28-32**: Run browser agent with timeout
- **Why asyncio.wait_for**: Prevents API from hanging indefinitely
- **Why 900 seconds**: Browser automation can take time, but shouldn't exceed 15 minutes

```python
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
```
- **Line 34-48**: Handle different return types from browser agent
- **Why multiple checks**: Browser agent might return dict, Pydantic model, or wrapped result
- **Why compatibility**: Handles different Pydantic versions and browser-use versions

```python
            return {
                "success": True,
                "intent": intent.model_dump() if hasattr(intent, 'model_dump') else intent.dict() if hasattr(intent, 'dict') else intent,
                "cart": cart_data
            }
```
- **Line 50-54**: Return success response
- **success**: Boolean flag for UI to check
- **intent**: Parsed intent (for debugging/display)
- **cart**: CartResult data with product info
- **Why include intent**: Helps debugging and shows what was parsed

```python
        return {
            "success": False,
            "error": "Failed to add to cart - no result returned"
        }
```
- **Line 55-58**: Return error if no result
- **Why**: Provides clear error message to user

```python
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"JSON parsing error: {str(e)}"
        }
```
- **Line 59-63**: Handle JSON parsing errors
- **Why specific exception**: Intent parser might fail JSON parsing

```python
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Request timed out - browser automation took too long. Please try again with a simpler query."
        }
```
- **Line 64-68**: Handle timeout errors
- **Why specific message**: Helps user understand issue and suggests solution

```python
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }
```
- **Line 69-74**: Catch-all exception handler
- **Why traceback import**: For detailed error logging (could log to file)
- **Why generic message**: Prevents exposing internal errors to user

---

### ui.py

**Purpose**: Streamlit frontend interface for users to input queries and see results.

**Why Streamlit**: Quick to build, great for prototyping, handles UI automatically.

```python
import streamlit as st
import requests

API_URL = "http://localhost:8000/query"
```
- **Line 1**: Streamlit for UI
- **Line 2**: Requests for API calls
- **Line 4**: API endpoint URL
- **Why localhost:8000**: FastAPI runs on port 8000 by default

```python
st.title("Amazon Cart Automation")
```
- **Line 6**: Display page title
- **Why**: Clear branding/identification

```python
query = st.text_input(
    "Enter your shopping query",
    placeholder="add pen below 20 rs with good rating"
)
```
- **Line 9-12**: Create text input field
- **placeholder**: Example query to guide users
- **Why**: Shows users expected query format

```python
if st.button("Add to Cart"):
    if not query:
        st.error("please enter a query")
```
- **Line 14-16**: Check if button clicked and validate input
- **Why validation**: Prevents empty API calls

```python
    else:
        try:
            res = requests.post(API_URL, json={"query": query}, timeout=600)  # 10 minutes timeout
```
- **Line 17-19**: Make API request
- **json={"query": query}**: Send query as JSON in request body
- **timeout=600**: 10 minutes timeout for long-running automation
- **Why long timeout**: Browser automation takes time, especially with filters

```python
            res.raise_for_status()  # Raise an exception for bad status codes
            data = res.json()
```
- **Line 20-21**: Check HTTP status and parse JSON response
- **Why raise_for_status**: Fails fast on HTTP errors (404, 500, etc.)

```python
            if data.get("success"):
                st.success("Item added to cart!")
                if "cart" in data and "items" in data["cart"]:
                    for item in data["cart"]["items"]:
                        st.markdown(f"🔗 [{item['name']}]({item['url']})")
```
- **Line 23-27**: Display success message and product links
- **st.success**: Green success banner
- **st.markdown**: Render clickable product links
- **Why link format**: Users can click to verify product on Amazon

```python
            else:
                error_msg = data.get("error", "Automation failed")
                st.error(f"Automation failed: {error_msg}")
```
- **Line 28-30**: Display error message
- **st.error**: Red error banner
- **Why**: Clear visual feedback for failures

```python
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
```
- **Line 31-32**: Handle network/connection errors
- **Why specific exception**: Network issues vs application errors

```python
        except KeyError as e:
            st.error(f"Unexpected response format: missing key {e}")
```
- **Line 33-34**: Handle malformed API responses
- **Why**: API might return unexpected structure

```python
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
```
- **Line 35-36**: Catch-all exception handler
- **Why**: Prevents UI crash from unexpected errors

---

### test.py

**Purpose**: Comprehensive test suite for validating intent parser and browser automation.

**Why testing**: Ensures system works correctly with various query formats.

```python
import asyncio
import sys
from automation.intent_parser import parse_intent
from automation.browser_agent import run_browser_agent
from automation.models import ProductIntent
```
- **Line 1-5**: Import test dependencies
- **asyncio**: For async browser agent tests
- **sys**: For exit codes

```python
TEST_CASES = [
    {
        "name": "Simple product query",
        "query": "add pen",
        "expected": {
            "product": "pen",
            "brand": None,
            # ... other fields
        }
    },
    # ... more test cases
]
```
- **Line 8-220**: Define test cases with expected outputs
- **Why list of dicts**: Easy to add/modify test cases
- **Why expected**: Validates parser extracts correct data

```python
def test_intent_parser():
    """Test the intent parser with various queries"""
```
- **Line 222-223**: Function to test intent parser
- **Why separate function**: Can run parser tests without browser automation (faster)

```python
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] Testing: {test_case['name']}")
        print(f"Query: '{test_case['query']}'")
```
- **Line 227-231**: Track test results and iterate through test cases
- **Why counters**: Provides summary statistics

```python
        try:
            intent = parse_intent(test_case['query'])
            expected = test_case['expected']
            
            # Check each field
            errors = []
            if intent.product.lower() != expected['product'].lower():
                errors.append(f"Product: expected '{expected['product']}', got '{intent.product}'")
            # ... check other fields
```
- **Line 233-245**: Parse query and validate each field
- **Why case-insensitive**: "Pen" vs "pen" should both work
- **Why collect errors**: Show all failures at once, not stop on first

```python
            if errors:
                print(f"❌ FAILED")
                for error in errors:
                    print(f"   - {error}")
                failed += 1
            else:
                print(f"✅ PASSED")
                passed += 1
```
- **Line 286-294**: Display test results
- **Why visual indicators**: Easy to see pass/fail at a glance

```python
async def test_browser_agent(test_queries=None):
    """Test the browser agent with actual automation (optional - takes time)"""
```
- **Line 309-310**: Function to test full browser automation
- **Why optional**: Takes minutes per test, may not want to run always

```python
    if test_queries is None:
        # Use a subset of simpler queries for browser testing
        test_queries = [
            "add pen with price less than 20 rs",
            "add prestige cooker",
        ]
```
- **Line 317-321**: Use simpler queries for browser tests
- **Why**: Faster tests, less likely to fail due to Amazon changes

```python
        try:
            intent = parse_intent(query)
            print(f"Parsed intent: {intent.product}")
            # ... display intent details
            
            print("Running browser agent... (this may take 2-5 minutes)")
            result = await run_browser_agent(intent)
```
- **Line 328-336**: Parse query and run browser agent
- **Why async/await**: Browser agent is async function

```python
            if result and hasattr(result, 'items') and len(result.items) > 0:
                print(f"✅ PASSED - Item added to cart")
                item = result.items[0]
                print(f"   Product: {item.name}")
                print(f"   Price: ₹{item.price}")
                print(f"   Rating: {item.rating}")
                print(f"   URL: {item.url}")
                passed += 1
```
- **Line 338-347**: Validate result and display product info
- **Why validate structure**: Ensures agent returns correct format

```python
def main():
    """Main test function"""
    parser_passed, parser_failed = test_intent_parser()
    
    # Ask user if they want to run browser automation tests
    run_browser_tests = True  # Can be set to False for faster tests
```
- **Line 356-363**: Main function orchestrates all tests
- **Why configurable**: Can skip slow browser tests during development

```python
    if run_browser_tests:
        try:
            browser_passed, browser_failed = asyncio.run(test_browser_agent())
        except KeyboardInterrupt:
            print("\n\nBrowser tests interrupted by user")
```
- **Line 365-370**: Run browser tests if enabled
- **Why KeyboardInterrupt handling**: Allow user to cancel long-running tests

```python
    total_passed = parser_passed + browser_passed
    total_failed = parser_failed + browser_failed
    print(f"\nTotal: {total_passed} passed, {total_failed} failed out of {total_tests} tests")
```
- **Line 380-382**: Calculate and display summary statistics

```python
    # Exit with error code if any tests failed
    if total_failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)
```
- **Line 384-387**: Exit with error code for CI/CD integration
- **Why**: Automated testing systems check exit codes

---

## Setup and Installation

1. **Install Dependencies**:
```bash
pip install fastapi uvicorn streamlit requests langchain-openai browser-use pydantic python-dotenv playwright
playwright install  # Install browser drivers
```

2. **Create .env file**:
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. **Start API Server**:
```bash
uvicorn api:app --reload --port 8000
```

4. **Start UI** (in another terminal):
```bash
streamlit run ui.py
```

5. **Run Tests**:
```bash
python test.py
```

---

## Usage

1. Open UI in browser (usually http://localhost:8501)
2. Enter a natural language query (e.g., "add prestige cooker 3 ltr")
3. Click "Add to Cart"
4. Wait for automation to complete (2-5 minutes)
5. View result - product link will be displayed

---

## Example Queries

- Simple: "add pen"
- With price: "add pen with price less than 20 rs"
- With rating: "add pen with more user rating"
- With brand: "add prestige cooker 3 ltr"
- With color: "add Oneplus 15r in black"
- Combined: "add samsung phone in black under 30000 with good rating"
- Sort: "add cheapest phone", "add best rated pen"

---

## Why Each Design Decision

1. **LangChain for Intent Parsing**: Provides structure, handles prompts, manages LLM responses
2. **browser-use for Automation**: High-level automation with LLM decision making, easier than raw Playwright
3. **FastAPI Backend**: Async support, automatic docs, fast performance
4. **Streamlit UI**: Quick to build, good for demos, handles state automatically
5. **Pydantic Models**: Type safety, validation, better IDE support
6. **Modular Structure**: Each component can be tested/modified independently
7. **Comprehensive Error Handling**: Prevents crashes, provides clear error messages
8. **Timeout Protection**: Prevents hanging on slow/failed automation
9. **Test Suite**: Ensures system works with various query formats

---

## Future Improvements

1. Support for multiple items in one query
2. User authentication for real Amazon accounts
3. Order confirmation (not just add to cart)
4. Price drop alerts
5. Product comparison
6. Review summarization
7. Faster automation (parallel processing, caching)
