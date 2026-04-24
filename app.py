import streamlit as st

st.title("Page Replacement Algorithm")

pages_input = st.text_input("Enter pages (comma separated):")
frames = st.number_input("Enter number of frames", min_value=1)

if st.button("Run"):
    if pages_input:
        try:
            pages = list(map(int, pages_input.split(",")))

            memory = []
            faults = 0

            for page in pages:
                if page not in memory:
                    faults += 1
                    if len(memory) < frames:
                        memory.append(page)
                    else:
                        memory.pop(0)
                        memory.append(page)

            st.success(f"Page Faults: {faults}")

        except:
            st.error("Invalid input")