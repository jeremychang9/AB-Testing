import streamlit as st
import pandas as pd

def load_data(file):
    return pd.read_excel(file, sheet_name=None)

def main():
    # Expand page width
    st.set_page_config(layout="wide")

    st.title("A/B Testing Annotation Tool")

    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
    
    if uploaded_file:
        df_dict = load_data(uploaded_file)
        sheet_names = list(df_dict.keys())
        selected_sheet = st.selectbox("Select a Comparison Group", sheet_names)
        df = df_dict[selected_sheet]

        # Initialize session state
        if 'df' not in st.session_state:
            st.session_state['df'] = df.copy()

        # Ensure annotation columns exist
        for col in ['Prosociality', 'Engaged', 'Respect', 'Coherency', 'Overall']:
            if col not in st.session_state['df']:
                st.session_state['df'][col] = None

        # Pagination settings
        page_size = 5
        total_pages = (len(st.session_state['df']) // page_size) + (1 if len(st.session_state['df']) % page_size != 0 else 0)
        page_number = st.number_input("Page", min_value=1, max_value=total_pages, step=1, value=1)
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        df_page = st.session_state['df'].iloc[start_idx:end_idx]

        for i, row in df_page.iterrows():
            # Create a section for each entry
            st.markdown(f"""
                <div style="
                    background-color: #f7e5d6; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin-bottom: 15px;">
                    <p style="font-size: 22px; font-weight: bold;">Entry {i+1+start_idx}</p>
                    <p><strong>Context:</strong> {row['context']}</p>
                </div>
            """, unsafe_allow_html=True)

            # Two-column layout for Option A and B
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div style="
                        background-color: #d6ecf7; 
                        padding: 10px; 
                        border-radius: 5px;">
                        <strong>Option A:</strong> {row['A']}
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div style="
                        background-color: #d6ecf7; 
                        padding: 10px; 
                        border-radius: 5px;">
                        <strong>Option B:</strong> {row['B']}
                    </div>
                """, unsafe_allow_html=True)

            # **Metrics Section (Inside a Box)**
            st.markdown("""
                <div style="
                    background-color: #f0e5f7; 
                    padding: 15px; 
                    border-radius: 10px;
                    margin-top: 10px;">
                    <p style="font-size: 18px; font-weight: bold;">Evaluation Metrics</p>
            """, unsafe_allow_html=True)

            # 5-column layout for ratings
            with st.container():  # Ensure it's inside the same container
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.session_state['df'].at[i, 'Prosociality'] = st.radio(
                        "Prosociality", ["Option A wins", "Tie", "Option B wins"], index=1, key=f"Prosociality_{i}"
                    )
                with col2:
                    st.session_state['df'].at[i, 'Engaged'] = st.radio(
                        "Engaged", ["Option A wins", "Tie", "Option B wins"], index=1, key=f"Engaged_{i}"
                    )
                with col3:
                    st.session_state['df'].at[i, 'Respect'] = st.radio(
                        "Respect", ["Option A wins", "Tie", "Option B wins"], index=1, key=f"Respect_{i}"
                    )
                with col4:
                    st.session_state['df'].at[i, 'Coherency'] = st.radio(
                        "Coherency", ["Option A wins", "Tie", "Option B wins"], index=1, key=f"Coherency_{i}"
                    )
                with col5:
                    st.session_state['df'].at[i, 'Overall'] = st.radio(
                        "Overall", ["Option A wins", "Tie", "Option B wins"], index=1, key=f"Overall_{i}"
                    )

            # Close the metrics section
            st.markdown("</div>", unsafe_allow_html=True)
            st.write("---")  # Add separation between entries

        # Save Annotations Button
        if st.button("Save Annotations"):
            output_path = "annotated_data.xlsx"
            st.session_state['df'].to_excel(output_path, index=False)
            st.success(f"Annotations saved to {output_path}")

            with open(output_path, "rb") as file:
                st.download_button("Download Annotated File", file, "annotated_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
