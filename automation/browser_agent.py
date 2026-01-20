from browser_use import Agent, Browser, ChatOpenAI
from automation.models import CartResult, ProductIntent
from dotenv import load_dotenv 

load_dotenv()

def build_task(intent:ProductIntent)->CartResult:
    filters = []
    if intent.max_price:
        filters.append(f"price ≤ {intent.max_price}")
    if intent.min_rating:
        filters.append(f"rating ≥ {intent.min_rating}")
    if intent.min_price:
        filters.append(f"price ≥ {intent.min_price}")
    if intent.max_rating:
        filters.append(f"rating ≤ {intent.max_rating}")
    
    # Build search query - include brand if specified for better results
    search_query = intent.product
    if intent.brand:
        search_query = f"{intent.brand} {intent.product}"
    
    # Build filter instructions
    price_filter_instruction = ""
    if intent.min_price and intent.max_price:
        price_filter_instruction = f"Apply price filter: ₹{intent.min_price} - ₹{intent.max_price}"
    elif intent.max_price:
        price_filter_instruction = f"Apply price filter: Under ₹{intent.max_price}"
    elif intent.min_price:
        price_filter_instruction = f"Apply price filter: Over ₹{intent.min_price}"
    
    rating_filter_instruction = ""
    if intent.min_rating:
        rating_filter_instruction = f"Apply rating filter: {intent.min_rating} stars and above"
    
    # Handle sort preferences - Amazon sort dropdown options
    sort_dropdown_option = {
        "price_asc": "Price: Low to High",
        "price_desc": "Price: High to Low",
        "rating_desc": "Avg. Customer Review",
        "rating_asc": "Price: Low to High"  # Fallback, Amazon doesn't have low rating sort
    }.get(intent.sort_by, "Featured")  # Default/relevance

    # Only enforce non-sponsored filter if user has specific requirements
    has_filters = bool(intent.max_price or intent.min_price or intent.min_rating or intent.max_rating or intent.sort_by)
    sponsored_rule = "ABSOLUTE RULE: Never select products marked as 'Sponsored' - humans skip these too." if has_filters else "Preference: Try to select non-sponsored products when available, but sponsored products are acceptable if they match the requirements."
    
    return f"""
You are shopping on Amazon like a human would. Behave naturally and interact with the page as a person would.

{sponsored_rule}

==================================================
CRITICAL WORKFLOW ORDER (MUST FOLLOW THIS SEQUENCE)
==================================================
1. SEARCH FIRST - Complete search before anything else
2. APPLY FILTERS - Apply all required filters (sort, price, rating) if they exist
3. THEN PICK PRODUCTS - Only after filters are applied, browse and pick products
4. NAVIGATE TO PRODUCT PAGE - Use the complete product URL
5. ADD TO CART - One time only, on the product page

DO NOT skip steps or change the order!

==================================================
HUMAN-LIKE SHOPPING PROCESS
==================================================

STEP 1: SEARCH FIRST (Mandatory - Do This First!)
   - Go to https://www.amazon.in
   - Wait for page to load completely (wait 3-5 seconds)
   - If page seems unresponsive, wait a bit longer (5-8 seconds)
   - Find the search box at the top
   {"- Type \"" + search_query + "\" in the search box (includes brand for better results)" if intent.brand else "- Type \"" + search_query + "\" naturally in the search box"}
   - Press Enter or click search button
   - Wait for search results to load (URL should change to /s?k=)
   - Wait additional 3-5 seconds for page to stabilize and elements to load
   - CRITICAL: Complete search first before doing anything else

STEP 2: APPLY FILTERS (If Required - Do This Before Product Picking)
   - After search results load, wait 3-5 seconds for page to stabilize
   - If page seems unresponsive, wait a bit longer (5-8 seconds)
   - Make sure page elements are loaded before trying to interact
   - Check what filters are needed:
     {"* Price filter: " + price_filter_instruction if price_filter_instruction else ""}
     {"* Rating filter: " + rating_filter_instruction if rating_filter_instruction else ""}
     {"* Sort: " + sort_dropdown_option if intent.sort_by else ""}
   
   {"APPLY SORT (If Required):" if intent.sort_by else ""}
   {"- Wait for page to be loaded and stable (3-5 seconds)" if intent.sort_by else ""}
   {"- Look for the 'Sort by' dropdown (usually top-right of results)" if intent.sort_by else ""}
   {"- Click it ONCE to open the menu" if intent.sort_by else ""}
   {"- Wait 1-2 seconds for menu to appear" if intent.sort_by else ""}
   {"- Select '" + sort_dropdown_option + "' from the opened menu" if intent.sort_by else ""}
   {"- Wait 3-5 seconds for results to reorder" if intent.sort_by else ""}
   {"- If sort doesn't work after 2 attempts, skip it - not critical" if intent.sort_by else ""}

   {"APPLY PRICE FILTER (If Required):" if price_filter_instruction else ""}
   {"- Wait for page to be loaded and stable (3-5 seconds)" if price_filter_instruction else ""}
   {"- Look at the LEFT SIDEBAR for the 'Price' filter section" if price_filter_instruction else ""}
   {"- You want products " + price_filter_instruction.lower() if price_filter_instruction else ""}
   {"- In the Price section, you'll see clickable price range options like:" if price_filter_instruction else ""}
   {"  * 'Up to ₹200'" if price_filter_instruction else ""}
   {"  * '₹200 - ₹300'" if price_filter_instruction else ""}
   {"  * '₹300 - ₹450'" if price_filter_instruction else ""}
   {"  * etc." if price_filter_instruction else ""}
   {"- Use find_text or extract to locate the price filter options" if price_filter_instruction else ""}
   {"- Click on the price range option that matches your requirement" if price_filter_instruction else ""}
   {"- For example, if you want 'Under ₹99', click 'Up to ₹200' (closest match)" if price_filter_instruction else ""}
   {"- Wait 3-5 seconds for the filtered results to load" if price_filter_instruction else ""}
   {"- The page will refresh showing only products in that price range" if price_filter_instruction else ""}
   {"- If price filter click fails (element not available), wait 2-3 seconds, then try using find_text to locate it first" if price_filter_instruction else ""}
   {"- If still fails after 2 attempts, skip price filter and filter manually during product selection" if price_filter_instruction else ""}
   {"- IMPORTANT: Use the sidebar price filter - it's the easiest way to filter by price" if price_filter_instruction else ""}
   
   {"APPLY RATING FILTER (If Required):" if rating_filter_instruction else ""}
   {"- Wait for page to be loaded (3-5 seconds)" if rating_filter_instruction else ""}
   {"- Look for 'Avg. Customer Review' or 'Customer Rating' in left sidebar" if rating_filter_instruction else ""}
   {"- Use find_text to locate the rating filter if needed" if rating_filter_instruction else ""}
   {"- Click on '" + str(intent.min_rating) + " Stars & Up' if you see it" if rating_filter_instruction else ""}
   {"- Wait 3-5 seconds for results to update" if rating_filter_instruction else ""}
   {"- If rating filter fails after 2 attempts, skip it" if rating_filter_instruction else ""}
   
   - CRITICAL: If any filter fails due to page unresponsiveness or element not available:
     * Wait 3-5 seconds for page to stabilize
     * Use find_text to locate the filter element first
     * Try the filter again (maximum 2 attempts per filter)
     * If element index is not available, use find_text then click
     * If still fails after 2 attempts, skip that filter and proceed to product selection
   - Browser state recovery: If you see "element not available" or "page may have changed":
     * Wait 3-5 seconds for page to stabilize
     * Use find_text to locate elements instead of relying on element indices
     * Try again with find_text approach
   - Remember: Filters are helpful but optional - if they're hard to use, skip them and filter manually during product selection

STEP 3: BROWSE FILTERED PRODUCTS (Only After Filters Applied)
   - CRITICAL: Only start browsing/picking products AFTER all filters are applied
   - Wait for all filters to finish loading (page should refresh)
   - Wait additional 2-3 seconds for filtered results to load
   - Make sure products are visible before extracting
   - Now you can browse the filtered results
   - Scroll through the results naturally
   - Extract information about 30-40 products with COMPLETE details:
     * Product name (full name including brand/color/variant if mentioned)
     * Brand (extract brand from product name or brand field)
     * Color/variant (extract color from product name or description)
     * Price (as a number, extract numeric value)
     * Rating (as a number, extract star rating)
     * COMPLETE product URL (full URL starting with https://www.amazon.in)
     {"* Sponsored status (identify if sponsored,always prefer non-sponsored)" if has_filters else ""}
   - IMPORTANT: When extracting, ask specifically for:
     {"* Prefer non-sponsored products/organic results when possible" if has_filters else ""}
     * "complete product URLs" (full URLs, not partial)
     * "exact prices as numbers"
     * "exact ratings as numbers"
     {"* product brands (if user wants a specific brand, extract brand for each product)" if intent.brand else ""}
     {"* product colors/variants (if user wants a specific color, extract color for each product)" if intent.color else ""}
   {"- Pay attention: Sponsored products have labels/badges - prefer non-sponsored when available"}
   - CRITICAL: Extract the COMPLETE URL for each product - it should look like:
     * https://www.amazon.in/dp/B0XXXXXXX/ or
     * https://www.amazon.in/gp/product/B0XXXXXXX/
   {"- If extraction only shows sponsored products:" if has_filters else ""}
     {"* Scroll down significantly (2-3 full page scrolls)" if has_filters else ""}
     {"* Extract again, specifically requesting non-sponsored products with complete URLs" if has_filters else ""}
     {"* Look for products that don't have 'Sponsored' labels" if has_filters else ""}
   - Keep scrolling if needed to see more options
   {"- Humans scroll past sponsored ads to find real results" if has_filters else "- Look at all available products, sponsored or not"}
   {"- Usually unsponsored products appear after scrolling past the first few sponsored ones" if has_filters else ""}

STEP 4: CHOOSE THE BEST PRODUCT (Match Exact User Intent)
   - You MUST find a product that meets ALL these EXACT requirements:
     {"✓ Prefer NOT sponsored"}
     ✓ Product name matches or closely matches: "{intent.product}" - MANDATORY
     {"✓ Brand MUST match: " + intent.brand.lower() + " (check product name/brand field for brand)" if intent.brand else ""}
     {"✓ Color MUST match: " + intent.color.lower() + " (check product name/description for color)" if intent.color else ""}
     {"✓ Price MUST be ≤ ₹" + str(intent.max_price) if intent.max_price else ""}
     {"✓ Price MUST be ≥ ₹" + str(intent.min_price) if intent.min_price else ""}
     {"✓ Rating MUST be ≥ " + str(intent.min_rating) + " stars" if intent.min_rating else ""}
   - Extract product information carefully and verify each requirement
   - For each product, check:
     * Full product name (must include brand if brand is required, color if color is required)
     * Brand (if brand is specified, product name/brand field must contain that brand)
     * Color/variant (if color is specified, product name/description must contain that color)
     * Exact price (as a number, not text)
     * Exact rating (as a number)
     * Complete product URL (must be full URL starting with https://www.amazon.in)
     {"* Sponsored status (prefer NOT sponsored)" if has_filters else ""}
   - CRITICAL: The product URL must be the COMPLETE URL, like:
     * https://www.amazon.in/dp/B0XXXXXXX/ or
     * https://www.amazon.in/gp/product/B0XXXXXXX/
   - Pick the FIRST product that meets ALL criteria exactly
   - If no product meets ALL criteria:
     * Scroll down more to see additional products
     * Extract 20 more products with complete URLs
     * Try again (maximum 2 additional attempts)
   - Once you find a matching product, note its COMPLETE URL - you'll need this exact URL

STEP 5: NAVIGATE TO PRODUCT PAGE (CRITICAL - Use Exact URL)
   - DO NOT click "Add to Cart" from the search results page
   - You MUST navigate to the product's detail page first using the EXACT URL
   - Use the COMPLETE product URL you extracted in Step 6
   - The URL should be like: https://www.amazon.in/dp/B0XXXXXXX/ or https://www.amazon.in/gp/product/B0XXXXXXX/
   - Navigate to that EXACT URL (use navigate action with the full product URL)
   - Wait for the product detail page to load (wait 3-5 seconds)
   - If page seems slow, wait a bit longer (5-8 seconds)
   - Verify you're on the correct product page:
     * URL should show /dp/ or /gp/product/
     * Product name should match what you selected
     * Price should match your requirements
   - If URL doesn't work or page doesn't load, extract the URL again from search results
   - This is how humans shop - they click on a product to see details first
   

STEP 6: VERIFY PRODUCT MATCHES EXACT INTENT (On Product Page)
   - Now that you're on the product page, verify it matches EXACTLY:
     * Product name matches: "{intent.product}"
     {"* Brand matches: " + intent.brand.lower() + " (check product name, brand field, or description)" if intent.brand else ""}
     {"* Color matches: " + intent.color.lower() + " (check product name, description, or color options)" if intent.color else ""}
     {"- If color doesn't match but color options are available:" if intent.color else ""}
     {"  * Look for color selection buttons/dropdowns on the product page" if intent.color else ""}
     {"  * Click on the color option that matches: " + intent.color.lower() if intent.color else ""}
     {"  * Wait 3-5 seconds for page to update with selected color" if intent.color else ""}
     {"  * Verify the selected color matches your requirement" if intent.color else ""}
     {"  * If color option not available, this product doesn't match - return error" if intent.color else ""}
     {"* Price is ≤ ₹" + str(intent.max_price) if intent.max_price else ""}
     {"* Price is ≥ ₹" + str(intent.min_price) if intent.min_price else ""}
     {"* Rating is ≥ " + str(intent.min_rating) + " stars" if intent.min_rating else ""}
     {"* Product is NOT sponsored (preferred)" if has_filters else ""}
   - Extract the exact details:
     * Product name (full name including color if selected)
     * Color/variant (verify it matches requirement)
     * Price (as a number, extract the numeric value)
     * Rating (as a number, extract the star rating)
     * Brand (if available)
     * Size/quantity if shown
     * Current page URL (this is the final URL to return - must be complete)
   - CRITICAL: Verify the current page URL is the complete product URL (https://www.amazon.in/dp/... or /gp/product/...)
   - If product doesn't match requirements (especially color), return error - don't add to cart
   - Only proceed if ALL requirements are met exactly, including color if specified

STEP 7: ADD TO CART (ONE TIME ONLY - On Product Page)
   - Make sure product page is loaded (wait 3-5 seconds if needed)
   - Check for any popups or overlays (warranty offers, deals, etc.) - dismiss them if they block the "Add to Cart" button
   - Find the "Add to Cart" button on THIS product page (main product, not warranty/add-on buttons)
   - The "Add to Cart" button should be for the main product, not for extended warranties or add-ons
   - Click it ONCE and ONLY ONCE (like a human would)
   - Wait 3-5 seconds for the page to respond and update
   - After clicking, if a popup appears (warranty offer, etc.):
     * Click "No thanks" or close the popup (X button)
     * Wait 1-2 seconds
     * The product is likely already added - check for success indicators
   - DO NOT click "Add to Cart" buttons from search results - those are shortcuts that don't work well
   - CRITICAL: You get ONE attempt to add to cart - do not retry

STEP 8: CONFIRM IT WORKED & RETURN RESULT (Final Step)
   - After clicking "Add to Cart", wait 3-5 seconds for page to update
   - Dismiss any popups/overlays that appear (warranty offers, deals, etc.) - click "No thanks" or close (X)
   - Look for signs it worked (check MULTIPLE indicators):
     * "Added to cart" message or confirmation text
     * Cart icon (top right) shows item count increased (e.g., "Cart (1)")
     * "Proceed to Buy" or "Go to Cart" button appears
     * Page might change to show confirmation
     * The "Add to Cart" button might disappear or change to "Added" or "Go to Cart"
     * URL might change to include /cart/ or /gp/cart/
     * Success message like "Added to Cart" or "Item added to your cart"
   - CRITICAL: If you see ANY popup/error after clicking "Add to Cart":
     * It might be a warranty offer or add-on popup, NOT an error
     * Dismiss the popup and check for success indicators
     * The product might already be in the cart even if a popup appeared
     * Check the cart icon count - if it increased, it's SUCCESS
   - If you see ANY of the success signs above, it worked! Proceed to return result
   - If you don't see clear success indicators:
     * Extract the page content to check what happened
     * Look specifically for cart icon count increase
     * Check if URL changed to /cart/ or /gp/cart/
     * If cart icon shows items or count increased, it's SUCCESS even if no message
     * Only return error if cart icon count did NOT increase AND no success indicators found
   - DO NOT click "Add to Cart" again - that would add duplicate items
   - DO NOT navigate back to search results to try another product
   - ONE attempt only - accept the result
   
   - IMMEDIATELY after confirming cart addition, use the "done" action to return the result
   - Return the EXACT product information in CartResult format:
     * Product name (exact name from product page)
     * Price (exact numeric price as number, not text - remove ₹ symbol)
     * Rating (exact numeric rating if available)
     * URL (the COMPLETE product URL you navigated to - must be full URL)
   - The URL must be the complete Amazon product URL, like:
     * https://www.amazon.in/dp/B0XXXXXXX/ or
     * https://www.amazon.in/gp/product/B0XXXXXXX/
   - Use the "done" action with the structured CartResult JSON format
   - Format example:
     {{
       "items": [
         {{
           "name": "exact product name from product page",
           "price": 99.0,
           "rating": 4.4,
           "url": "https://www.amazon.in/dp/B0XXXXXXX/"
         }}
       ]
     }}
   - Price must be a NUMBER (remove ₹ symbol, convert "₹99.00" to 99.0)
   - Rating must be a NUMBER (extract numeric value, "4.4 stars" becomes 4.4)
   - URL must be COMPLETE (full URL starting with https://www.amazon.in)
   - CRITICAL: Use "done" action - DO NOT write files
   - The "done" action will display the result in the UI automatically
   - After using "done" action, STOP immediately - task is complete
   - DO NOT perform any additional steps after "done" action
   - DO NOT write files - the "done" action handles displaying results

==================================================
HUMAN-LIKE BEHAVIOR TIPS
==================================================

- Browse naturally: Look around, scroll, take in what you see
- Use filters when they're easy: Click price/rating filters if visible and clickable
- Skip complicated things: If a filter is a slider or hard to use, skip it
{"- Scroll past ads: Sponsored products are like ads - prefer non-sponsored when available"}
- Make decisions: Pick the best product from what you see, like a human would
- CRITICAL: Always navigate to product page first - NEVER click "Add to Cart" from search results
- Navigate then add: Click on product → Go to product page → Then add to cart
- ONE TIME ADD ONLY: Click "Add to Cart" exactly ONCE - never retry
- If add to cart fails, return error - DO NOT navigate back to try another product
- DO NOT retry adding to cart - one attempt only
- Be patient: Wait 3-5 seconds after clicking before checking for success
- Trust your eyes: Use visual understanding to see what's on the page
- Stop loops: If extraction fails 3 times, pick the best available product and proceed
- USE DONE ACTION: After confirming cart addition, use "done" action immediately with CartResult format
- DO NOT write files - the "done" action returns the result to the UI
- STOP after "done" action - task is complete, no further steps needed

Remember: Act like a human shopping online - natural, thoughtful, and efficient.
Humans click on products to see details before adding to cart - you should too!
After adding to cart, return the result using "done" action and stop.
"""

    
async def run_browser_agent(intent:ProductIntent)->CartResult:
    # Use vision-capable model for better page understanding via screenshots
    # gpt-4o or gpt-4o-mini with vision support can see page screenshots
    agent = Agent(
        browser=Browser(),
        llm=ChatOpenAI(model="gpt-4o-mini"),  # gpt-4o-mini supports vision
        task=build_task(intent),
        output_model_schema=CartResult,
        max_steps=30
    )
    return await agent.run()
    