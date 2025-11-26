import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Superstore Data Visualization", layout="wide")
st.title("Superstore Data Visualization")

# -----------------------------
# 1️⃣ Load Excel Data
# -----------------------------
BASE_URL = "https://raw.githubusercontent.com/sorcoffee/superstore_dashboard/main/data/"

order_df = pd.read_excel(f"{BASE_URL}superstore_order.xlsx")
stock_df = pd.read_excel(f"{BASE_URL}product_stock.xlsx")
customer_df = pd.read_excel(f"{BASE_URL}superstore_customer.xlsx")
product_df = pd.read_excel(f"{BASE_URL}superstore_product.xlsx")

for df in [order_df, stock_df, customer_df, product_df]:
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

for col in ['sales','profit','quantity','stock']:
    for df in [order_df, stock_df]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

# -----------------------------
# 2️⃣ Sidebar Filters
# -----------------------------
selected_regions = st.sidebar.multiselect(
    "Select Region", options=order_df['region'].dropna().unique(), default=order_df['region'].dropna().unique()
)
selected_segments = st.sidebar.multiselect(
    "Select Customer Segment", options=customer_df['segment'].dropna().unique(), default=customer_df['segment'].dropna().unique()
)

filtered_orders = order_df[order_df['region'].isin(selected_regions)]
filtered_customers = customer_df[customer_df['segment'].isin(selected_segments)]

# -----------------------------
# 3️⃣ Summary Metrics
# -----------------------------
total_sales = filtered_orders['sales'].sum()
total_profit = filtered_orders['profit'].sum()
total_quantity = filtered_orders['quantity'].sum()
average_sales = filtered_orders['sales'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Total Quantity", f"{total_quantity:,.0f}")
col4.metric("Average Sales", f"${average_sales:,.2f}")

# -----------------------------
# 4️⃣ Profit Category per Order (Donut)
# -----------------------------
filtered_orders['profit_category'] = filtered_orders['profit'].apply(
    lambda x: 'High' if x>100 else 'Medium' if x>=50 else 'Low'
)
profit_counts = filtered_orders['profit_category'].value_counts().reset_index()
profit_counts.columns = ['Category','Count']

fig1 = px.pie(profit_counts, names='Category', values='Count', title='Profit Category Distribution', hole=0.3)
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# 5️⃣ Order Size by Quantity (Bar)
# -----------------------------
filtered_orders['order_size'] = filtered_orders['quantity'].apply(lambda x: 'Large' if x>=10 else 'Small')
size_counts = filtered_orders['order_size'].value_counts().reset_index()
size_counts.columns = ['Order Size','Count']

fig2 = px.bar(size_counts, x='Order Size', y='Count', color='Order Size', text='Count', title='Order Size Distribution')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 6️⃣ Low Stock Products (Line Chart)
# -----------------------------
low_stock = stock_df[stock_df['stock'] < 50]
fig_low_stock = px.line(low_stock, x='product_name', y='stock', markers=True,
                        title='Low Stock Products (<50 units)')
st.plotly_chart(fig_low_stock, use_container_width=True)

# -----------------------------
# 7️⃣ Top Products by Sales (Bar)
# -----------------------------
top_products = filtered_orders.groupby('product_name')['sales'].sum().reset_index()
top_products = top_products.sort_values(by='sales', ascending=False).head(10)

fig3_bar = px.bar(top_products, x='product_name', y='sales', text='sales', title='Top 10 Products by Sales')
st.plotly_chart(fig3_bar, use_container_width=True)

# -----------------------------
# 8️⃣ Total Profit per Region 
# -----------------------------
profit_region = filtered_orders.groupby('region')['profit'].sum().reset_index()
fig4_bar = px.bar(profit_region, x='region', y='profit', text='profit', title='Total Profit per Region')
fig4_pie = px.pie(profit_region, names='region', values='profit', title='Profit Share by Region')

st.plotly_chart(fig4_bar, use_container_width=True)
st.plotly_chart(fig4_pie, use_container_width=True)

# -----------------------------
# 9️⃣ Top Customers by Average Sales
# -----------------------------
avg_sales_customer = filtered_orders.groupby(['customer_id','customer_name'])['sales'].mean().reset_index()
avg_sales_customer = avg_sales_customer.sort_values(by='sales', ascending=False).head(10)

fig5_bubble = px.scatter(avg_sales_customer, x='customer_name', y='sales', size='sales', color='sales',
                         color_continuous_scale='Viridis', title='Top Customers')
st.plotly_chart(fig5_bubble, use_container_width=True)
