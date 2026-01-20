# """
# Test file for Amazon Cart Automation
# Tests multiple queries with different combinations of filters
# """

# import asyncio
# import sys
# from automation.intent_parser import parse_intent
# from automation.browser_agent import run_browser_agent
# from automation.models import ProductIntent

# # Test cases with different query types
# TEST_CASES = [
#     {
#         "name": "Simple product query",
#         "query": "add pen",
#         "expected": {
#             "product": "pen",
#             "brand": None,
#             "color": None,
#             "max_price": None,
#             "min_price": None,
#             "min_rating": None,
#             "sort_by": None
#         }
#     },
#     {
#         "name": "Product with price constraint",
#         "query": "add pen with price less than 20 rs",
#         "expected": {
#             "product": "pen",
#             "brand": None,
#             "color": None,
#             "max_price": 20.0,
#             "min_price": None,
#             "min_rating": None,
#             "sort_by": None
#         }
#     },
#     {
#         "name": "Product with rating constraint",
#         "query": "add pen with more user rating",
#         "expected": {
#             "product": "pen",
#             "brand": None,
#             "color": None,
#             "max_price": None,
#             "min_price": None,
#             "min_rating": 4.0,
#             "sort_by": "rating_desc"
#         }
#     },
#     {
#         "name": "Product with brand",
#         "query": "add prestige cooker 3 ltr",
#         "expected": {
#             "product": "cooker",
#             "brand": "prestige",
#             "color": None,
#             "max_price": None,
#             "min_price": None,
#             "min_rating": None,
#             "sort_by": None
#         }
#     },
#     {
#         "name": "Product with brand and color",
#         "query": "add boAt Airdopes 141",
#         "expected": {
#             "product": "Airdopes 141",
#             "brand": "boAt",
#             "color": None,
#             "max_price": None,
#             "min_price": None,
#             "min_rating": None,
#             "sort_by": None
#         }
#     },
#     {
#         "name": "Product with color",
#         "query": "add Oneplus 15r in black",
#         "expected": {
#             "product": "15r",
#             "brand": "oneplus",
#             "color": "black",
#             "max_price": None,
#             "min_price": None,
#             "min_rating": None,
#             "sort_by": None
#         }
#     },
#     {
#         "name": "Product with price and rating",
#         "query": "add laptop under 50000 with good rating",
#         "expected": {
#             "product": "laptop",
#             "brand": None,
#             "color": None,
#             "max_price": 50000.0,
#             "min_price": None,
#             "min_rating": 4.0,
#             "sort_by": None
#         }
#     },
#     {
#         "name": "Cheapest product",
#         "query": "add cheapest phone",
#         "expected": {
#             "product": "phone",
#             "brand": None,
#             "color": None,
#             "max_price": None,
#             "min_price": None,
#             "min_rating": None,
#             "sort_by": "price_asc"
#         }
#     },
#     {
#         "name": "Best rated product",
#         "query": "add best rated pen",
#         "expected": {
#             "product": "pen",
#             "brand": None,
#             "color": None,
#             "max_price": None,
#             "min_price": None,
#             "min_rating": None,
#             "sort_by": "rating_desc"
#         }
#     },
#     {
#         "name": "Product with brand, color, and price",
#         "query": "add samsung phone in black under 30000",
#         "expected": {
#             "product": "phone",
#             "brand": "samsung",
#             "color": "black",
#             "max_price": 30000.0,
#             "min_price": None,
#             "min_rating": None,
#             "sort_by": None
#         }
#     },
#     {
#         "name": "Product with brand and color (Charcoal Black)",
#         "query": "add Oneplus 15r with Charcoal Black color",
#         "expected": {
#             "product": "15r",
#             "brand": "oneplus",
#             "color": "charcoal black",
#             "max_price": None,
#             "min_price": None,
#             "min_rating": None,
#             "sort_by": None
#         }
#     },
#     {
#         "name": "Product with price range",
#         "query": "add pen between 10 and 50 rs",
#         "expected": {
#             "product": "pen",
#             "brand": None,
#             "color": None,
#             "max_price": 50.0,
#             "min_price": 10.0,
#             "min_rating": None,
#             "sort_by": None
#         }
#     }
# ]

# def test_intent_parser():
#     """Test the intent parser with various queries"""
#     print("=" * 80)
#     print("TESTING INTENT PARSER")
#     print("=" * 80)
    
#     passed = 0
#     failed = 0
    
#     for i, test_case in enumerate(TEST_CASES, 1):
#         print(f"\n[{i}/{len(TEST_CASES)}] Testing: {test_case['name']}")
#         print(f"Query: '{test_case['query']}'")
        
#         try:
#             intent = parse_intent(test_case['query'])
#             expected = test_case['expected']
            
#             # Check each field
#             errors = []
#             if intent.product.lower() != expected['product'].lower():
#                 errors.append(f"Product: expected '{expected['product']}', got '{intent.product}'")
            
#             if expected['brand']:
#                 if not intent.brand or intent.brand.lower() != expected['brand'].lower():
#                     errors.append(f"Brand: expected '{expected['brand']}', got '{intent.brand}'")
#             elif intent.brand:
#                 errors.append(f"Brand: expected None, got '{intent.brand}'")
            
#             if expected['color']:
#                 if not intent.color or intent.color.lower() != expected['color'].lower():
#                     errors.append(f"Color: expected '{expected['color']}', got '{intent.color}'")
#             elif intent.color:
#                 errors.append(f"Color: expected None, got '{intent.color}'")
            
#             if expected['max_price']:
#                 if intent.max_price != expected['max_price']:
#                     errors.append(f"Max Price: expected {expected['max_price']}, got {intent.max_price}")
#             elif intent.max_price:
#                 errors.append(f"Max Price: expected None, got {intent.max_price}")
            
#             if expected['min_price']:
#                 if intent.min_price != expected['min_price']:
#                     errors.append(f"Min Price: expected {expected['min_price']}, got {intent.min_price}")
#             elif intent.min_price:
#                 errors.append(f"Min Price: expected None, got {intent.min_price}")
            
#             if expected['min_rating']:
#                 if intent.min_rating != expected['min_rating']:
#                     errors.append(f"Min Rating: expected {expected['min_rating']}, got {intent.min_rating}")
#             elif intent.min_rating:
#                 errors.append(f"Min Rating: expected None, got {intent.min_rating}")
            
#             if expected['sort_by']:
#                 if intent.sort_by != expected['sort_by']:
#                     errors.append(f"Sort By: expected '{expected['sort_by']}', got '{intent.sort_by}'")
#             elif intent.sort_by:
#                 errors.append(f"Sort By: expected None, got '{intent.sort_by}'")
            
#             if errors:
#                 print(f"❌ FAILED")
#                 for error in errors:
#                     print(f"   - {error}")
#                 failed += 1
#             else:
#                 print(f"✅ PASSED")
#                 print(f"   Product: {intent.product}")
#                 if intent.brand:
#                     print(f"   Brand: {intent.brand}")
#                 if intent.color:
#                     print(f"   Color: {intent.color}")
#                 if intent.max_price:
#                     print(f"   Max Price: ₹{intent.max_price}")
#                 if intent.min_price:
#                     print(f"   Min Price: ₹{intent.min_price}")
#                 if intent.min_rating:
#                     print(f"   Min Rating: {intent.min_rating} stars")
#                 if intent.sort_by:
#                     print(f"   Sort By: {intent.sort_by}")
#                 passed += 1
                
#         except Exception as e:
#             print(f"❌ FAILED with exception: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             failed += 1
    
#     print("\n" + "=" * 80)
#     print(f"INTENT PARSER TEST RESULTS: {passed} passed, {failed} failed out of {len(TEST_CASES)} tests")
#     print("=" * 80)
    
#     return passed, failed

# async def test_browser_agent(test_queries=None):
#     """Test the browser agent with actual automation (optional - takes time)"""
#     print("\n" + "=" * 80)
#     print("TESTING BROWSER AGENT (Full Automation)")
#     print("=" * 80)
#     print("⚠️  WARNING: This will run actual browser automation and may take several minutes per test")
#     print("=" * 80)
    
#     if test_queries is None:
#         # Use a subset of simpler queries for browser testing
#         test_queries = [
#             "add pen with price less than 20 rs",
#             "add prestige cooker",
#         ]
    
#     passed = 0
#     failed = 0
    
#     for i, query in enumerate(test_queries, 1):
#         print(f"\n[{i}/{len(test_queries)}] Testing browser automation")
#         print(f"Query: '{query}'")
        
#         try:
#             intent = parse_intent(query)
#             print(f"Parsed intent: {intent.product}")
#             if intent.brand:
#                 print(f"  Brand: {intent.brand}")
#             if intent.color:
#                 print(f"  Color: {intent.color}")
#             if intent.max_price:
#                 print(f"  Max Price: ₹{intent.max_price}")
            
#             print("Running browser agent... (this may take 2-5 minutes)")
#             result = await run_browser_agent(intent)
            
#             if result and hasattr(result, 'items') and len(result.items) > 0:
#                 print(f"✅ PASSED - Item added to cart")
#                 item = result.items[0]
#                 print(f"   Product: {item.name}")
#                 print(f"   Price: ₹{item.price}")
#                 print(f"   Rating: {item.rating}")
#                 print(f"   URL: {item.url}")
#                 passed += 1
#             else:
#                 print(f"❌ FAILED - No items returned")
#                 failed += 1
                
#         except Exception as e:
#             print(f"❌ FAILED with exception: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             failed += 1
    
#     print("\n" + "=" * 80)
#     print(f"BROWSER AGENT TEST RESULTS: {passed} passed, {failed} failed out of {len(test_queries)} tests")
#     print("=" * 80)
    
#     return passed, failed

# def main():
#     """Main test function"""
#     print("\n" + "=" * 80)
#     print("AMAZON CART AUTOMATION - TEST SUITE")
#     print("=" * 80)
    
#     # Test intent parser
#     parser_passed, parser_failed = test_intent_parser()
    
#     # Ask user if they want to run browser automation tests
#     print("\n" + "=" * 80)
#     print("BROWSER AUTOMATION TESTS")
#     print("=" * 80)
#     print("Browser automation tests will run actual automation and take time.")
#     print("Do you want to run browser automation tests? (y/n): ", end="")
    
#     # For automated testing, you can set this to False
#     run_browser_tests = True
    
#     if run_browser_tests:
#         try:
#             browser_passed, browser_failed = asyncio.run(test_browser_agent())
#         except KeyboardInterrupt:
#             print("\n\nBrowser tests interrupted by user")
#             browser_passed, browser_failed = 0, 0
#     else:
#         print("Skipping browser automation tests (set run_browser_tests=True to enable)")
#         browser_passed, browser_failed = 0, 0
    
#     # Summary
#     print("\n" + "=" * 80)
#     print("TEST SUMMARY")
#     print("=" * 80)
#     print(f"Intent Parser: {parser_passed} passed, {parser_failed} failed")
#     if run_browser_tests:
#         print(f"Browser Agent: {browser_passed} passed, {browser_failed} failed")
#     total_passed = parser_passed + browser_passed
#     total_failed = parser_failed + browser_failed
#     total_tests = len(TEST_CASES) + (browser_passed + browser_failed if run_browser_tests else 0)
#     print(f"\nTotal: {total_passed} passed, {total_failed} failed out of {total_tests} tests")
#     print("=" * 80)
    
#     # Exit with error code if any tests failed
#     if total_failed > 0:
#         sys.exit(1)
#     else:
#         sys.exit(0)

# if __name__ == "__main__":
#     main()
