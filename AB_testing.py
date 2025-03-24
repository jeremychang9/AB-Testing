import streamlit as st
import streamlit.components.v1 as components
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
        selected_sheet = st.selectbox("Select a Comparison Group", sheet_names, key="selected_sheet")
        
        # Update session state when selecting a new sheet
        if 'df_dict' not in st.session_state or st.session_state.get("uploaded_file") != uploaded_file:
            st.session_state['df_dict'] = df_dict.copy()
            st.session_state['uploaded_file'] = uploaded_file

        if 'df' not in st.session_state or st.session_state.get("current_sheet") != selected_sheet:
            st.session_state['df'] = st.session_state['df_dict'][selected_sheet].copy()
            st.session_state['current_sheet'] = selected_sheet

        # Ensure annotation columns exist without overwriting existing values
        for col in ['Prosociality', 'Engaged', 'Respect', 'Coherency', 'Overall']:
            if col not in st.session_state['df']:
                st.session_state['df'][col] = None

        # Pagination settings
        page_size = 10
        total_pages = (len(st.session_state['df']) // page_size) + (1 if len(st.session_state['df']) % page_size != 0 else 0)

        # Page selection (TOP)
        page_number = st.number_input("Page", min_value=1, max_value=total_pages, step=1, value=1, key="page_top")

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
                    <p style="font-size: 22px; font-weight: bold;">Example {i+1}</p>
                    <p><strong>Context:</strong> {row['context']}</p>
                    <p><strong>RoT:</strong> {row['RoT']}</p>
                    <p><strong>Golden:</strong> {row['gold']}</p>
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
            # Evaluation Metrics Title
            st.markdown("<p style='font-size: 18px; font-weight: bold; text-align: center;'>Evaluation Metrics</p>", unsafe_allow_html=True)

            # 5-column layout for ratings
            with st.container():  # Ensure it's inside the same container
                col1, col2, col3, col4, col5 = st.columns(5)
                for col_name, col_widget in zip(['Prosociality', 'Engaged', 'Respect', 'Coherency', 'Overall'], [col1, col2, col3, col4, col5]):
                    with col_widget:
                        default_index = 1  # Default to "Tie"
                        if pd.notna(row[col_name]) and row[col_name] in ["Option A", "Tie", "Option B"]:
                            default_index = ["Option A", "Tie", "Option B"].index(row[col_name])
                        st.session_state['df'].at[i, col_name] = st.radio(
                            col_name, ["Option A", "Tie", "Option B"], index=default_index, key=f"{col_name}_{i}"
                        )

            # Close the metrics section
            st.markdown("</div>", unsafe_allow_html=True)
            st.write("---")  # Add separation between entries
        
        # Save Annotations Button
        if st.button("Save Annotations"):
            output_path = "annotated_data.xlsx"
            st.session_state['df_dict'][selected_sheet] = st.session_state['df']  # Save modified sheet back to dictionary
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                for sheet_name, sheet_df in st.session_state['df_dict'].items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            st.success(f"Annotations saved to {output_path}")

            with open(output_path, "rb") as file:
                st.download_button("Download Annotated File", file, "annotated_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            # Compute and display average results
            avg_results = {}
            for col in ['Prosociality', 'Engaged', 'Respect', 'Coherency', 'Overall']:
                avg_results[col] = st.session_state['df'][col].value_counts(normalize=True).to_dict()
            
            st.markdown("### Average Annotation Results")
            for metric, values in avg_results.items():
                st.write(f"**{metric}:**")
                for option, percentage in values.items():
                    st.write(f"- {option}: {percentage:.2%}")

if __name__ == "__main__":
    main()
