import streamlit as st

st.title("Page Replacement Simulator")

frames = st.number_input("Number of Frames", 1, 10, 3)
pages_input = st.text_input("Reference String", "7,0,1,2,0,3,0,4")

def fifo(pages, capacity):
    memory = []
    queue = []
    faults = 0

    for page in pages:
        if page not in memory:
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
                queue.append(page)
            else:
                removed = queue.pop(0)
                index = memory.index(removed)
                memory[index] = page
                queue.append(page)
    return faults

if st.button("Run FIFO"):
    pages = list(map(int, pages_input.split(",")))
    faults = fifo(pages, frames)
    st.success(f"Total Page Faults: {faults}")