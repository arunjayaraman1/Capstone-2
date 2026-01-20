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



from browser_use import Agent, Browser, ChatOpenAI
from automation.models import CartResult, ProductIntent
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------

SPONSORED_URL_PATTERNS = [
    "/sspa/",
    "sp_atk",
    "sp_csd",
    "sp_btf",
    "sp_"
]

MAX_FILTER_ATTEMPTS = 2
MAX_SCROLL_ATTEMPTS = 2
MAX_PRODUCT_PAGE_REJECTIONS = 3

# ---------------------------------------------------------
# INTENT CLASSIFICATION
# ---------------------------------------------------------

def is_generic_intent(intent: ProductIntent) -> bool:
    return (
        not intent.brand
        and not intent.color
        and len(intent.product.split()) <= 2
    )

# ---------------------------------------------------------
# TASK BUILDER
# ---------------------------------------------------------

def build_task(intent: ProductIntent) -> str:
    generic_mode = is_generic_intent(intent)

    search_query = intent.product
    if intent.brand:
        search_query = f"{intent.brand} {intent.product}"

    return f"""
You are a HUMAN shopping on Amazon India.

==================================================
ABSOLUTE RULES (NEVER BREAK)
==================================================

1. ❌ SPONSORED PRODUCTS ARE FORBIDDEN
   - If label shows "Sponsored", "Ad", "Promoted" → DISCARD
   - If URL contains:
     {", ".join(SPONSORED_URL_PATTERNS)}
     → DISCARD IMMEDIATELY

2. 🛑 ADD TO CART ONLY ONCE
   - Click Add to Cart exactly ONE TIME
   - Never retry
   - Never add alternatives

3. 🎯 INTENT MODE
   - {"GENERIC MODE" if generic_mode else "EXACT MATCH MODE"}

==================================================
STEP 1 — SEARCH
==================================================

- Go to https://www.amazon.in
- Wait 4–5 seconds
- Type "{search_query}" in the search box
- Press Enter
- Wait for results page to fully load

==================================================
STEP 2 — TRY FILTERS FIRST (OPTIONAL, HUMAN-GUARDED)
==================================================

Filters are OPTIONAL. Humans use them only if they HELP.

-------------------------
RATING FILTER (SAFE)
-------------------------
{"- Look for 'Avg. Customer Review'" if intent.min_rating else ""}
{"- Click '" + str(intent.min_rating) + " Stars & Up' if available" if intent.min_rating else ""}
{"- If clickable → apply and wait 3–4 seconds" if intent.min_rating else ""}
{"- If missing → SKIP rating filter" if intent.min_rating else ""}

-------------------------
PRICE FILTER (STRICT HUMAN RULES)
-------------------------

Intent:
{"- Minimum price: ₹" + str(intent.min_price) if intent.min_price else ""}
{"- Maximum price: ₹" + str(intent.max_price) if intent.max_price else ""}

PRICE FILTER SAFETY RULES (CRITICAL):

1. If BOTH min and max are given:
   - Click ONLY ranges that OVERLAP the intent range
   - Example: ₹300–₹500 overlaps ₹300–₹400 → OK

2. If ONLY min_price is given (no max):
   - Prefer the CLOSEST lower-bound range
   - Example: min ₹200 → prefer ₹200–₹300 or ₹200–₹400
   - NEVER jump to "Over ₹700" or very high ranges

3. If ONLY max_price is given:
   - Prefer the CLOSEST upper-bound range

4. If no reasonable filter exists:
   - SKIP price filter entirely

IMPORTANT:
- NEVER click a price filter that unnecessarily narrows results
- If unsure → SKIP price filter
- Rating + manual check is safer than wrong price filters

==================================================
STEP 3 — SCROLL (ALWAYS)
==================================================

- Scroll down at least 2 full screen heights
- Sponsored products usually appear first
- Humans scroll past ads

==================================================
STEP 4 — EXTRACT PRODUCTS (NON-SPONSORED ONLY)
==================================================

- Extract 30–40 products
- Extract:
  - name
  - price (number)
  - rating (number)
  - COMPLETE URL

- DISCARD immediately if:
  - Sponsored label exists
  - URL contains sponsored patterns

==================================================
STEP 5 — SELECT PRODUCT
==================================================

GENERIC MODE RULES:
- Select the FIRST product that satisfies numeric rules
- Do NOT search for best or cheapest
- Humans pick the first acceptable option

Numeric rules:
{"- Price ≥ ₹" + str(intent.min_price) if intent.min_price else ""}
{"- Price ≤ ₹" + str(intent.max_price) if intent.max_price else ""}
{"- Rating ≥ " + str(intent.min_rating) + " stars" if intent.min_rating else ""}

- Pick FIRST valid product
- If none found:
  - Scroll once more (max {MAX_SCROLL_ATTEMPTS})
  - Extract again
- If still none → RETURN ERROR

==================================================
STEP 6 — VERIFY ON PRODUCT PAGE
==================================================

- Navigate using COMPLETE product URL
- Wait 4–5 seconds

VERIFY:
- Product is NOT sponsored
{"- Name match NOT required (generic)" if generic_mode else "- Name must match intent"}
{"- Price rule satisfied" if intent.min_price or intent.max_price else ""}
{"- Rating rule satisfied" if intent.min_rating else ""}

GENERIC MODE SPECIAL RULE:
- If price/rating mismatch:
  - Go BACK
  - Try NEXT extracted product
  - DO NOT scroll again
  - Max {MAX_PRODUCT_PAGE_REJECTIONS} rejections

==================================================
STEP 7 — ADD TO CART (ONE TIME ONLY)
==================================================

- Click main "Add to Cart" button ONCE
- Wait 4–5 seconds
- Dismiss warranty popups if needed
- DO NOT click again

==================================================
STEP 8 — CONFIRM SUCCESS
==================================================

Confirm success via ANY:
- "Added to Cart" message
- Cart icon count increased
- "Proceed to Buy" visible

If confirmed:
- Use DONE action
- Return CartResult JSON

==================================================
FINAL RULE
==================================================

- After DONE → STOP
- No retries
- No file writes
"""

# ---------------------------------------------------------
# RUNNER
# ---------------------------------------------------------

async def run_browser_agent(intent: ProductIntent) -> CartResult:
    agent = Agent(
        browser=Browser(headless=False),
        llm=ChatOpenAI(model="gpt-4o-mini"),
        task=build_task(intent),
        output_model_schema=CartResult,
        max_steps=45
    )

    return await agent.run()
