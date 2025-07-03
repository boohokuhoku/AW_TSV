import streamlit as st
import re

# Function to process AW IDs
def get_unique_aw_ids(aw_ids_input):
    # Split input by commas or newlines, strip whitespace, and filter out empty strings
    aw_ids = [id.strip() for id in aw_ids_input.replace('\n', ',').split(',') if id.strip()]
    # Remove duplicates while preserving order
    unique_aw_ids = list(dict.fromkeys(aw_ids))
    return unique_aw_ids

# Function to generate short URLs from artwork names
def generate_short_urls(artwork_names_input):
    # Split input by newlines, strip whitespace, and filter out empty strings
    artwork_names = [name.strip() for name in artwork_names_input.split('\n') if name.strip()]
    short_urls = []
    name_count = {}
    
    for name in artwork_names:
        # Convert to lowercase, replace special characters with spaces, and split
        clean_name = re.sub(r'[^\w\s]', ' ', name.lower()).strip()
        # Replace multiple spaces with single space and then replace spaces with hyphens
        slug = '-'.join(clean_name.split())
        
        # Handle duplicates
        if slug in name_count:
            name_count[slug] += 1
            short_urls.append(f"{slug}-atwgp{name_count[slug]}")
        else:
            name_count[slug] = 1
            short_urls.append(slug)
    
    return short_urls

# Streamlit app layout
st.title("Artwork ID and URL Generator")

# Input section for AW IDs
st.header("AW ID Processor")
aw_ids_input = st.text_area("Enter AW IDs (comma-separated or one per line):")
if st.button("Process AW IDs"):
    if aw_ids_input:
        unique_aw_ids = get_unique_aw_ids(aw_ids_input)
        st.subheader("Unique AW IDs:")
        st.text('\n'.join(unique_aw_ids))
    else:
        st.error("Please enter at least one AW ID.")

# Input section for Artwork Names
st.header("Artwork Name to Short URL")
artwork_names_input = st.text_area("Enter artwork names (one per line):")
if st.button("Generate Short URLs"):
    if artwork_names_input:
        short_urls = generate_short_urls(artwork_names_input)
        st.subheader("Generated Short URLs:")
        st.text('\n'.join(short_urls))
    else:
        st.error("Please enter at least one artwork name.")
