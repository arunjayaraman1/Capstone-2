from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from automation.models import ProductIntent
import json
import re
from dotenv import load_dotenv 
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_template(
    """
You are an expert at extracting shopping intent from natural language queries.

Extract the shopping intent from the user query and return ONLY valid JSON.

QUERY ANALYSIS RULES:
1. PRODUCT NAME: Extract the main product/item the user wants to buy (e.g., "pen", "laptop", "phone")
   - Remove color/size/other attributes from product name - extract only the base product
   - Example: "Oneplus 15r in black" → product: "Oneplus 15r"

2. COLOR CONSTRAINTS:
   - If user mentions a color (e.g., "black", "white", "red", "blue", "mint", "silver", "gold", etc.), extract it
   - Common patterns: "X in color", "X color", "color X", "black X", "white X", etc.
   - Examples: 
     * "Oneplus 15r in black" → product: "Oneplus 15r", color: "black"
     * "black pen" → product: "pen", color: "black"
     * "laptop white" → product: "laptop", color: "white"
   - Extract color as lowercase string (e.g., "black", "white", "mint breeze", "silver")
   - If no color mentioned, color = null

3. PRICE CONSTRAINTS:
   - If user says "less than X", "below X", "under X", "maximum X", "up to X", "not more than X" → max_price = X
   - If user says "more than X", "above X", "at least X", "minimum X", "starting from X" → min_price = X
   - If user says "between X and Y" → min_price = X, max_price = Y
   - Currency indicators (rs, rupees, ₹, $, etc.) should be ignored, extract just the number
   - Examples: "less than 20 rs" → max_price: 20, "above 500 rupees" → min_price: 500

3. RATING CONSTRAINTS:
   - If user says "high rating", "good rating", "more rating", "better rating", "well rated", "highly rated" → min_rating = 4.0 (assume they want good products)
   - If user says "rating above X", "rating more than X", "minimum X stars", "at least X stars" → min_rating = X
   - If user says "rating below X", "rating less than X", "maximum X stars" → max_rating = X
   - If user says "best rated", "top rated", "highest rating" → sort_by = "rating_desc"
   - Star ratings: Extract numeric value (e.g., "4 stars" → 4.0, "4.5 stars" → 4.5)

4. SORT PREFERENCES:
   - "cheapest", "lowest price", "low price", "affordable", "budget" → sort_by: "price_asc"
   - "expensive", "highest price", "premium" → sort_by: "price_desc"
   - "best rated", "highest rating", "top rated", "well rated" → sort_by: "rating_desc"
   - "worst rated", "lowest rating" → sort_by: "rating_asc"
   - "most popular", "best selling" → sort_by: null (use default/best match)

5. COMMON PATTERNS:
   - "add X with price less than Y" → product: "X", max_price: Y
   - "add X with more user rating" → product: "X", min_rating: 4.0 or sort_by: "rating_desc"
   - "add X with good rating" → product: "X", min_rating: 4.0
   - "cheap X", "affordable X" → product: "X", sort_by: "price_asc"
   - "best X", "top X" → product: "X", sort_by: "rating_desc"
   - "X in color", "color X", "black X", "white X" → extract color separately

RETURN FORMAT (ONLY valid JSON, no markdown, no explanation):
{{
  "product": "extracted product name as string (without color/size attributes)",
  "max_price": number or null,
  "min_price": number or null,
  "min_rating": number or null,
  "max_rating": number or null,
  "sort_by": "price_asc" or "price_desc" or "rating_asc" or "rating_desc" or null,
  "color": "color name as lowercase string or null"
}}

EXAMPLES:
Query: "add pen with price less than 20 rs"
Response: {{"product": "pen", "max_price": 20, "min_price": null, "min_rating": null, "max_rating": null, "sort_by": null, "color": null}}

Query: "add pen with more user rating"
Response: {{"product": "pen", "max_price": null, "min_price": null, "min_rating": 4.0, "max_rating": null, "sort_by": "rating_desc", "color": null}}

Query: "add laptop under 50000 with good rating"
Response: {{"product": "laptop", "max_price": 50000, "min_price": null, "min_rating": 4.0, "max_rating": null, "sort_by": null, "color": null}}

Query: "add cheapest phone"
Response: {{"product": "phone", "max_price": null, "min_price": null, "min_rating": null, "max_rating": null, "sort_by": "price_asc", "color": null}}

Query: "add Oneplus 15r in black"
Response: {{"product": "Oneplus 15r", "max_price": null, "min_price": null, "min_rating": null, "max_rating": null, "sort_by": null, "color": "black"}}

Query: "add black pen"
Response: {{"product": "pen", "max_price": null, "min_price": null, "min_rating": null, "max_rating": null, "sort_by": null, "color": "black"}}

User query:
{query}

Return ONLY the JSON object, no additional text:
    """
)

def parse_intent(query:str)-> ProductIntent:
    """
    Parse natural language query into structured ProductIntent using LangChain.
    Handles various query formats like:
    - "add pen with price less than 20 rs"
    - "add pen with more user rating"
    - "add laptop under 50000 with good rating"
    """
    response = llm.invoke(prompt.format(query=query))
    content = response.content.strip()
    
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
    
    # Try to parse JSON directly
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # If direct parsing fails, try to extract JSON object using regex
        # This handles nested objects and arrays
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
    
    # Validate and create ProductIntent
    try:
        return ProductIntent(**data)
    except Exception as e:
        raise ValueError(f"Failed to create ProductIntent from parsed data: {data}. Error: {str(e)}")