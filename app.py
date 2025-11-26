import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Superstore Dashboard", layout="wide")
st.title("Superstore Interactive Dashboard")

# -----------------------------
# Load Excel Data dari GitHub
# -----------------------------
BASE_URL = "https://raw.githubusercontent.com/sorcoffee/superstore_dashboard/main/data/"

order_df = pd.read_excel(f"{BASE_URL}superstore_order.xlsx")
stock_df = pd.read_excel(f"{BASE_URL}product_stock.xlsx")
customer_df = pd.read_excel(f"{BASE_URL}superstore_customer.xlsx")
product_df = pd.read_excel(f"{BASE_URL}superstore_product.xlsx")

# Normalisasi nama kolom
for df in [order_df, stock_df, customer_df, product_df]:
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Convert numeric columns
for col in ['sales','profit','quantity','stock']:
    for df in [order_df, stock_df]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

# -----------------------------
# Sidebar Filters
# -----------------------------
selected_region = st.sidebar.multiselect("Select Region",
                                         order_df['region'].dropna().unique(),
                                         default=order_df['region'].dropna().unique())
selected_segment = st.sidebar.multiselect("Select Customer Segment",
                                          customer_df['segment'].dropna().unique(),
                                          default=customer_df['segment'].dropna().unique())

filtered_orders = order_df[order_df['region'].isin(selected_region)]
filtered_customers = customer_df[customer_df['segment'].isin(selected_segment)]

# -----------------------------
# Summary Metrics
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
# Profit Category per Order → Pie
# -----------------------------
def profit_category(profit):
    if profit > 100:
        return 'High Profit'
    elif 50 <= profit <= 100:
        return 'Medium Profit'
    else:
        return 'Low Profit'

filtered_orders['profit_category'] = filtered_orders['profit'].apply(profit_category)
profit_counts = filtered_orders['profit_category'].value_counts().reset_index()
profit_counts.columns = ['Category','Count']

fig1 = px.pie(profit_counts, names='Category', values='Count', title='Profit Category Distribution')
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# Order Size → Bar
# -----------------------------
def order_size(qty):
    return 'Large Order' if qty >= 10 else 'Small Order'

filtered_orders['order_size'] = filtered_orders['quantity'].apply(order_size)
size_counts = filtered_orders['order_size'].value_counts().reset_index()
size_counts.columns = ['Order Size','Count']

fig2 = px.bar(size_counts, x='Order Size', y='Count', text='Count', title='Order Size Distribution')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Top Customers → Bubble Chart
# -----------------------------
avg_sales_customer = (filtered_orders.groupby(['customer_id','customer_name'])['sales']
                      .mean()
                      .reset_index()
                      .sort_values(by='sales', ascending=False)
                      .head(15))
fig3 = px.scatter(avg_sales_customer, x='customer_name', y='sales',
                  size='sales', color='sales',
                  title='Top Customers by Avg Sales', size_max=60)
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Total Sales Over Time → Line Chart
# -----------------------------
if 'order_date' in filtered_orders.columns:
    filtered_orders['order_date'] = pd.to_datetime(filtered_orders['order_date'], errors='coerce')
    sales_over_time = filtered_orders.groupby('order_date')['sales'].sum().reset_index()
    fig4 = px.line(sales_over_time, x='order_date', y='sales', title='Total Sales Over Time')
    st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# Sales vs Profit → Scatter
# -----------------------------
fig5 = px.scatter(filtered_orders, x='sales', y='profit',
                  hover_data=['product_name', 'order_id'],
                  title='Sales vs Profit per Order')
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# Region Profit Treemap
# -----------------------------
profit_region = filtered_orders.groupby(['region','product_name'])['profit'].sum().reset_index()
fig6 = px.treemap(profit_region, path=['region','product_name'], values='profit',
                  color='profit', title='Profit Distribution per Region & Product')
st.plotly_chart(fig6, use_container_width=True)

# -----------------------------
# Low Stock → Heatmap Table
# -----------------------------
low_stock = stock_df[stock_df['stock'] < 50]
st.subheader("Products Low Stock (<50)")
st.dataframe(low_stock)
