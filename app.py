import streamlit as st
import re
import pandas as pd

# Function to clean non-English characters and any English values before the last non-English character
def clean_non_english(text):
    # Find all non-ASCII characters
    matches = list(re.finditer(r'[^\x00-\x7F]', text))
    if matches:
        # Get the last non-ASCII character's end position
        last_non_ascii_end = matches[-1].end()
        # Keep only the part after the last non-English character
        text = text[last_non_ascii_end:].strip()
        # Remove any remaining non-English characters, keeping ASCII letters, digits, and spaces
        text = re.sub(r'[^\x00-\x7F]', ' ', text).strip()
    # If no non-ASCII character found, return original text
    return text

# Function to generate short URLs from artwork names
def generate_short_urls(artwork_names):
    short_urls = []
    name_count = {}
    
    for name in artwork_names:
        # Apply word replacements
        name = re.sub(r'\biphone\b', 'phone', name, flags=re.IGNORECASE)
        name = re.sub(r'\bipad\b', 'tablet', name, flags=re.IGNORECASE)
        name = re.sub(r'\bairpods\b', 'earbuds', name, flags=re.IGNORECASE)
        # Convert to lowercase, replace special characters (except apostrophes) with spaces
        clean_name = re.sub(r'[^\w\s\']', ' ', name.lower()).strip()
        # Replace multiple spaces with single space and then replace spaces with hyphens
        slug = '-'.join(clean_name.split())
        # Remove apostrophes
        slug = slug.replace("'", "")
        
        # Handle duplicates to match format: e.g., i-just-cant-sit-still, i-just-cant-sit-still-atwgp1
        if slug in name_count:
            name_count[slug] += 1
            short_urls.append(f"{slug}-atwgp{name_count[slug]}")
        else:
            name_count[slug] = 0
            short_urls.append(slug)
    
    return short_urls

# Function to process input for TSV generation
def process_input_for_tsv(input_text, user_id, user_name):
    # Split input by newlines and strip whitespace
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    aw_id_name_pairs = []
    
    # Parse each line for artwork name and AW IDs
    for line in lines:
        # Split by tabs
        columns = re.split(r'\t+', line)
        if len(columns) >= 2:
            if len(columns) >= 3:
                # Three columns: Artwork Name in Line Sheet, Product Type, AW IDs
                artwork_name_line = clean_non_english(columns[0 strip()]
                product_type = clean_non_english(columns[1].strip())
                # Apply word replacements
                artwork_name_line = re.sub(r'\biphone\b', 'phone', artwork_name_line, flags=re.IGNORECASE)
                artwork_name_line = re.sub(r'\bipad\b', 'tablet', artwork_name_line, flags=re.IGNORECASE)
                artwork_name_line = re.sub(r'\bairpods\b', 'earbuds', artwork_name_line, flags=re.IGNORECASE)
                product_type = re.sub(r'\biphone\b', 'phone', product_type, flags=re.IGNORECASE)
                product_type = re.sub(r'\bipad\b', 'tablet', product_type, flags=re.IGNORECASE)
                product_type = re.sub(r'\bairpods\b', 'earbuds', product_type, flags=re.IGNORECASE)
                # Only concatenate if both parts are non-empty
                if artwork_name_line and product_type:
                    artwork_name = f"{artwork_name_line} {product_type}"
                elif artwork_name_line:
                    artwork_name = artwork_name_line
                elif product_type:
                    artwork_name = product_type
                else:
                    artwork_name = ""
                aw_ids = [token.strip() for token in re.split(r'[,\s]+', clean_non_english(columns[2])) if token.strip() and token.isdigit()]
            else:
                # Two columns: Artwork Name, AW IDs
                artwork_name = clean_non_english(columns[0].strip())
                # Apply word replacements
                artwork_name = re.sub(r'\biphone\b', 'phone', artwork_name, flags=re.IGNORECASE)
                artwork_name = re.sub(r'\bipad\b', 'tablet', artwork_name, flags=re.IGNORECASE)
                artwork_name = re.sub(r'\bairpods\b', 'earbuds', artwork_name, flags=re.IGNORECASE)
                aw_ids = [token.strip() for token in re.split(r'[,\s]+', clean_non_english(columns[1])) if token.strip() and token.isdigit()]
            
            # Pair each AW ID with the artwork name, if artwork_name is not empty
            if artwork_name:
                for aw_id in aw_ids:
                    aw_id_name_pairs.append((aw_id, artwork_name))
    
    # Remove duplicate AW IDs while preserving order and keeping the first associated artwork name
    unique_aw_id_pairs = []
    seen_aw_ids = set()
    for aw_id, artwork_name in aw_id_name_pairs:
        if aw_id not in seen_aw_ids:
            unique_aw_id_pairs.append((aw_id, artwork_name))
            seen_aw_ids.add(aw_id)
    
    # Generate short URLs
    artwork_names = [pair[1] for pair in unique_aw_id_pairs]
    short_urls = generate_short_urls(artwork_names)
    
    # Create DataFrame with all required columns
    df = pd.DataFrame({
        'id': [pair[0] for pair in unique_aw_id_pairs],
        'user_id': [user_id] * len(unique_aw_id_pairs),
        'user_name': [user_name] * len(unique_aw_id_pairs),
        'status': ['N'] * len(unique_aw_id_pairs),
        'art_work_name': artwork_names,
        'art_work_url_name': short_urls,
        'sell_design_approval_status': ['P'] * len(unique_aw_id_pairs),
        'is_public': [1] * len(unique_aw_id_pairs)
    })
    
    # Convert to TSV string
    return df.to_csv(sep='\t', index=False)

# Streamlit app layout
st.title("TSV Generator")

# User inputs for user_id and user_name
user_id = st.text_input("User ID:")
user_name = st.text_input("User Name:")

# Input for artwork names and AW IDs
st.write("Enter either two tab-separated columns (Artwork Name, AW IDs) or three tab-separated columns (Artwork Name in Line Sheet, Product Type, AW IDs). Non-English characters and any values before the last non-English character will be removed. Words like 'iphone', 'ipad', and 'airpods' will be replaced with 'phone', 'tablet', and 'earbuds' respectively in Artwork Name and Short URL. Apostrophes are removed in Short URLs (e.g., 'can't' becomes 'cant' in Short URL).")
input_text = st.text_area("Artwork Names and AW IDs:", 
                         placeholder="",
                         key="input_text")

# Initialize session state for TSV content
if 'tsv_content' not in st.session_state:
    st.session_state.tsv_content = None

# Button to generate and store TSV content
if st.button("Generate TSV", key="btn_generate_tsv"):
    if input_text and user_id and user_name:
        tsv_content = process_input_for_tsv(input_text, user_id, user_name)
        if tsv_content:
            st.session_state.tsv_content = tsv_content
        else:
            st.error("No valid numeric AW IDs found in the input.")
    else:
        st.error("Please enter User ID, User Name, and at least one line with an artwork name and AW IDs.")

# Download button for TSV file
if st.session_state.tsv_content:
    st.download_button(
        label="Download TSV for Google Sheets",
        data=st.session_state.tsv_content,
        file_name="artwork_data.tsv",
        mime="text/tab-separated-values"
    )
