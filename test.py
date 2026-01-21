# import asyncio
# from automation.intent_parser import parse_intent
# from automation.browser_agent import run_browser_agent
# from automation.models import ProductIntent, CartResult

# # ---------------------------------------------------------
# # TEST CASES
# # ---------------------------------------------------------

# TEST_CASES = [
#     {
#         "name": "Generic pen under 100",
#         "query": "Add a pen below 100 rs and 4 rating",
#         "expect_generic": True
#     },
#     {
#         "name": "Generic pen above 200",
#         "query": "Add a pen below 200 rs and 4 rating",
#         "expect_generic": True
#     },
#     {
#         "name": "Generic Oneplus15r",
#         "query": "add Oneplus15r Charcoal Black Color",
#         "expect_generic": True
#     },
#     {
#         "name": "Exact brand + color",
#         "query": "Add Oneplus 15r Charcoal black color",
#         "expect_generic": True
#     },
#     {
#         "name": "Exact cheap product",
#         "query": "Add pentonic pen for 99 rs",
#         "expect_generic": True
#     },
#     {
#         "name": "Laptop under budget",
#         "query": "Add a laptop under 50000 with good rating",
#         "expect_generic": True
#     },
#     {
#         "name": "Premium intent",
#         "query": "Add premium pen above 1000 rs",
#         "expect_generic": True
#     }
# ]

# # ---------------------------------------------------------
# # HELPERS
# # ---------------------------------------------------------

# def is_generic_intent(intent: ProductIntent) -> bool:
#     return (
#         not intent.brand
#         and not intent.color
#         and len(intent.product.split()) <= 2
#     )

# def print_intent(intent: ProductIntent):
#     print("Parsed Intent:")
#     print(f"  product      : {intent.product}")
#     print(f"  min_price    : {intent.min_price}")
#     print(f"  max_price    : {intent.max_price}")
#     print(f"  min_rating   : {intent.min_rating}")
#     print(f"  sort_by      : {intent.sort_by}")
#     print(f"  color        : {intent.color}")
#     print(f"  price_intent : {getattr(intent, 'price_intent', None)}")

# # ---------------------------------------------------------
# # MAIN TEST RUNNER
# # ---------------------------------------------------------

# async def run_test_case(test_case: dict):
#     print("\n" + "=" * 80)
#     print(f"TEST: {test_case['name']}")
#     print(f"QUERY: {test_case['query']}")
#     print("=" * 80)

#     # Step 1: Parse intent
#     intent = parse_intent(test_case["query"])
#     print_intent(intent)

#     # Step 2: Validate intent type
#     generic = is_generic_intent(intent)
#     expected = test_case["expect_generic"]

#     print(f"\nIntent mode detected : {'GENERIC' if generic else 'EXACT'}")
#     print(f"Expected intent mode : {'GENERIC' if expected else 'EXACT'}")

#     if generic != expected:
#         print("❌ Intent classification mismatch!")
#         return

#     print("✅ Intent classification OK")

#     # Step 3: Run browser agent
#     try:
#         print("\n🚀 Running browser agent...")
#         result: CartResult = await run_browser_agent(intent)

#         if not result.items:
#             print("⚠️ No items added to cart")
#             return

#         item = result.items[0]
#         print("\n✅ Item added to cart:")
#         print(f"  Name   : {item.name}")
#         print(f"  Price  : {item.price}")
#         print(f"  Rating : {item.rating}")
#         print(f"  URL    : {item.url}")

#     except Exception as e:
#         print("❌ Test failed with exception:")
#         print(str(e))

# # ---------------------------------------------------------
# # ENTRY POINT
# # ---------------------------------------------------------

# async def main():
#     print("\n🧪 STARTING MULTI-PRODUCT INTENT TEST SUITE")

#     for test_case in TEST_CASES:
#         await run_test_case(test_case)

#     print("\n✅ ALL TESTS COMPLETED")

# if __name__ == "__main__":
#     asyncio.run(main())

