import streamlit as st
import re
import pandas as pd

# Initialize session state to store results
if 'full_table_result' not in st.session_state:
    st.session_state.full_table_result = None
if 'pdp_result' not in st.session_state:
    st.session_state.pdp_result = None

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

# Function to process input and extract unique AW IDs
def process_input(input_text):
    # Split input by newlines and strip whitespace
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    aw_ids = []
    
    # Parse each line for AW IDs
    for line in lines:
        # Clean non-English characters and English values before the first non-English character
        cleaned_line = clean_non_english(line)
        if cleaned_line:
            # Extract numeric IDs from the cleaned line
            tokens = re.split(r'[,\s]+', cleaned_line)
            for token in tokens:
                if token.strip().isdigit():
                    aw_ids.append(token.strip())
    
    # Remove duplicate AW IDs while preserving order
    unique_aw_ids = []
    seen_aw_ids = set()
    for aw_id in aw_ids:
        if aw_id not in seen_aw_ids:
            unique_aw_ids.append(aw_id)
            seen_aw_ids.add(aw_id)
    
    # Format as comma-separated string
    return ', '.join(unique_aw_ids)

# Function to process input for full table (artwork names and AW IDs)
def process_input_for_table(input_text):
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
                artwork_name_line = clean_non_english(columns[0].strip())
                product_type = clean_non_english(columns[1].strip())
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
                aw_ids = [token.strip() for token in re.split(r'[,\s]+', clean_non_english(columns[1])) if token.strip() and token.isdigit()]
            
            # Pair each AW ID with the artwork name, if artwork_name is not empty
            if artwork_name:
                for aw_id in aw_ids:
                    aw_id_name_pairs.append((aw_id, artwork_name))
    
    # Remove duplicate AW IDs while preserving order and keeping the first associated artwork name
    unique_aw_ids = []
    seen_aw_ids = set()
    for aw_id, artwork_name in aw_id_name_pairs:
        if aw_id not in seen_aw_ids:
            unique_aw_ids.append((aw_id, artwork_name))
            seen_aw_ids.add(aw_id)
    
    return unique_aw_ids

# Function to generate short URLs from artwork names
def generate_short_urls(artwork_names):
    short_urls = []
    name_count = {}
    
    for name in artwork_names:
        # Convert to lowercase, replace special characters with spaces, and split
        clean_name = re.sub(r'[^\w\s]', ' ', name.lower()).strip()
        # Replace multiple spaces with single space and then replace spaces with hyphens
        slug = '-'.join(clean_name.split())
        
        # Handle duplicates to match format: e.g., absolutely-no-problem-phone-cases, absolutely-no-problem-phone-cases-atwgp1, etc.
        if slug in name_count:
            name_count[slug] += 1
            short_urls.append(f"{slug}-atwgp{name_count[slug]}")
        else:
            name_count[slug] = 0
            short_urls.append(slug)
    
    return short_urls

# Function to create a table from AW IDs, artwork names, and short URLs
def create_id_name_url_table(aw_ids, artwork_names, short_urls):
    # Create DataFrame
    df = pd.DataFrame({
        'AW ID': aw_ids,
        'Artwork Name': artwork_names,
        'Short URL': short_urls
    })
    return df

# Function to generate amended TSV file content with additional columns
def generate_tsv_file(df, amended=False):
    if amended:
        # Create DataFrame with all columns from the sample data
        amended_df = pd.DataFrame({
            'id': df['AW ID'],
            'user_id': ['40992246'] * len(df),  # Fixed user_id from sample
            'user_name': ['afaleecyu'] * len(df),  # Fixed user_name from sample
            'status': ['N'] * len(df),  # Fixed status from sample
            'art_work_name': df['Artwork Name'],
            'art_work_url_name': df['Short URL'],
            'sell_design_approval_status': ['P'] * len(df),  # Fixed status from sample
            'is_public': [1] * len(df)  # Fixed is_public from sample
        })
        # Convert to TSV string
        return amended_df.to_csv(sep='\t', index=False)
    else:
        # Original TSV with AW ID, Artwork Name, Short URL
        return df.to_csv(sep='\t', index=False)

# Function to format unique AW IDs for PDP
def process_for_pdp(aw_ids):
    # Join unique AW IDs with commas and spaces
    return ', '.join(aw_ids)

# Streamlit app layout
st.title("Artwork ID and URL Generator")

# Block 1: Generate Full Table
with st.container():
    st.header("Generate Full Table")
    st.write("Enter either two tab-separated columns (Artwork Name, AW IDs) or three tab-separated columns (Artwork Name in Line Sheet, Product Type, AW IDs). Non-English characters and any values before the last non-English character will be removed, and the output Artwork Name will start with English characters.")
    input_text_name_id = st.text_area("Artwork Names and AW IDs:", 
                                     placeholder="e.g., Please Input!",
                                     key="name_id_input")
    
    if st.button("Generate Full Table", key="btn_full_table"):
        if input_text_name_id:
            unique_aw_id_pairs = process_input_for_table(input_text_name_id)
            if unique_aw_id_pairs:
                # Extract AW IDs and artwork names
                aw_ids = [pair[0] for pair in unique_aw_id_pairs]
                artwork_names = [pair[1] for pair in unique_aw_id_pairs]
                # Generate short URLs from artwork names
                short_urls = generate_short_urls(artwork_names)
                
                # Create table
                df = create_id_name_url_table(aw_ids, artwork_names, short_urls)
                st.session_state.full_table_result = {
                    'df': df,
                    'table_text': df.to_string(index=False),
                    'tsv_content': generate_tsv_file(df, amended=False),
                    'amended_tsv_content': generate_tsv_file(df, amended=True)
                }
            else:
                st.session_state.full_table_result = {'error': "No valid numeric AW IDs found in the input."}
        else:
            st.session_state.full_table_result = {'error': "Please enter at least one line with an artwork name and AW IDs."}
    
    # Display Full Table result if it exists
    if st.session_state.full_table_result:
        if 'error' in st.session_state.full_table_result:
            st.error(st.session_state.full_table_result['error'])
        else:
            st.write("Generated Table:")
            st.dataframe(st.session_state.full_table_result['df'])
            st.text_area("Copyable Table Content:", 
                         st.session_state.full_table_result['table_text'], 
                         height=150, 
                         key="full_table_copy")
            st.markdown("""
                <script>
                function copyToClipboardFull() {
                    const text = document.getElementById('full_table_copy').value;
                    navigator.clipboard.writeText(text).then(() => {
                        alert('Table copied to clipboard!');
                    });
                }
                </script>
                <textarea id="full_table_copy" style="display:none;">{}</textarea>
                <button onclick="copyToClipboardFull()">Copy Table to Clipboard</button>
            """.format(st.session_state.full_table_result['table_text']), unsafe_allow_html=True)
            
            # Add download button for original TSV file
            if 'tsv_content' in st.session_state.full_table_result:
                st.download_button(
                    label="Download Original TSV for Google Sheets",
                    data=st.session_state.full_table_result['tsv_content'],
                    file_name="artwork_data.tsv",
                    mime="text/tab-separated-values"
                )
            
            # Add download button for amended TSV file
            if 'amended_tsv_content' in st.session_state.full_table_result:
                st.download_button(
                    label="Download Amended TSV for Google Sheets",
                    data=st.session_state.full_table_result['amended_tsv_content'],
                    file_name="amended_artwork_data.tsv",
                    mime="text/tab-separated-values"
                )

# Divider for visual separation
st.markdown("---")

# Block 2: Process for PDP
with st.container():
    st.header("Process for PDP")
    st.write("Enter one AW ID per line. Non-English characters and any English values before them will be removed in the output.")
    input_text_ids = st.text_area("AW IDs:", 
                                 placeholder="e.g., Please Input!",
                                 key="ids_input")
    
    if st.button("Process for PDP", key="btn_pdp"):
        if input_text_ids:
            pdp_text = process_input(input_text_ids)
            if pdp_text:
                st.session_state.pdp_result = {'pdp_text': pdp_text}
            else:
                st.session_state.pdp_result = {'error': "No valid numeric AW IDs found in the input."}
        else:
            st.session_state.pdp_result = {'error': "Please enter at least one AW ID."}
    
    # Display PDP result if it exists
    if st.session_state.pdp_result:
        if 'error' in st.session_state.pdp_result:
            st.error(st.session_state.pdp_result['error'])
        else:
            st.write("PDP Formatted AW IDs:")
            st.text(st.session_state.pdp_result['pdp_text'])
            st.text_area("Copyable PDP AW IDs:", 
                         st.session_state.pdp_result['pdp_text'], 
                         height=100, 
                         key="pdp_copy")
            st.markdown("""
                <script>
                function copyToClipboardPDP() {
                    const text = document.getElementById('pdp_copy').value;
                    navigator.clipboard.writeText(text).then(() => {
                        alert('PDP AW IDs copied to clipboard!');
                    });
                }
                </script>
                <textarea id="pdp_copy" style="display:none;">{}</textarea>
                <button onclick="copyToClipboardPDP()">Copy PDP AW IDs to Clipboard</button>
            """.format(st.session_state.pdp_result['pdp_text']), unsafe_allow_html=True)
