import streamlit as st
import pandas as pd
import os

def load_data(file):
    df = pd.read_excel(file, sheet_name=None)
    return df

def main():
    # Set the custom CSS for contrastive design
    st.markdown("""
    <style>
        /* General styling for the page */
        body {
            background-color: #f0f0f0;
            font-family: Arial, sans-serif;
        }

        /* Title */
        h1 {
            color: #ffffff;
            background-color: #FF6347;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }

        /* Section containers with background color */
        .section-container {
            background-color: #dcf2ec;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }

        .metric-container {
            background-color: #e0f7fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
        }

        /* Styling for Save and Download buttons */
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
        }

        .stButton > button:hover {
            background-color: #45a049;
        }

        /* Add some margin to the input elements */
        .stRadio, .stNumberInput, .stSelectbox {
            margin-top: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("A/B Testing Annotation Tool")
    
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])
    
    if uploaded_file is not None:
        # Load data from the uploaded Excel file
        df_dict = load_data(uploaded_file)
        sheet_names = list(df_dict.keys())
        selected_sheet = st.selectbox("Select a Comparison Group", sheet_names)
        df = df_dict[selected_sheet]
        
        # Initialize session state if it's not already set
        if 'df' not in st.session_state:
            st.session_state['df'] = df.copy()

        # Create columns for annotations if they don't exist
        if 'Prosociality' not in st.session_state['df']:
            st.session_state['df']['Prosociality'] = None
            st.session_state['df']['Engaged'] = None
            st.session_state['df']['Respect'] = None
            st.session_state['df']['Coherency'] = None
            st.session_state['df']['Overall'] = None
        
        # Display the A/B testing table with distinct sections for each entry and metrics
        page_size = 10
        total_pages = (len(st.session_state['df']) // page_size) + (1 if len(st.session_state['df']) % page_size != 0 else 0)
        page_number = st.number_input("Page", min_value=1, max_value=total_pages, step=1, value=1)
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        df_page = st.session_state['df'].iloc[start_idx:end_idx]

        for i, row in df_page.iterrows():
            # Create a section for each sample entry
            st.markdown(f'<div class="section-container">', unsafe_allow_html=True)
            
            # Wrap the Entry and Context inside the container
            with st.container():
                st.write(f"### Entry {i+1+start_idx}")
                st.write(f"**Context:** {row['context']}")
            
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Option A:** {row['A']}")
                
                with col2:
                    st.write(f"**Option B:** {row['B']}")
            
            # Create a section for metrics
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)

            # Horizontal display of metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                prosociality = st.radio(
                    f"Prosociality (Entry {i+1+start_idx})",
                    options=["Option A wins", "Tie", "Option B wins"],
                    index=1,  # Default is "Tie"
                    key=f"Prosociality_{i}"
                )
                st.session_state['df'].at[i, 'Prosociality'] = prosociality
                        
            with col2:
                engaged = st.radio(
                    f"Engaged (Entry {i+1+start_idx})",
                    options=["Option A wins", "Tie", "Option B wins"],
                    index=1,  # Default is "Tie"
                    key=f"Engaged_{i}"
                )
                st.session_state['df'].at[i, 'Engaged'] = engaged
           
            with col3:
                respect = st.radio(
                    f"Respect (Entry {i+1+start_idx})",
                    options=["Option A wins", "Tie", "Option B wins"],
                    index=1,  # Default is "Tie"
                    key=f"Respect_{i}"
                )
                st.session_state['df'].at[i, 'Respect'] = respect
            
            with col4:
                coherency = st.radio(
                    f"Coherency (Entry {i+1+start_idx})",
                    options=["Option A wins", "Tie", "Option B wins"],
                    index=1,  # Default is "Tie"
                    key=f"Coherency_{i}"
                )
                st.session_state['df'].at[i, 'Coherency'] = coherency
            
            with col5:
                overall = st.radio(
                    f"Overall (Entry {i+1+start_idx})",
                    options=["Option A wins", "Tie", "Option B wins"],
                    index=1,  # Default is "Tie"
                    key=f"Overall_{i}"
                )
                st.session_state['df'].at[i, 'Overall'] = overall

            st.markdown('</div>', unsafe_allow_html=True)  # End of metric container
            st.markdown('</div>', unsafe_allow_html=True)  # End of sample section

        # Save button with custom styling
        st.markdown('<button class="save-button">Save Annotations</button>', unsafe_allow_html=True)
        
        if st.button("Save Annotations"):
            # Calculate the count of each choice for each metric
            averages = {}
            for metric in ['Prosociality', 'Engaged', 'Respect', 'Coherency', 'Overall']:
                averages[metric] = st.session_state['df'][metric].value_counts()

            # Display the counts of wins/ties for each metric
            st.write("### Final Counts of Each Metric")
            for metric, counts in averages.items():
                st.write(f"{metric}:")
                for option, count in counts.items():
                    st.write(f"{option}: {count}")

            # Save the annotations to a file
            output_path = "annotated_data.xlsx"
            st.session_state['df'].to_excel(output_path, index=False)
            st.success(f"Annotations saved to {output_path}")
            
            # Provide download button with custom styling
            with open(output_path, "rb") as file:
                st.download_button(
                    label="Download Annotated File",
                    data=file,
                    file_name="annotated_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()
