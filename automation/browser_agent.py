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
    - No hard brand constraint
    - Minimal hard constraints
    - Very short product name
    """
    has_hard_brand = intent.hard_constraints.get('brand')
    has_many_attributes = len(intent.attributes) > 2
    has_specific_model = len(intent.product.split()) > 2
    
    return (
        not has_hard_brand
        and not has_many_attributes
        and not has_specific_model
    )


def build_search_query(intent: ProductIntent, brand_override: Optional[str] = None) -> str:
    """
    Build Amazon search query from product + attributes + soft preferences.
    
    Args:
        intent: ProductIntent with search criteria
        brand_override: If provided, use this brand instead of intent brands (for multi-brand search)
    """
    parts = [intent.product]
    
    # Add attributes to search (color, connectivity, type, etc.)
    if intent.attributes:
        parts.extend(intent.attributes.values())
    
    # Add hard brand constraint if present
    hard_brand = intent.hard_constraints.get('brand')
    if hard_brand:
        parts.insert(0, hard_brand)
        return " ".join(str(p) for p in parts if p)
    
    # Use brand override if provided (for multi-brand iteration)
    if brand_override:
        parts.insert(0, brand_override)
        return " ".join(str(p) for p in parts if p)
    
    # Add soft brand preference to search (helps ranking)
    soft_brand = intent.soft_preferences.get('brand')
    if soft_brand:
        parts.insert(0, soft_brand)
    
    # Check for multiple brands (list)
    soft_brands = intent.soft_preferences.get('brands')
    if soft_brands and isinstance(soft_brands, list) and soft_brands:
        # Use first brand for initial search
        parts.insert(0, soft_brands[0])
    
    return " ".join(str(p) for p in parts if p)


def build_filter_instructions(intent: ProductIntent) -> tuple[str, str, str]:
    """
    Build filter instructions for price, rating, and discount.
    Returns (price_text, rating_text, discount_text)
    """
    price_text = ""
    rating_text = ""
    discount_text = ""
    
    # Price filter
    price_constraint = intent.hard_constraints.get('price', {})
    min_price = price_constraint.get('min')
    max_price = price_constraint.get('max')
    
    if min_price and max_price:
        price_text = f"₹{min_price} – ₹{max_price}"
    elif max_price:
        price_text = f"Under ₹{max_price}"
    elif min_price:
        price_text = f"Over ₹{min_price}"
    
    # Rating filter
    rating_constraint = intent.hard_constraints.get('rating', {})
    min_rating = rating_constraint.get('min')
    
    if min_rating:
        rating_text = f"{min_rating} Stars & Up"
    
    # Discount filter
    discount_constraint = intent.hard_constraints.get('discount', {})
    min_discount = discount_constraint.get('min')
    
    if min_discount:
        # Find closest Amazon discount filter
        # Amazon typically has: 10%, 25%, 50%, 60% filters
        if min_discount >= 50:
            discount_text = "50% Off or more"
        elif min_discount >= 25:
            discount_text = "25% Off or more"
        elif min_discount >= 10:
            discount_text = "10% Off or more"
        else:
            discount_text = f"{min_discount}% Off or more"
    
    return price_text, rating_text, discount_text


def build_selection_rules(intent: ProductIntent, generic_mode: bool) -> str:
    """
    Build product selection rules based on intent.
    """
    rules = []
    
    # Hard constraints (MUST satisfy)
    rules.append("HARD CONSTRAINTS (MUST SATISFY):")
    
    # Price constraint
    price_constraint = intent.hard_constraints.get('price', {})
    min_price = price_constraint.get('min')
    max_price = price_constraint.get('max')
    if min_price:
        rules.append(f"- Price ≥ ₹{min_price}")
    if max_price:
        rules.append(f"- Price ≤ ₹{max_price}")
    
    # Rating constraint
    rating_constraint = intent.hard_constraints.get('rating', {})
    min_rating = rating_constraint.get('min')
    max_rating = rating_constraint.get('max')
    if min_rating:
        rules.append(f"- Rating ≥ {min_rating} stars")
    if max_rating:
        rules.append(f"- Rating ≤ {max_rating} stars")
    
    # Discount constraint
    discount_constraint = intent.hard_constraints.get('discount', {})
    min_discount = discount_constraint.get('min')
    if min_discount:
        rules.append(f"- Discount ≥ {min_discount}%")
    
    # Hard brand constraint
    hard_brand = intent.hard_constraints.get('brand')
    if hard_brand and not generic_mode:
        rules.append(f"- Brand MUST be: {hard_brand}")
    
    # Product attributes (should match search context)
    if intent.attributes and not generic_mode:
        rules.append("\nPRODUCT ATTRIBUTES (should be present in listing):")
        for attr_name, attr_value in intent.attributes.items():
            rules.append(f"- {attr_name.title()}: {attr_value}")
    
    # Soft preferences (nice to have, use for sorting)
    if intent.soft_preferences:
        rules.append("\nSOFT PREFERENCES (prefer but not required):")
        
        # Single brand preference
        soft_brand = intent.soft_preferences.get('brand')
        if soft_brand:
            rules.append(f"- PREFER {soft_brand} but accept other brands if constraints met")
        
        # Multiple brands preference
        soft_brands = intent.soft_preferences.get('brands')
        if soft_brands and isinstance(soft_brands, list):
            brands_str = " OR ".join(soft_brands)
            rules.append(f"- PREFER {brands_str} (try each brand one by one)")
            rules.append(f"  Search order: {' → '.join(soft_brands)} → generic")
        
        # Other preferences
        for pref_name, pref_value in intent.soft_preferences.items():
            if pref_name not in ('brand', 'brands'):
                rules.append(f"- Prefer {pref_name}: {pref_value}")
    
    if not rules[1:]:  # Only header, no actual rules
        rules.append("- None (select first valid non-sponsored product)")
    
    return "\n".join(rules)


# =========================================================
# TASK BUILDER
# =========================================================

def build_task(intent: ProductIntent) -> str:
    validate_intent(intent)

    generic_mode = is_generic_intent(intent)
    search_query = build_search_query(intent)
    price_text, rating_text, discount_text = build_filter_instructions(intent)
    selection_rules = build_selection_rules(intent, generic_mode)
    
    # Check for multiple preferred brands
    soft_brands = intent.soft_preferences.get('brands', [])
    has_multiple_brands = isinstance(soft_brands, list) and len(soft_brands) > 1
    brand_search_instructions = ""
    
    if has_multiple_brands:
        brand_list = ", ".join(f"'{b}'" for b in soft_brands)
        brand_search_instructions = f"""
MULTI-BRAND SEARCH STRATEGY:
You have multiple preferred brands: {brand_list}

Try each brand ONE BY ONE:
1. Search "{soft_brands[0]} {intent.product}" first
2. Apply filters, scroll, extract products
3. If valid non-sponsored product found → NAVIGATE to it → Add to cart → DONE
4. If NO valid product found:
   - Go back to Amazon home
   - Search "{soft_brands[1] if len(soft_brands) > 1 else 'next'} {intent.product}"
   - Apply filters again
   - Extract products
   - If valid product found → NAVIGATE → Add to cart → DONE
{f'5. If still not found, try "{soft_brands[2]} {intent.product}"' if len(soft_brands) > 2 else ''}
{f'6. If no preferred brands work, search generic "{intent.product}"' if soft_brands else ''}

IMPORTANT:
- Try each brand separately with fresh search
- Only move to next brand if current brand has NO valid products
- Don't mix products from different brand searches
"""
    else:
        brand_search_instructions = ""

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
   - {"GENERIC MODE (flexible matching)" if generic_mode else "SPECIFIC MODE (match attributes + constraints)"}
{brand_search_instructions}
4. 🚫 ANTI-HALLUCINATION RULES
   - ONLY use actions that exist: navigate, click, input, extract, scroll, wait, evaluate, done
   - DO NOT try to input() into elements that don't exist
   - DO NOT use element indices from extracted data - use URLs
   - After finding valid product → NAVIGATE to its URL immediately
   - DO NOT scroll indefinitely - max {MAX_SCROLL_ATTEMPTS} scrolls
   - If stuck → FAIL with clear error, don't loop
   - DO NOT try to sign in or provide credentials
   - DO NOT proceed to checkout/payment
   - Task ends at "Add to Cart" - nothing after that

==================================================
STEP 1 — SEARCH
==================================================

- Go to {AMAZON_URL}
- Wait 4–5 seconds
- Search for: "{search_query}"
- Press Enter
- Wait for results to load

==================================================
STEP 2 — APPLY FILTERS (USE WHEN AVAILABLE)
==================================================

Amazon has filters in the LEFT SIDEBAR. USE THEM - they improve results quality!

FILTER DISCOVERY:
- Scroll down LEFT sidebar to see all available filters
- Common filters: Price, Rating, Discount, Brand, Size, Color, etc.

FILTERS TO APPLY (in order):

1. PRICE FILTER (if price constraint exists):
{f"   - Look for 'Price' section in left sidebar" if price_text else "   - Skip (no price constraint)"}
{f"   - Click on: '{price_text}' or closest matching range" if price_text else ""}
{f"   - If exact range not available, use 'Under ₹{price_text.split('₹')[-1]}' or similar" if price_text else ""}
{f"   - Wait 3-4 seconds after applying" if price_text else ""}

2. RATING FILTER (if rating constraint exists):
{f"   - Look for 'Customer Review' or 'Avg. Customer Review' section" if rating_text else "   - Skip (no rating constraint)"}
{f"   - Click on: '{rating_text}' or '⭐⭐⭐⭐ & Up'" if rating_text else ""}
{f"   - Wait 3-4 seconds after applying" if rating_text else ""}

3. DISCOUNT FILTER (if discount constraint exists):
{f"   - Look for 'Discount' or 'Offers' section in left sidebar" if discount_text else "   - Skip (no discount constraint)"}
{f"   - Scroll down sidebar if not visible initially" if discount_text else ""}
{f"   - Click on: '{discount_text}' or closest matching option" if discount_text else ""}
{f"   - Common options: '10% Off or more', '25% Off or more', '50% Off or more'" if discount_text else ""}
{f"   - Wait 3-4 seconds after applying" if discount_text else ""}

4. ATTRIBUTE FILTERS (size, color, brand):
{f"   - SIZE: Look for 'Size' filter, select '{intent.attributes.get('size')}'" if intent.attributes.get('size') else "   - Skip size (not specified)"}
{f"   - COLOR: Look for 'Colour' filter, select '{intent.attributes.get('color')}'" if intent.attributes.get('color') else "   - Skip color (not specified)"}
{f"   - BRAND: Look for 'Brand' filter, select '{intent.hard_constraints.get('brand')}'" if intent.hard_constraints.get('brand') else "   - Skip brand filter (not a hard constraint)"}

FILTERING STRATEGY:
- Try each relevant filter (max {MAX_FILTER_ATTEMPTS} attempts per filter)
- If a filter is not visible, scroll down the LEFT sidebar
- If a filter doesn't work after {MAX_FILTER_ATTEMPTS} attempts → skip it and continue
- Filters significantly reduce irrelevant results - use them when possible!

==================================================
STEP 3 — SCROLL
==================================================

- Scroll down 1–2 full screen heights
- Sponsored items usually appear first

==================================================
STEP 4 — EXTRACT PRODUCTS (ONE TIME)
==================================================

Extract visible products using extract() action:
- Extract ALL visible products on screen
- For EACH product collect:
  - name (full product name)
  - price (numeric value only, e.g. 78, 149)
  - rating (numeric value, e.g. 4.0, 4.3)
  - FULL URL (must include /dp/ or product identifier)

IMMEDIATE DISCARD IF:
- Product has "Sponsored" label
- URL contains: {", ".join(SPONSORED_URL_PATTERNS)}

AFTER EXTRACTION:
- Create a filtered list of NON-SPONSORED products only
- Sort by soft preferences if any (e.g. preferred brand first)
- Proceed immediately to STEP 5
- DO NOT extract again unless no valid products found

==================================================
STEP 5 — SELECT & NAVIGATE TO PRODUCT
==================================================

{selection_rules}

SELECTION STRATEGY:
{"- Select FIRST product meeting hard constraints" if generic_mode else "- Select FIRST product meeting all hard constraints + attributes"}
- If soft preferences exist: PREFER matching products but DON'T reject if they don't match
- Example: If prefer Logitech, sort Logitech first, but accept other brands if they match hard constraints

CRITICAL: After identifying the FIRST valid product:

1. GET THE PRODUCT URL from extracted data
   - Example: https://www.amazon.in/dp/B074N7X12P
   
2. NAVIGATE to that URL immediately:
   - Use navigate(url=PRODUCT_URL) action
   - OR use evaluate: window.location.href = "PRODUCT_URL"
   - DO NOT try to click elements by index
   - DO NOT open new tabs
   
3. Wait 4-5 seconds for page load

4. STOP scrolling - you found a valid product!

If NO valid product found after {MAX_SCROLL_ATTEMPTS} scrolls:
  - FAIL with error message
  - DO NOT keep scrolling indefinitely

==================================================
STEP 6 — VERIFY PRODUCT PAGE
==================================================

You should now be on the product detail page (/dp/ URL).

VERIFY:
- URL contains /dp/ or /gp/aw/d/
- NOT sponsored (no sponsored labels)
- Meets hard constraints (price, rating match extracted data)
{"- Matches product attributes" if not generic_mode else ""}

If verification fails:
  - Go BACK to search results
  - Try NEXT extracted product (don't scroll yet)
  
If verification passes:
  - Proceed to STEP 7

==================================================
STEP 7 — ADD TO CART (ONCE)
==================================================

- Click "Add to Cart" ONCE
- Wait 4–5 seconds
- Close warranty/protection plan popups if shown (click "No thanks" or close)
- DO NOT click "Proceed to Buy" or "Go to Cart"

🚫 ADD TO CART FIREWALL
- NEVER click "Add to Cart" on search/results pages
- ONLY add to cart on product detail page (/dp/ or /gp/aw/d/)
- If cart count increases before product page → FAIL

==================================================
STEP 8 — VERIFY & FINISH
==================================================

VERIFY SUCCESS by checking ANY of:
1. "Added to Cart" confirmation message appears
2. Cart icon shows count increased (e.g., "1" badge on cart)
3. "Go to Cart" button visible
4. Can see "Subtotal" or cart summary

If ANY verification succeeds:
- Extract final product details (name, price, rating, URL)
- Use DONE action
- Return CartResult JSON with the product

IMPORTANT - DO NOT:
❌ Click "Proceed to Buy" or "Proceed to Checkout"
❌ Try to complete purchase
❌ Fill in any forms or sign-in pages
❌ Navigate to checkout/payment pages

If sign-in page appears:
- Task is ALREADY COMPLETE (item was added to cart)
- Don't try to sign in
- Just return the CartResult

FINAL RULE:
- After adding to cart successfully → DONE immediately
- After DONE → STOP (no retries, no additional actions)
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