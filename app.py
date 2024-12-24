import streamlit as st
import pandas as pd
from io import StringIO
import io
from methods import *
from langchain_ollama import ChatOllama
##################################################################################################
# # Create a custom function to extract and structure info
# def extract_df_info(df):
#     buffer = io.StringIO()
#     df.info(buf=buffer)
#     info_str = buffer.getvalue().split('\n')

#     # Extract column info
#     columns_info = info_str[4:-2]  # Skip the initial part and footer (e.g., memory usage)
#     column_data = []
#     for col_info in columns_info:
#         # Split into parts based on spaces for column details
#         parts = col_info.strip().split(" ")
#         new_list = list(filter(None, parts))
#         st.write(new_list)
#         column_name = new_list[1]
#         non_null_count = f"{new_list[2]} {new_list[3]}"
#         dtype = new_list[4]
#         column_data.append([column_name, non_null_count, dtype])
#     st.write(column_data)

#     # Convert into a DataFrame for display
#     info_df = pd.DataFrame(column_data, columns=["Column", "Non-Null Count", "Dtype"])
#     return info_df
##################################################################################################
def main():
    st.set_page_config(layout="wide")
    st.sidebar.title("Data Quality Analysis")
    uploaded_file = st.sidebar.file_uploader("Upload A .CSV File", type="csv")

    if uploaded_file is not None:
        if 'data' not in st.session_state:
            try:
                csv_file = StringIO(uploaded_file.getvalue().decode("utf-8"))
                df = pd.read_csv(csv_file)
                st.session_state['data'] = df
                st.sidebar.success("Dataset uploaded successfully!")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
        else:
            df = st.session_state['data'].copy()
##################################################################################################
        if st.sidebar.button("Show Data"):
            reset_all_flags()
            st.session_state['show_data'] = True
            st.rerun()

        if 'show_data' in st.session_state and st.session_state['show_data']:
            reset_all_flags()
            st.header("Data")
            st.write(df)

        st.sidebar.write("###################################")
##################################################################################################
        if st.sidebar.button("Data Info"):
            reset_all_flags()
            st.session_state['data_info'] = True
            st.rerun()

        if 'data_info' in st.session_state and st.session_state['data_info']:
            # reset_all_flags()

            st.header("Data Info")
            buffer = io.StringIO()
            df.info(buf=buffer)
            info_output = buffer.getvalue().split('\n')

            st.text(f"{info_output[1]}\n{info_output[2]}")

            info_data = {
                'Column': df.columns,
                'Non-Null Count': df.count(),
                'Dtype': df.dtypes
            }

            info_df = pd.DataFrame(info_data)
            info_df.reset_index(drop=True, inplace=True)
            st.dataframe(info_df)

            st.text(f"{info_output[17]}\n{info_output[18]}")

            # # Extract and display the DataFrame info
            # info_df = extract_df_info(df)
            # st.text(info_df)
        st.sidebar.write("###################################")
##################################################################################################
        if st.sidebar.button("Describe Data"):
            reset_all_flags()
            st.session_state['describe_data'] = True
            st.rerun()

        if 'describe_data' in st.session_state and st.session_state['describe_data']:
            # reset_all_flags()
            st.header("Data Description")
            st.table(df.describe())
        st.sidebar.write("###################################")
##################################################################################################
        col1, col2 = st.columns(2)
        if st.sidebar.button("Data Type Analysis"):
            reset_all_flags()
            # reset_all_flags()
            st.session_state['data_type_analysis_clicked'] = True
            st.rerun()

        if 'data_type_analysis_clicked' in st.session_state and st.session_state['data_type_analysis_clicked']:
            with col1:
                st.header("Data Types Analysis")
                st.subheader("Before:")
                st.write(df.dtypes)
            # reset_all_flags()
            # st.session_state['data_type_analysis_clicked'] = True
            st.sidebar.subheader("Convert Data Types:")
            selected_column = st.sidebar.selectbox("Select A Column To Convert", df.columns)
            new_type = st.sidebar.selectbox("Select The New Data Type", ["int", "float", "str", "datetime"])

            if st.sidebar.button("Convert Data Type"):
                data_type_conversion(df, selected_column, new_type)

        if 'type_converted' in st.session_state and st.session_state['type_converted']:
            with col2:
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.subheader("After:")
                st.write(data_type_conversion(df, selected_column, new_type).dtypes)
                # st.session_state['data_type_analysis_clicked'] = False
                # reset_all_flags()
            if st.sidebar.button("Apply"):
                st.session_state['data'] = data_type_conversion(df, selected_column, new_type)
                st.success(f"Column '{selected_column}' Converted To '{new_type}' Successfully!")
                # reset_all_flags()
                # st.session_state['type_converted'] = False
        st.sidebar.write("###################################")
##################################################################################################
        if st.sidebar.button("Column Name Analysis"):
            reset_all_flags()
            st.session_state['column_name_analysis_clicked'] = True
            # For Removing "Data Type Analysis" Sidebar Content:
            st.rerun()

        if 'column_name_analysis_clicked' in st.session_state and st.session_state['column_name_analysis_clicked']:
            df = column_names_analysis(df)
            # For Removing The Last Function Content:
            # reset_all_flags()

        if 'columns_renamed' in st.session_state and st.session_state['columns_renamed']:
            st.write(df.columns)
            # reset_all_flags()

        st.sidebar.write("###################################")
##################################################################################################
        if st.sidebar.button("Missing Value Analysis"):
            reset_all_flags()
            st.session_state['missing_analysis_run'] = True
            st.rerun()
            
        if 'missing_analysis_run' in st.session_state and st.session_state['missing_analysis_run']:
            missing_value_analysis(df)
            # reset_all_flags()
            # st.session_state['missing_analysis_run'] = True

            method_options = ["-- Select Method --", "mean", "median", "mode", "drop"]
            column_options = ["-- Select Column --"] + list(df.columns)
            method = st.sidebar.selectbox("Select Method", method_options)
            column = st.sidebar.selectbox("Select Column (Optional)", column_options)
            
            if column == column_options[0]:
                column = None

            if st.sidebar.button("Handle Missing Values"):
                if method != method_options[0] or method == None:
                    data_frame = handle_missing_values(df, method, column)
                    st.header("After Handling Missing Values")
                    missing_value_analysis(data_frame)
                    # st.session_state['missing_values_handled'] = True
                    # reset_all_flags()
                else:
                    st.sidebar.error("Please, Select A Method!")
                    # reset_all_flags()

            if st.sidebar.button("Apply"):
                if method != method_options[0] or method == None:
                    st.session_state['data'] = handle_missing_values(df, method, column)
                    st.success("Changes Applied Successfully!")
                    st.header("After Applying Handling Missing Values")
                    missing_value_analysis(df)
                    # st.session_state['missing_analysis_run']= False
                else:
                    st.sidebar.error("Please, Select A Method!")

            # if 'missing_values_handled' in st.session_state and st.session_state['missing_values_handled']:
            #     reset_all_flags()
        st.sidebar.write("###################################")
##################################################################################################
        if st.sidebar.button("Handle Duplicates"):
            reset_all_flags()
            st.session_state['duplicate_analysis_run'] = True
            st.rerun()
            # For Removing "Column Name Analysis" Function Content:
            # st.rerun()

        if 'duplicate_analysis_run' in st.session_state and st.session_state['duplicate_analysis_run']:
            df = handle_duplicates(df)

        if 'duplicates_handled' in st.session_state and st.session_state['duplicates_handled']:
            st.header("Dataset After Handling Duplicates")
            st.write(df)
            # st.session_state['duplicates_handled'] = False
        st.sidebar.write("###################################")
##################################################################################################
        column_for_outlier = st.sidebar.selectbox("Select Column For Outlier Analysis", df.select_dtypes(include='number').columns)
        # lower_bound = upper_bound = zero = None

        if st.sidebar.button("Outlier Analysis"):
            reset_all_flags()
            st.session_state['outlier_analysis_run'] = True
            st.rerun()

        if 'outlier_analysis_run' in st.session_state and st.session_state['outlier_analysis_run']:
            st.header("Outlier Analysis")
            st.subheader("Before:")
            lower_bound, upper_bound, zero = outlier_analysis(df, column_for_outlier)
            # reset_all_flags()
            # st.session_state['outlier_analysis_run'] = True

            if lower_bound is not None and upper_bound is not None:
                outlier_method = st.sidebar.selectbox("Select Outlier Handling Method", ['clip', 'drop'])
                if st.sidebar.button("Handle Outliers"):
                    if zero != 0:
                        dataf, length = handle_outliers(df, column_for_outlier, lower_bound, upper_bound, outlier_method)
                        st.subheader("After:")
                        # st.subheader(f"Number Of Outliers In '{column_for_outlier}': {length}")
                        outlier_analysis(dataf, column_for_outlier)
                        # st.session_state['outliers_handled'] = True
                    else:
                        st.error("No Outliers To Handle!")
            if st.sidebar.button("Apply"):
                if zero != 0:
                    st.session_state['data'], len = handle_outliers(df, column_for_outlier, lower_bound, upper_bound, outlier_method)
                    st.success("Changes Applied Successfully!")
                    zero = 1
                else:
                    st.error("No Operation To Apply!")
                    # reset_all_flags()
                # reset_all_flags()

        if 'outliers_handled' in st.session_state and st.session_state['outliers_handled']:
            st.header("Data after Handling Outliers")
            st.write(df)
            # st.session_state['outliers_handled'] = False
        st.sidebar.write("###################################")
##################################################################################################
        column_to_visualize = st.sidebar.selectbox("Select Column For Visualization", df.columns)

        if st.sidebar.button("Visualize Data"):
            reset_all_flags()
            st.session_state['visualize_data_run'] = True
            st.rerun()

        if 'visualize_data_run' in st.session_state and st.session_state['visualize_data_run']:
            st.header("Data Visualization")
            fig1, fig2 = visualize_data(df, column_to_visualize)
            st.pyplot(fig1)
            st.pyplot(fig2)
            # st.session_state['visualize_data_run'] = False
        st.sidebar.write("###################################")
##################################################################################################
        if st.sidebar.button("Correlation Matrix"):
            reset_all_flags()
            st.session_state['correlation_run'] = True
            st.rerun()

        if 'correlation_run' in st.session_state and st.session_state['correlation_run']:
            # reset_all_flags()
            st.header("Correlation Matrix")
            fig = correlation_matrix(df)
            if fig is not None:
                st.pyplot(fig)
            # st.session_state['correlation_run']= False
        st.sidebar.write("###################################")
##################################################################################################
        if st.sidebar.button("Generate Download Dataset Link"):
            download_dataset(df)
        st.sidebar.write("###################################")
##################################################################################################
        if st.sidebar.button("Chat"):
            reset_all_flags()
            st.session_state['RAG'] = True
            st.rerun()

        if 'RAG' in st.session_state and st.session_state['RAG']:
            st.title("🧠 Chat With Ollama 3.2:Latest")

            with st.form("llm-form"):
                text = st.text_area("Enter Your Question or Statement:")
                submit = st.form_submit_button("Submit")
            if st.button("Chat History"):
                st.session_state['chat_history_run'] = True

            if "chat_history" not in st.session_state:
                st.session_state['chat_history'] = []

            if submit and text:
                with st.spinner("Generating Response..."):
                    response = generate_response(text)
                    st.session_state['chat_history'].append({"user": text, "ollama": response})
                    st.write(response)

        if 'chat_history_run' in st.session_state and st.session_state['chat_history_run']:
            st.write("## Chat History")
            if st.session_state['chat_history']:
                for chat in reversed(st.session_state['chat_history']):
                    st.write(f"**🧑 User**: {chat['user']}")
                    st.write(f"**🧠 Assistant**: {chat['ollama']}")
                    st.write("---")
            else:
                st.warning("No Chat Histories!")

            # For Removing "Outlier Analysis" Functoin (outlier_analysis) Content:
            # st.rerun()
##################################################################################################
def generate_response(input_text):
    model = ChatOllama(model="llama3.2:latest", base_url="http://localhost:11434/")

    response = model.invoke(input_text)

    return response.content

if __name__ == "__main__":
    main()