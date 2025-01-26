import streamlit as st
import pandas as pd
import datetime

# Initialize or load data
def load_data():
    # Replace this with actual data loading logic if needed
    data = pd.DataFrame({
        'Product Name': [
            '1캐릭터뱃지', '2커스터드푸딩뱃지', '3파파야푸딩뱃지', '4일반스티커', '5조각스티커',
            '6사각스티커', '7캐릭터키링', '8비즈키링', '9떡메모지', '10엽서',
            '11포스터', '12비즈반지', '12비즈반지-1', '12비즈반지-2','엽서4종'
        ],
        'Total Quantity': [4, 2, 2, 55, 480, 432, 60, 21, 83, 848, 8, 6, 2, 1,480],
        'Sold Quantity': [0] * 15,
        'Remaining Quantity': [4, 2, 2, 55, 480, 432, 60, 21, 83, 848, 8, 6, 2, 1,480],
        'Price': [4000, 5000, 5000, 3000, 1000, 500, 4000, 7000, 2000, 1000, 4000, 4000, 3300, 5000, 3500],
        'Revenue': [0] * 15
    })
    return data

# Save data as an Excel file
def save_to_excel(df):
    file_name = f"sales_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(file_name, index=False)
    return file_name

# Main application
# Use session state to persist data
def initialize_session_state():
    if 'data' not in st.session_state:
        st.session_state['data'] = load_data()
    if 'sales_history' not in st.session_state:
        st.session_state['sales_history'] = pd.DataFrame(columns=['Timestamp', 'Product Name', 'Quantity Sold', 'Revenue'])

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
    selected_products = st.multiselect('Select Products', data['Product Name'])
    sold_quantities = {}
    for product in selected_products:
        sold_quantities[product] = st.number_input(f'{product}', min_value=0, step=1, key=f"sales_{product}")

    # Display total revenue for selected products
    if selected_products:
        total_sale_revenue = sum(sold_quantities[product] * data[data['Product Name'] == product]['Price'].values[0] for product in selected_products)
        st.write(f"Total Revenue for Selected Products: {total_sale_revenue} ₩")

    if st.button('Submit Sale'):
        for product, quantity in sold_quantities.items():
            product_index = data[data['Product Name'] == product].index[0]
            if quantity <= data.at[product_index, 'Remaining Quantity']:
                data.at[product_index, 'Sold Quantity'] += quantity
                data.at[product_index, 'Remaining Quantity'] -= quantity

                # Update Revenue dynamically
                data.at[product_index, 'Revenue'] = data.at[product_index, 'Sold Quantity'] * data.at[product_index, 'Price']
                

                # Log the sale
                new_sale = {
                    'Timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Product Name': product,
                    'Quantity Sold': quantity,
                    'Revenue': quantity * data.at[product_index, 'Price']
                }
                sales_history = pd.concat([sales_history, pd.DataFrame([new_sale])], ignore_index=True)

        st.session_state['data'] = data
        st.session_state['sales_history'] = sales_history
        st.success("Sales recorded successfully!")

    # Display updated data
    st.dataframe(data)

    # Display sales history
    st.header('Sales History')
    st.dataframe(sales_history)

    # Download updated data as Excel
    st.header('Download Updated Data')
    if st.button('Download Excel'):
        file_path = save_to_excel(data)
        with open(file_path, 'rb') as f:
            st.download_button('Download Excel File', f, file_name=file_path)

    # Final totals
    st.header('Summary')
    total_revenue = data['Revenue'].sum()
    st.write(f"Total Revenue: {total_revenue} ₩")

# Data Modification Tab
# Data Modification Tab
with tabs[1]:
    st.title('Data Modification')

    st.write("Modify the data below. Adjust values and click 'Save Changes' to apply updates. You can also add new rows.")

    # Display the editable data table
    editable_data = data.copy()
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
            # Append the new row to the DataFrame
            new_row = {
                "Product Name": new_product_name,
                "Total Quantity": new_total_quantity,
                "Sold Quantity": new_sold_quantity,
                "Remaining Quantity": new_remaining_quantity,
                "Price": new_price,
                "Revenue": new_sold_quantity * new_price
            }
            editable_data = pd.concat([editable_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("New row added successfully!")
        else:
            st.error("Please provide a valid product name.")

    if st.button('Save Changes'):
        editable_data['Revenue'] = editable_data['Sold Quantity'] * editable_data['Price']  # Update revenue dynamically
        st.session_state['data'] = editable_data
        st.success("Data updated successfully!")
