# from browser_use import Agent, Browser, ChatOpenAI
# from automation.models import CartResult, ProductIntent
# from dotenv import load_dotenv

# load_dotenv()

# # ---------------------------------------------------------
# # CONSTANTS
# # ---------------------------------------------------------

# SPONSORED_URL_PATTERNS = [
#     "/sspa/",
#     "sp_atk",
#     "sp_csd",
#     "sp_btf",
#     "sp_"
# ]

# MAX_FILTER_ATTEMPTS = 2
# MAX_SCROLL_ATTEMPTS = 2

# # ---------------------------------------------------------
# # INTENT CLASSIFICATION
# # ---------------------------------------------------------

# def is_generic_intent(intent: ProductIntent) -> bool:
#     """
#     Generic intent = no brand, no color, very short product name
#     """
#     print(intent)
#     return (
#         not intent.brand
#         and not intent.color
#         and len(intent.product.split()) <= 2
#     )

# # ---------------------------------------------------------
# # TASK BUILDER
# # ---------------------------------------------------------

# def build_task(intent: ProductIntent) -> str:
#     print(intent)
#     generic_mode = is_generic_intent(intent)

#     search_query = intent.product
#     if intent.brand:
#         search_query = f"{intent.brand} {intent.product}"

#     price_filter_text = ""
#     if intent.min_price and intent.max_price:
#         price_filter_text = f"₹{intent.min_price} – ₹{intent.max_price}"
#     elif intent.max_price:
#         price_filter_text = f"Under ₹{intent.max_price}"
#     elif intent.min_price:
#         price_filter_text = f"Over ₹{intent.min_price}"

#     rating_filter_text = (
#         f"{intent.min_rating} Stars & Up"
#         if intent.min_rating else ""
#     )

#     return f"""
# You are a HUMAN shopping on Amazon India.

# ==================================================
# ABSOLUTE RULES (NEVER BREAK)
# ==================================================

# 1. ❌ SPONSORED PRODUCTS ARE FORBIDDEN
#    - If label shows "Sponsored", "Ad", "Promoted" → DISCARD
#    - If URL contains:
#      {", ".join(SPONSORED_URL_PATTERNS)}
#      → DISCARD IMMEDIATELY

# 2. 🛑 ADD TO CART ONLY ONCE
#    - Click Add to Cart exactly ONE TIME
#    - Never retry
#    - Never add alternatives

# 3. 🎯 INTENT MODE
#    - {"GENERIC MODE" if generic_mode else "EXACT MATCH MODE"}

# ==================================================
# STEP 1 — SEARCH
# ==================================================

# - Go to https://www.amazon.in
# - Wait 4–5 seconds
# - Type "{search_query}" in the search box
# - Press Enter
# - Wait for results page to fully load

# ==================================================
# STEP 2 — TRY FILTERS FIRST (OPTIONAL BUT PREFERRED)
# ==================================================

# - Humans use filters when they are easy
# - Filters are OPTIONAL — do NOT get stuck

# TRY THIS (max {MAX_FILTER_ATTEMPTS} attempts total):

# PRICE FILTER (if available):
# {"- Look in LEFT sidebar for 'Price'" if price_filter_text else ""}
# {"- Try clicking a matching range like '" + price_filter_text + "'" if price_filter_text else ""}
# {"- If clickable → apply and wait 3–4 seconds" if price_filter_text else ""}
# {"- If not clickable or missing → SKIP price filter" if price_filter_text else ""}

# RATING FILTER (if available):
# {"- Look for 'Avg. Customer Review'" if rating_filter_text else ""}
# {"- Click '" + rating_filter_text + "'" if rating_filter_text else ""}
# {"- If works → wait 3–4 seconds" if rating_filter_text else ""}
# {"- If not available → SKIP rating filter" if rating_filter_text else ""}

# IMPORTANT:
# - If ANY filter fails → skip filters entirely
# - Do NOT retry filters endlessly
# - Proceed to scrolling

# ==================================================
# STEP 3 — SCROLL (ALWAYS DO THIS)
# ==================================================

# - Scroll down at least 2 full screen heights
# - Sponsored products usually appear first
# - Humans scroll past ads

# ==================================================
# STEP 4 — EXTRACT PRODUCTS (NON-SPONSORED ONLY)
# ==================================================

# - Extract 30–40 products
# - Extract:
#   - name
#   - price (number)
#   - rating (number)
#   - COMPLETE URL

# - DISCARD immediately if:
#   - Sponsored label exists
#   - URL contains sponsored patterns

# ==================================================
# STEP 5 — SELECT PRODUCT
# ==================================================

# {"GENERIC MODE RULES:" if generic_mode else "EXACT MATCH MODE RULES:"}

# {"- Select the FIRST product that satisfies price & rating" if generic_mode else ""}
# {"- Do NOT search for best or cheapest" if generic_mode else ""}
# {"- Humans pick the first acceptable option" if generic_mode else ""}

# {"- Product name MUST match: " + intent.product if not generic_mode else ""}
# {"- Brand MUST match: " + intent.brand if intent.brand and not generic_mode else ""}
# {"- Color MUST match: " + intent.color if intent.color and not generic_mode else ""}

# Numeric rules:
# {"- Price ≥ ₹" + str(intent.min_price) if intent.min_price else ""}
# {"- Price ≤ ₹" + str(intent.max_price) if intent.max_price else ""}
# {"- Rating ≥ " + str(intent.min_rating) + " stars" if intent.min_rating else ""}

# - Pick FIRST valid product
# - If none found:
#   - Scroll once more (max {MAX_SCROLL_ATTEMPTS})
#   - Extract again
# - If still none → RETURN ERROR

# ==================================================
# STEP 6 — VERIFY ON PRODUCT PAGE
# ==================================================

# - Navigate using COMPLETE product URL
# - Wait 4–5 seconds

# VERIFY:
# - Product is NOT sponsored
# {"- Name match NOT required (generic)" if generic_mode else "- Name must match intent"}
# {"- Brand matches" if intent.brand and not generic_mode else ""}
# {"- Color matches" if intent.color and not generic_mode else ""}
# {"- Price rule satisfied" if intent.min_price or intent.max_price else ""}
# {"- Rating rule satisfied" if intent.min_rating else ""}

# GENERIC MODE SPECIAL RULE:
# - If price/rating mismatch:
#   - Go BACK
#   - Try NEXT extracted product
#   - Do NOT scroll again

# EXACT MODE:
# - Any mismatch → FAIL

# ==================================================
# STEP 7 — ADD TO CART (ONE TIME ONLY)
# ==================================================

# - Click main "Add to Cart" button ONCE
# - Wait 4–5 seconds
# - Dismiss warranty popups if needed
# - DO NOT click again

# ==================================================
# STEP 8 — CONFIRM SUCCESS
# ==================================================

# Confirm success via ANY:
# - "Added to Cart" message
# - Cart count increased
# - "Proceed to Buy" visible

# If confirmed:
# - Use DONE action
# - Return CartResult JSON

# If not:
# - RETURN ERROR

# ==================================================
# FINAL RULE
# ==================================================

# - After DONE → STOP
# - No retries
# - No file writes
# """

# # ---------------------------------------------------------
# # RUNNER
# # ---------------------------------------------------------

# async def run_browser_agent(intent: ProductIntent) -> CartResult:
#     """
#     Production-safe runner:
#     - Uses filters when easy
#     - Falls back cleanly
#     - Never loops
#     - Never adds wrong item
#     """

#     agent = Agent(
#         browser=Browser(headless=False),
#         llm=ChatOpenAI(model="gpt-4o-mini"),
#         task=build_task(intent),
#         output_model_schema=CartResult,
#         max_steps=40
#     )

#     return await agent.run()

# ==================================================================================================================================

from browser_use import Agent, Browser, ChatOpenAI
from automation.models import CartResult, ProductIntent
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# =========================================================
# CONFIGURATION
# =========================================================

AMAZON_URL = "https://www.amazon.in"

SPONSORED_URL_PATTERNS = (
    "/sspa/",
    "sp_atk",
    "sp_csd",
    "sp_btf",
    "sp_",
)

MAX_FILTER_ATTEMPTS = 2
MAX_SCROLL_ATTEMPTS = 2
MAX_AGENT_STEPS = 40

MODEL_NAME = "gpt-4o-mini"


# =========================================================
# VALIDATION
# =========================================================

def validate_intent(intent: ProductIntent) -> None:
    """Fail fast on invalid intent"""
    if not intent.product or not intent.product.strip():
        raise ValueError("Product name is required")

    if intent.min_price and intent.max_price:
        if intent.min_price > intent.max_price:
            raise ValueError("min_price cannot exceed max_price")

    if intent.min_rating:
        if not (0 < intent.min_rating <= 5):
            raise ValueError("min_rating must be between 0 and 5")


# =========================================================
# INTENT MODE
# =========================================================

def is_generic_intent(intent: ProductIntent) -> bool:
    """
    Generic intent:
    - No brand
    - No color
    - Very short product name
    """
    return (
        not intent.brand
        and not intent.color
        and len(intent.product.split()) <= 2
    )


# =========================================================
# TASK BUILDER
# =========================================================

def build_task(intent: ProductIntent) -> str:
    validate_intent(intent)

    generic_mode = is_generic_intent(intent)

    search_query = (
        f"{intent.brand} {intent.product}"
        if intent.brand
        else intent.product
    )

    price_text = ""
    if intent.min_price and intent.max_price:
        price_text = f"₹{intent.min_price} – ₹{intent.max_price}"
    elif intent.max_price:
        price_text = f"Under ₹{intent.max_price}"
    elif intent.min_price:
        price_text = f"Over ₹{intent.min_price}"

    rating_text = (
        f"{intent.min_rating} Stars & Up"
        if intent.min_rating else ""
    )

    return f"""
You are a REAL HUMAN shopping on Amazon India.

==================================================
ABSOLUTE RULES (NEVER BREAK)
==================================================

1. ❌ NO SPONSORED PRODUCTS
   - If label shows: Sponsored / Ad / Promoted → DISCARD
   - If URL contains any of:
     {", ".join(SPONSORED_URL_PATTERNS)}
     → DISCARD IMMEDIATELY

2. 🛑 ADD TO CART EXACTLY ONCE
   - One click only
   - No retries
   - No alternatives

3. 🎯 MODE
   - {"GENERIC MODE" if generic_mode else "EXACT MATCH MODE"}

==================================================
STEP 1 — SEARCH
==================================================

- Go to {AMAZON_URL}
- Wait 4–5 seconds
- Search for: "{search_query}"
- Press Enter
- Wait for results to load

==================================================
STEP 2 — OPTIONAL FILTERS (DO NOT GET STUCK)
==================================================

ATTEMPTS: max {MAX_FILTER_ATTEMPTS}

PRICE FILTER:
{f"- Try '{price_text}' if available" if price_text else "- Skip (no price constraint)"}

RATING FILTER:
{f"- Try '{rating_text}' if available" if rating_text else "- Skip (no rating constraint)"}

RULE:
- If ANY filter fails → stop filtering and continue

==================================================
STEP 3 — SCROLL
==================================================

- Scroll down 1 full screen heights
- Sponsored items usually appear first

==================================================
STEP 4 — EXTRACT PRODUCTS
==================================================

- Extract 30–40 products
- For EACH product collect:
  - name
  - price (number)
  - rating (number)
  - FULL URL

IMMEDIATE DISCARD IF:
- Sponsored label exists
- URL matches sponsored patterns

==================================================
STEP 5 — SELECT FIRST VALID PRODUCT
==================================================

{"GENERIC MODE:" if generic_mode else "EXACT MODE:"}

{"- Select FIRST product meeting numeric rules" if generic_mode else ""}
{"- Do NOT optimize or compare" if generic_mode else ""}

{"- Name must match: " + intent.product if not generic_mode else ""}
{"- Brand must match: " + intent.brand if intent.brand and not generic_mode else ""}
{"- Color must match: " + intent.color if intent.color and not generic_mode else ""}

NUMERIC RULES:
{f"- Price ≥ ₹{intent.min_price}" if intent.min_price else ""}
{f"- Price ≤ ₹{intent.max_price}" if intent.max_price else ""}
{f"- Rating ≥ {intent.min_rating}" if intent.min_rating else ""}

- Pick FIRST valid product only
- If none found:
  - Scroll once more (max {MAX_SCROLL_ATTEMPTS})
  - Extract again
- If still none → FAIL

==================================================
STEP 6 — VERIFY PRODUCT PAGE (SAME TAB ONLY)
==================================================

- DO NOT click product title links
- DO NOT open new tabs
- Use the FULL product URL
- Navigate in the SAME tab by:
  - Typing URL in address bar OR
  - Direct navigation (window.location.href)

- Wait 4–5 seconds

==================================================
STEP 7 — ADD TO CART (ONCE)
==================================================

- Click "Add to Cart" ONCE
- Wait 4–5 seconds
- Close warranty popups if shown

🚫 ADD TO CART FIREWALL
- NEVER click "Add to Cart" on search/results pages
- ONLY add to cart on product detail page (/dp/ or /gp/aw/d/)
- If cart count increases before product page → FAIL


==================================================
STEP 8 — CONFIRM
==================================================

SUCCESS IF ANY:
- "Added to Cart" message
- Cart count increased
- "Proceed to Buy" visible

If success:
- DONE
- Return CartResult JSON

If failure:
- RETURN ERROR

FINAL RULE:
- After DONE → STOP
- No retries
"""

# =========================================================
# RUNNER
# =========================================================

# async def run_browser_agent(intent: ProductIntent) -> CartResult:
#     """
#     Industry-grade runner:
#     - Deterministic
#     - No infinite loops
#     - Strict non-sponsored selection
#     - Guaranteed first valid product
#     """

#     validate_intent(intent)

#     agent = Agent(
#         browser=Browser(headless=False),
#         llm=ChatOpenAI(model=MODEL_NAME),
#         task=build_task(intent),
#         output_model_schema=CartResult,
#         max_steps=MAX_AGENT_STEPS,
#     )

#     result: CartResult = await agent.run()

#     if not result or not result.success:
#         return CartResult(
#             success=False,
#             message="No non-sponsored product matched the criteria",
#             product=None,
#         )

#     return result



async def run_browser_agent(intent: ProductIntent) -> CartResult:
    validate_intent(intent)

    agent = Agent(
        browser=Browser(headless=False),
        llm=ChatOpenAI(model=MODEL_NAME),
        task=build_task(intent),
        output_model_schema=CartResult,
        max_steps=MAX_AGENT_STEPS,
    )

    result = await agent.run()

    # -----------------------------------------
    # Try structured_output first (browser-use convention)
    # -----------------------------------------
    if hasattr(result, 'structured_output') and result.structured_output:
        return result.structured_output

    # -----------------------------------------
    # Fallback: Extract DONE payload from history
    # -----------------------------------------
    if hasattr(result, 'steps'):
        done_events = [
            step for step in result.steps
            if hasattr(step, 'action_name') and step.action_name == "done"
        ]

        if done_events:
            final_data = done_events[-1].action_input
            if final_data and final_data.get("items"):
                return CartResult(items=final_data["items"])

    return CartResult(items=[])

