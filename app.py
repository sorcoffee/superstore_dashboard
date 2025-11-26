import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Superstore Dashboard", layout="wide")
st.title("Superstore Pro Interactive Dashboard")

# -----------------------------
# 1️⃣ Load Excel Data dari GitHub
# -----------------------------
BASE_URL = "https://raw.githubusercontent.com/sorcoffee/superstore_dashboard/main/data/"

order_df = pd.read_excel(f"{BASE_URL}superstore_order.xlsx")
stock_df = pd.read_excel(f"{BASE_URL}product_stock.xlsx")
customer_df = pd.read_excel(f"{BASE_URL}superstore_customer.xlsx")
product_df = pd.read_excel(f"{BASE_URL}superstore_product.xlsx")

# Normalisasi kolom: lowercase + strip + replace spasi -> underscore
for df in [order_df, stock_df, customer_df, product_df]:
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# -----------------------------
# 2️⃣ Convert numeric columns
# -----------------------------
for col in ['sales','profit','quantity','stock']:
    for df in [order_df, stock_df]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

# -----------------------------
# 3️⃣ Sidebar Filters
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
# 4️⃣ Summary Metrics (Aggregate Function)
# -----------------------------
total_quantity = filtered_orders['quantity'].sum()
total_sales = filtered_orders['sales'].sum()
total_profit = filtered_orders['profit'].sum()
average_sales = filtered_orders['sales'].mean()
total_orders = len(filtered_orders)
earliest_order = filtered_orders['order_date'].min() if 'order_date' in filtered_orders.columns else 'N/A'
latest_order = filtered_orders['order_date'].max() if 'order_date' in filtered_orders.columns else 'N/A'

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Quantity", f"{total_quantity:,.0f}")
col2.metric("Total Sales", f"${total_sales:,.2f}")
col3.metric("Total Profit", f"${total_profit:,.2f}")
col4.metric("Average Sales", f"${average_sales:,.2f}")
col5.metric("Total Orders", f"{total_orders}")
col6.metric("Order Date Range", f"{earliest_order} - {latest_order}")

# -----------------------------
# 5️⃣ Profit Category per Order
# -----------------------------
def profit_category(p):
    if p > 100:
        return 'High Profit'
    elif 50 <= p <= 100:
        return 'Medium Profit'
    else:
        return 'Low Profit'

if 'profit' in filtered_orders.columns:
    filtered_orders['profit_category'] = filtered_orders['profit'].apply(profit_category)
    profit_counts = filtered_orders['profit_category'].value_counts().reset_index()
    profit_counts.columns = ['Category','Count']
    fig1 = px.pie(profit_counts, names='Category', values='Count', title='Profit Category Distribution')
    st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# 6️⃣ Order Size by Quantity
# -----------------------------
def order_size(qty):
    return 'Large Order' if qty >= 10 else 'Small Order'

if 'quantity' in filtered_orders.columns:
    filtered_orders['order_size'] = filtered_orders['quantity'].apply(order_size)
    size_counts = filtered_orders['order_size'].value_counts().reset_index()
    size_counts.columns = ['Order Size','Count']
    fig2 = px.bar(size_counts, x='Order Size', y='Count', text='Count', title='Order Size Distribution', color='Order Size')
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 7️⃣ Low Stock Products
# -----------------------------
if 'stock' in stock_df.columns:
    low_stock = stock_df[stock_df['stock'] < 50]
    st.subheader("Products Low Stock (<50)")
    st.dataframe(low_stock)

# -----------------------------
# 8️⃣ Total Sales per Product (Bar + Line)
# -----------------------------
if {'product_name','sales'}.issubset(filtered_orders.columns):
    top_products = (filtered_orders.groupby('product_name')['sales']
                    .sum().reset_index()
                    .sort_values(by='sales', ascending=False).head(10))
    fig3 = px.bar(top_products, x='product_name', y='sales', text='sales', title='Top 10 Products by Sales')
    fig3_line = px.line(top_products, x='product_name', y='sales', markers=True, title='Top 10 Products Sales Trend')
    st.plotly_chart(fig3, use_container_width=True)
    st.plotly_chart(fig3_line, use_container_width=True)

# -----------------------------
# 9️⃣ Total Profit per Region (Bar + Pie)
# -----------------------------
if {'region','profit'}.issubset(filtered_orders.columns):
    profit_region = filtered_orders.groupby('region')['profit'].sum().reset_index()
    fig4 = px.bar(profit_region, x='region', y='profit', text='profit', title='Total Profit per Region')
    fig4_pie = px.pie(profit_region, names='region', values='profit', title='Profit Share by Region')
    st.plotly_chart(fig4, use_container_width=True)
    st.plotly_chart(fig4_pie, use_container_width=True)

# -----------------------------
# 10️⃣ Average Sales per Customer
# -----------------------------
if {'customer_id','customer_name','sales'}.issubset(filtered_orders.columns):
    avg_sales_customer = filtered_orders.groupby(['customer_id','customer_name'])['sales'].mean().reset_index()
    avg_sales_customer = avg_sales_customer.sort_values(by='sales', ascending=False).head(10)
    fig5 = px.bar(avg_sales_customer, x='customer_name', y='sales', text='sales', title='Top 10 Customers by Average Sales')
    fig5_scatter = px.scatter(avg_sales_customer, x='customer_name', y='sales', size='sales', color='sales', title='Top Customers Scatter Sales')
    st.plotly_chart(fig5, use_container_width=True)
    st.plotly_chart(fig5_scatter, use_container_width=True)

# -----------------------------
# 11️⃣ Aggregate + Condition + Filter (Region West)
# -----------------------------
if {'region','product_id','product_name','quantity','sales','profit'}.issubset(filtered_orders.columns):
    west_orders = filtered_orders[filtered_orders['region'] == 'West']
    agg_west = west_orders.groupby(['product_id','product_name']).agg(
        total_quantity=('quantity','sum'),
        total_sales=('sales','sum'),
        total_profit=('profit','sum')
    ).reset_index()
    agg_west['profit_category'] = agg_west['total_profit'].apply(lambda x: 'High Profit' if x>1000 else 'Low/Medium Profit')
    st.subheader("Region West: Product Aggregates")
    st.dataframe(agg_west)
    # Tambah visualisasi
    fig_west = px.bar(agg_west, x='product_name', y='total_sales', color='profit_category', text='total_sales', title='Region West: Sales per Product')
    st.plotly_chart(fig_west, use_container_width=True)
