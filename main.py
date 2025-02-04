import streamlit as st
import pandas as pd
import datetime
import os

# File to save/load data
DATA_FILE = "sales_data.csv"
HISTORY_FILE = "sales_history.csv"

# Initialize or load data
def load_data():
    if os.path.exists(DATA_FILE):
        data = pd.read_csv(DATA_FILE)
    else:
        data = pd.DataFrame({
            'Product Name': [
                '1캐릭터뱃지', '2커스터드푸딩뱃지', '3파파야푸딩뱃지', '4일반스티커', '5조각스티커',
                '6사각스티커', '7캐릭터키링', '8비즈키링', '9떡메모지', '10엽서',
                '11포스터', '12비즈반지', '12비즈반지-1', '12비즈반지-2', '엽서4종'
            ],
            'Total Quantity': [4, 2, 2, 55, 480, 432, 60, 21, 83, 848, 8, 6, 2, 1, 480],
            'Sold Quantity': [0] * 15,
            'Remaining Quantity': [4, 2, 2, 55, 480, 432, 60, 21, 83, 848, 8, 6, 2, 1, 480],
            'Price': [4000, 5000, 5000, 3000, 1000, 500, 4000, 7000, 2000, 1000, 4000, 4000, 3300, 5000, 3500],
        })
        # Calculate initial Revenue
        data['Revenue'] = data['Sold Quantity'] * data['Price']
        save_data(data)  # Save initial data
    return data

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_sales_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    else:
        sales_history = pd.DataFrame(columns=['Timestamp', 'Product Name', 'Quantity Sold', 'Revenue'])
        sales_history.to_csv(HISTORY_FILE, index=False)
        return sales_history

def save_sales_history(df):
    df.to_csv(HISTORY_FILE, index=False)

# Main application
def initialize_session_state():
    if 'data' not in st.session_state:
        st.session_state['data'] = load_data()
    if 'sales_history' not in st.session_state:
        st.session_state['sales_history'] = load_sales_history()

initialize_session_state()
data = st.session_state['data']
sales_history = st.session_state['sales_history']

# Tabs for main application
tabs = st.tabs(["Sales Tracking", "Data Modification"])

# Sales Tracking Tab
with tabs[0]:
    st.title('Sales Tracking and Update Application')

    # Input form for updating sales
    st.header('Update Sales')
    if 'selected_products' not in st.session_state:
        st.session_state['selected_products'] = []

    selected_products = st.multiselect(
        'Select Products', 
        data['Product Name'], 
        default=st.session_state['selected_products']
    )
    
    sold_quantities = {}
    for product in selected_products:
        sold_quantities[product] = st.number_input(
            f'{product}', min_value=0, step=1, key=f"sales_{product}"
        )

    # Display total revenue for selected products
    if selected_products:
        total_sale_revenue = sum(
            sold_quantities[product] * data[data['Product Name'] == product]['Price'].values[0]
            for product in selected_products
        )
        st.write(f"Total Revenue for Selected Products: {total_sale_revenue} ₩")

    if st.button('Submit Sale'):
        for product, quantity in sold_quantities.items():
            product_index = data[data['Product Name'] == product].index[0]
            if quantity <= data.at[product_index, 'Remaining Quantity']:
                data.at[product_index, 'Sold Quantity'] += quantity
                data.at[product_index, 'Remaining Quantity'] -= quantity

                # Update Revenue dynamically based on Sold Quantity and Price
                data.at[product_index, 'Revenue'] = data.at[product_index, 'Sold Quantity'] * data.at[product_index, 'Price']

                # Log the sale
                new_sale = {
                    'Timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Product Name': product,
                    'Quantity Sold': quantity,
                    'Revenue': quantity * data.at[product_index, 'Price']
                }
                sales_history = pd.concat([sales_history, pd.DataFrame([new_sale])], ignore_index=True)

        # Save updates to files
        save_data(data)
        save_sales_history(sales_history)

        # Reload data from CSV
        st.session_state['data'] = load_data()
        st.session_state['sales_history'] = load_sales_history()

        # Clear selected products after submission
        st.session_state['selected_products'] = []
        st.success("Sales recorded successfully and data reloaded!")

    # Display updated data
    st.dataframe(st.session_state['data'])

    # Display sales history
    st.header('Sales History')
    st.dataframe(st.session_state['sales_history'])

    # Download updated data as Excel
    st.header('Download Updated Data')
    if st.button('Download Excel'):
        file_path = save_to_excel(st.session_state['data'])
        with open(file_path, 'rb') as f:
            st.download_button('Download Excel File', f, file_name=file_path)

    # Final totals
    st.header('Summary')
    total_revenue = st.session_state['data']['Revenue'].sum()
    st.write(f"Total Revenue: {total_revenue} ₩")

# Data Modification Tab
with tabs[1]:
    st.title('Data Modification')

    st.write("Modify the data below. Adjust values and click 'Save Changes' to apply updates.")

    # Use shared session state for data editing
    editable_data = st.session_state['data']

    # Display the editable data table
    for idx, row in editable_data.iterrows():
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            editable_data.at[idx, 'Product Name'] = st.text_input(
                f'Product Name {idx}', row['Product Name'], key=f'product_name_{idx}')
        with col2:
            editable_data.at[idx, 'Total Quantity'] = st.number_input(
                f'Total Quantity {idx}', value=row['Total Quantity'], min_value=0, key=f'total_quantity_{idx}')
        with col3:
            editable_data.at[idx, 'Sold Quantity'] = st.number_input(
                f'Sold Quantity {idx}', value=row['Sold Quantity'], min_value=0, key=f'sold_quantity_{idx}')
        with col4:
            editable_data.at[idx, 'Remaining Quantity'] = st.number_input(
                f'Remaining Quantity {idx}', value=row['Remaining Quantity'], min_value=0, key=f'remaining_quantity_{idx}')
        with col5:
            editable_data.at[idx, 'Price'] = st.number_input(
                f'Price {idx}', value=row['Price'], min_value=0, key=f'price_{idx}')

    # Adding new row functionality
    st.header("Add New Row")
    new_product_name = st.text_input("New Product Name", key="new_product_name")
    new_total_quantity = st.number_input("New Total Quantity", min_value=0, step=1, key="new_total_quantity")
    new_sold_quantity = st.number_input("New Sold Quantity", min_value=0, step=1, key="new_sold_quantity")
    new_remaining_quantity = st.number_input("New Remaining Quantity", min_value=0, step=1, key="new_remaining_quantity")
    new_price = st.number_input("New Price", min_value=0, step=1, key="new_price")

    if st.button("Add New Row"):
        if new_product_name:
            # Append the new row to the shared DataFrame
            new_row = {
                "Product Name": new_product_name,
                "Total Quantity": new_total_quantity,
                "Sold Quantity": new_sold_quantity,
                "Remaining Quantity": new_remaining_quantity,
                "Price": new_price,
                "Revenue": new_sold_quantity * new_price
            }
            st.session_state['data'] = pd.concat([st.session_state['data'], pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state['data'])  # Save data after adding new row
            st.success("New row added successfully!")
        else:
            st.error("Please provide a valid product name.")

    if st.button('Save Changes'):
        # Dynamically update Revenue
        st.session_state['data']['Revenue'] = st.session_state['data']['Sold Quantity'] * st.session_state['data']['Price']
        save_data(st.session_state['data'])  # Save changes to file
        st.success("Data updated successfully!")

    # Display updated data
    st.dataframe(st.session_state['data'])
