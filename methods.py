import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import base64

def data_type_conversion(dataFrame, selected_column, new_type):
    try:
        if new_type == "datetime":
            dataFrame[selected_column] = pd.to_datetime(dataFrame[selected_column], errors='coerce')
        else:
            dataFrame[selected_column] = dataFrame[selected_column].astype(new_type)
        # Add type_converted to session_state:
        st.session_state['type_converted'] = True
        # st.success(f"Column '{selected_column}' Converted To '{new_type}' Successfully!")
        # st.header("Data Types Analysis")
        # st.write(dataFrame.dtypes)
        # For Removing After Done Content:
    except Exception as e:
        st.error(f"Error Converting Column '{selected_column}': {e}")
    return dataFrame
##################################################################################################
def column_names_analysis(df):
    st.header("Column Name Analysis")
    st.subheader("Current Column Names:")
    st.write(df.columns)

    st.subheader("Rename Columns:")
    new_columns_names = {}
    for col in df.columns:
        new_columns_names[col] = st.text_input(f"Rename '{col}' To:", value=col)
    if st.button("Apply Column Renaming"):
        try:    
            df.rename(columns=new_columns_names, inplace=True)
            st.session_state['data'] = df
            # Add key columns_renamed to session_state:
            st.session_state['columns_renamed'] = True
            st.success("Columns Renamed Successfully!")
        except Exception as e:
            st.error(f"Error renaming columns: {e}")
    return df
##################################################################################################
def missing_value_analysis(df):
    st.header("Missing Value Analysis")
    missing_values = df.isnull().sum()

    st.write("Missing Values per Column:")
    st.table(missing_values)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df.isnull(), cmap="viridis", cbar=True, ax=ax)
    plt.title("Missing Values Heatmap")
    st.pyplot(fig)

def handle_missing_values(df, method, column=None):
    if method in ["mean", "median", "mode"]:
        if column:
            if method in ["mean", "median"] and not pd.api.types.is_numeric_dtype(df[column]):
                st.error(f"Column '{column}' Is Not Numeric And Cannot Use {method}.")
                return df
            fill_value = getattr(df[column], method)() if method != "mode" else df[column].mode()[0]
            df[column].fillna(fill_value, inplace=True)
        else:
            fill_value = getattr(df.select_dtypes(include="number"), method)() if method != "mode" else df.mode().iloc[0]
            df.fillna(fill_value, inplace=True)
    elif method == "drop":
        df.dropna(subset=[column] if column else None, inplace=True)
    return df
##################################################################################################
def handle_duplicates(df):
    st.header("Duplicate Analysis")
    num_duplicates = df.duplicated().sum()
    st.subheader("Before:")
    st.subheader(f"Number Of Duplicated Rows: {num_duplicates}")
    st.subheader("After:")
    st.subheader(f"Number Of Duplicated Rows: 0")

    if num_duplicates > 0:
        show_duplicates = st.checkbox("Show Duplicate Rows")
        if show_duplicates:
            st.write(df[df.duplicated(keep=False)])
        if st.button("Apply"):
            df.drop_duplicates(inplace=True)
            st.session_state['data'] = df
            # Add
            st.session_state['duplicates_handled'] = True
            reset_all_flags()
            st.success("Duplicated Rows Removed Successfully!")
    return df
##################################################################################################
def outlier_analysis(df, column):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]

    st.subheader(f"Number Of Outliers In '{column}': {len(outliers)}")
    if not outliers.empty:
        st.write(outliers)

        if st.checkbox("Show Outliers Visualization"):
            if len(outliers) != 0:
                fig, ax = plt.subplots()
                sns.boxplot(x=df[column], ax=ax)
                sns.scatterplot(x=outliers[column], y=[0]*len(outliers), color='red', marker='o', ax=ax)
                plt.title(f"Box Plot of {column} with Outliers highlighted")
                st.pyplot(fig)
    return lower_bound, upper_bound, len(outliers)

def handle_outliers(df, column, lower_bound, upper_bound, method):
    if method == 'clip':
        df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        st.success(f"Outliers In {column} Have Been Clipped To The Defined Bounds!")
    elif method == 'drop':
        df.drop(df[(df[column] < lower_bound) | (df[column] > upper_bound)].index, inplace=True)
        st.success(f"Outliers In {column} Have Been Removed!")
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return df, len(outliers)
##################################################################################################
def visualize_data(df, column):
    fig, ax = plt.subplots()
    sns.histplot(df[column], ax=ax, kde=True)
    plt.title(f"Histogram Of {column} With KDE")
    plt.xlabel(column)
    plt.ylabel("Frequency")

    fig2, ax2 = plt.subplots()
    sns.boxplot(x=df[column], ax=ax2)
    plt.title(f"Box Plot Of {column}")
    return fig, fig2
##################################################################################################
def correlation_matrix(df):
    numeric_cols = df.select_dtypes(include='number')
    if numeric_cols.empty:
        st.warning("No Numeric Columns Found For Correlation Analysis!")
        return None
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(numeric_cols.corr(), annot=True, ax=ax, cmap='coolwarm')
    plt.title("Correlation Matrix (Numeric Columns)")
    return fig
##################################################################################################
def download_dataset(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="downloaded_data.csv">Download (CSV)</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)
##################################################################################################
def reset_all_flags():
    keys_to_reset = [
        'show_data', 'describe_data', 'data_info',
        'missing_analysis_run', 'missing_values_handled',
        'duplicate_analysis_run', 'duplicates_handled',
        'outlier_analysis_run', 'outliers_handled',
        'visualize_data_run', 'correlation_run',
        'type_converted', 'column_type_analysis_clicked','data_type_analysis_clicked',
        'columns_renamed', 'column_name_analysis_clicked',
        'RAG', 'chat_history'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            st.session_state[key] = False