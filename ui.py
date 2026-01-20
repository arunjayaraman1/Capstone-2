import streamlit as st
import requests

API_URL = "http://localhost:8000/query"

st.title("Amazon Cart Automation")


query = st.text_input(
    "Enter your shopping query",
    placeholder="add pen below 100 rs with good rating"
)

if st.button("Add to Cart"):
    if not query:
        st.error("please enter a query")
    else:
        try:
            res = requests.post(API_URL,json={"query":query},timeout=600)  # 10 minutes timeout for browser automation
            res.raise_for_status()  # Raise an exception for bad status codes
            data = res.json()

            if data.get("success"):
                st.success("Item added to cart!")
                if "cart" in data and "items" in data["cart"]:
                    for item in data["cart"]["items"]:
                        st.markdown(f"🔗 [{item['name']}]({item['url']})")
            else:
                error_msg = data.get("error", "Automation failed")
                st.error(f"Automation failed: {error_msg}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
        except KeyError as e:
            st.error(f"Unexpected response format: missing key {e}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")