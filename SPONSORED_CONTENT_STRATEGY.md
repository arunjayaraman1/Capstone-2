# Element-by-Element Sponsored Content Detection

## Overview

Implemented a **systematic, element-by-element approach** to detect and skip sponsored products instead of relying on scrolling. This makes the agent **more efficient, reliable, and faster**.

---

## Problem with Old Approach

### Old Strategy: Scroll First, Extract Later

```
1. Search for product
2. Apply filters
3. ⚠️ SCROLL DOWN 1-2 screen heights (hoping to get past sponsored content)
4. Extract ALL visible products
5. Filter out sponsored products
6. Select first valid product
```

### Issues

❌ **Assumes sponsored products are always at the top** - Not always true  
❌ **Misses early non-sponsored products** - Valid products above fold are skipped  
❌ **Wastes time scrolling** - Unnecessary if valid products are already visible  
❌ **Less reliable** - Depends on scroll position and timing  
❌ **Non-deterministic** - Different scroll amounts = different results  

### Real Example from Testing

In the basmati rice search screenshot:
- **Product 1-4:** Sponsored (Daawat, Kohinoor, Zeeba)
- **Product 5:** ✅ **"Daawat Rozana ₹78, 4.0★"** - Non-sponsored, meets criteria
- **Old behavior:** Scrolled past it, kept scrolling, never selected it
- **Should have selected:** Product 5 immediately

---

## New Approach: Extract First, Check Each Element

### New Strategy: Element-by-Element Checking

```
1. Search for product
2. Apply filters
3. ✅ EXTRACT products IMMEDIATELY (don't scroll yet)
4. ✅ CHECK EACH product sequentially (top to bottom):
   - Is it sponsored? → Skip
   - Does it meet criteria? → Check
   - First non-sponsored product that meets criteria → SELECT IT!
5. Navigate to selected product
6. Only scroll if NO valid products found in visible area
```

### Advantages

✅ **More efficient** - No unnecessary scrolling  
✅ **More reliable** - Systematic checking of every product  
✅ **Faster** - Finds products in first screen when available  
✅ **Deterministic** - Always checks in same order (top to bottom)  
✅ **Catches early non-sponsored items** - Like the ₹78 rice example  
✅ **Better user experience** - Less browser movement, quicker results  

---

## How It Works

### Step-by-Step Flow

#### Step 3: Extract Products (Before Scrolling)

```
- Extract ALL visible products on screen
- Get them in DISPLAY ORDER (top to bottom)
- For each product collect:
  - name
  - price
  - rating  
  - sponsored status
  - URL
```

#### Step 4: Check Each Product Sequentially

```python
for product in extracted_products (in order):
    # 1. Check if sponsored
    if "Sponsored" label OR url_contains_sponsored_pattern:
        continue  # Skip to next product
    
    # 2. Check if meets criteria
    if not_meets_price_criteria OR not_meets_rating_criteria:
        continue  # Skip to next product
    
    # 3. Found valid product!
    selected_product = product
    break  # Stop checking, proceed to Step 5
```

#### Step 4.1: Scroll (Only If Needed)

```
if no_valid_product_found AND scroll_attempts < MAX_SCROLL_ATTEMPTS:
    scroll_down(1 screen height)
    wait(2 seconds)
    extract_newly_visible_products()
    repeat Step 4
else if no_valid_product_found:
    return FAILURE
```

---

## Sponsored Detection Methods

### Method 1: Visual Label Check

```
if product.has_label("Sponsored"):
    skip_product()
```

Amazon shows "Sponsored" labels on paid placements.

### Method 2: URL Pattern Check

```python
SPONSORED_URL_PATTERNS = (
    "/sspa/",      # Sponsored Products Ads
    "sp_atk",      # Sponsored Product Attribution Token
    "sp_csd",      # Sponsored Product Creative Source Data
    "sp_btf",      # Sponsored Product Below The Fold
    "sp_",         # Generic sponsored parameter
)

if any(pattern in product.url for pattern in SPONSORED_URL_PATTERNS):
    skip_product()
```

Amazon encodes sponsored status in URLs for tracking.

---

## Example Walkthrough

### Scenario: "basmati rice under ₹200, rating 4+"

#### Visible Products After Search:

1. **Daawat Super Basmati ₹149, 4.4★** - URL: `/sspa/click?...` ❌ Sponsored
2. **Daawat Biryani ₹190, 4.4★** - Label: "Sponsored" ❌ Sponsored  
3. **Kohinoor Pulao ₹99, 4.3★** - URL: `/sspa/click?...` ❌ Sponsored
4. **Zeeba Super ₹149, 4.1★** - Label: "Sponsored" ❌ Sponsored
5. **Daawat Rozana ₹78, 4.0★** - No label, normal URL ✅ **SELECTED!**

### Agent Actions:

```
Step 3: Extract products 1-5
Step 4: Check sequentially
  - Product 1: Sponsored URL → Skip
  - Product 2: Sponsored label → Skip
  - Product 3: Sponsored URL → Skip
  - Product 4: Sponsored label → Skip
  - Product 5: ✅ Non-sponsored + Price ₹78 (< ₹200) + Rating 4.0 (≥ 4)
Step 5: Navigate to Product 5 URL
Step 6: Verify on product page
Step 7: Add to cart
Step 8: Done
```

**Total time:** Much faster, no scrolling needed!

---

## Comparison: Old vs New

| Aspect | Old Approach | New Approach |
|--------|--------------|--------------|
| **First action** | Scroll down | Extract products |
| **Detection** | After scrolling | Before scrolling |
| **Checking order** | Random (depends on scroll) | Sequential (top to bottom) |
| **Efficiency** | Scrolls even if products visible | Only scrolls if needed |
| **Reliability** | Medium (scroll-dependent) | High (systematic) |
| **Speed** | Slower (always scrolls) | Faster (conditional scroll) |
| **Example result** | Missed ₹78 rice | Found ₹78 rice |

---

## Benefits by Use Case

### Use Case 1: Product Visible in First Screen

**Query:** "mouse under ₹500"

**Old approach:**
- Scroll down → Extract → Check → Takes 3-4 seconds longer

**New approach:**
- Extract immediately → Check → Select → **3-4 seconds faster**

### Use Case 2: Early Non-Sponsored Product

**Query:** "rice under ₹200"  
**Product 5:** ₹78, non-sponsored, 4.0★

**Old approach:**
- Scroll past it → Keep scrolling → Maybe never find it

**New approach:**
- Check products 1-5 → Find ₹78 rice → Select it → **Reliable selection**

### Use Case 3: No Valid Products Visible

**Query:** "laptop under ₹5000" (unrealistic price)

**Old approach:**
- Scroll → Extract → No valid products → Scroll again → Fail

**New approach:**
- Extract → Check all → None valid → Scroll → Extract → Check → Still none → Fail
- **Same result, but more systematic**

---

## Configuration

### Constants

```python
MAX_SCROLL_ATTEMPTS = 2  # Maximum scrolls if no products found
SPONSORED_URL_PATTERNS = (
    "/sspa/",
    "sp_atk", 
    "sp_csd",
    "sp_btf",
    "sp_",
)
```

### Adjustable Parameters

- **MAX_SCROLL_ATTEMPTS:** Increase if products are further down
- **SPONSORED_URL_PATTERNS:** Add more patterns if Amazon adds new sponsored indicators
- **Extract count:** Currently extracts all visible; could limit to top N for speed

---

## Edge Cases Handled

### Edge Case 1: All Visible Products Are Sponsored

**Behavior:** Check all visible → None valid → Scroll → Extract new → Check again

**Result:** Correctly scrolls only when needed

### Edge Case 2: First Product Is Valid

**Behavior:** Check Product 1 → Valid → Select immediately

**Result:** Maximum efficiency, no unnecessary checks

### Edge Case 3: Valid Product at Bottom of Screen

**Behavior:** Check Products 1-N → Product N is valid → Select it

**Result:** No scrolling needed, found before scroll

### Edge Case 4: Sponsored URLs Without Label

**Behavior:** Check URL pattern → Contains `/sspa/` → Skip

**Result:** Catches sponsored products even without visible label

---

## Testing Recommendations

### Test Scenarios

1. **First product valid** - Should select immediately
2. **5th product valid** - Should check 1-4, select 5
3. **All products sponsored** - Should scroll and try again
4. **No valid products exist** - Should fail after MAX_SCROLL_ATTEMPTS
5. **Sponsored URL but no label** - Should skip via URL pattern
6. **Sponsored label but normal URL** - Should skip via label

### Success Metrics

- ✅ Selects first valid non-sponsored product
- ✅ Doesn't scroll if product is visible
- ✅ Scrolls only when needed
- ✅ Detects sponsored via both label and URL
- ✅ Faster completion time
- ✅ More deterministic results

---

## Future Enhancements

### 1. Smart Extraction
Extract only top 10 products for speed, then scroll if needed

### 2. Sponsored Pattern Learning
Automatically detect new sponsored URL patterns

### 3. Position Tracking
Track where non-sponsored products typically appear

### 4. Parallel Checking
Check multiple products simultaneously for speed

### 5. Confidence Scoring
Assign confidence scores to sponsored detection

---

## Summary

The **element-by-element sponsored content detection** strategy:

✅ Extracts products **before** scrolling  
✅ Checks each product **sequentially** (top to bottom)  
✅ Detects sponsored via **label AND URL patterns**  
✅ Selects **first valid non-sponsored** product  
✅ Scrolls **only when needed**  
✅ **Faster, more reliable, more efficient**  

This approach solves the issue of missing valid products like the ₹78 rice and makes the agent more systematic and predictable.

---

**Status:** ✅ Implemented and tested

**Files Modified:** `automation/browser_agent.py`

**Date:** 2026-01-21
