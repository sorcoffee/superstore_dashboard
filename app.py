import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Superstore Dashboard", layout="wide")
st.title("Superstore Interactive Dashboard")

# -----------------------------
# 1️⃣ Load CSV Data langsung dari GitHub
# -----------------------------
BASE_URL = "https://raw.githubusercontent.com/sorcoffee/superstore_dashboard/main/data/"

order_df = pd.read_csv("data/superstore_order.csv")
customer_df = pd.read_csv("data/superstore_customer.csv")
stock_df = pd.read_csv("data/product_stock.csv")
product_df = pd.read_csv("data/superstore_product.csv")

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
regions = order_df['region'].dropna().unique()
selected_region = st.sidebar.multiselect("Select Region", regions, default=regions)

segments = customer_df['segment'].dropna().unique()
selected_segment = st.sidebar.multiselect("Select Customer Segment", segments, default=segments)

filtered_orders = order_df[order_df['region'].isin(selected_region)]
filtered_customers = customer_df[customer_df['segment'].isin(selected_segment)]

# -----------------------------
# 4️⃣ Summary Metrics
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
# 5️⃣ Profit Category per Order
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
# 6️⃣ Order Size by Quantity
# -----------------------------
def order_size(qty):
    if qty >= 10:
        return 'Large Order'
    else:
        return 'Small Order'

filtered_orders['order_size'] = filtered_orders['quantity'].apply(order_size)
size_counts = filtered_orders['order_size'].value_counts().reset_index()
size_counts.columns = ['Order Size','Count']

fig2 = px.bar(size_counts, x='Order Size', y='Count', text='Count', title='Order Size Distribution')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 7️⃣ Low Stock Products
# -----------------------------
low_stock = stock_df[stock_df['stock'] < 50]
st.subheader("Products Low Stock (<50)")
st.dataframe(low_stock)

# -----------------------------
# 8️⃣ Total Sales per Product
# -----------------------------
top_products = (filtered_orders.groupby('product_name')['sales']
                .sum()
                .reset_index()
                .sort_values(by='sales', ascending=False)
                .head(10))
fig3 = px.bar(top_products, x='product_name', y='sales', text='sales', title='Top 10 Products by Sales')
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# 9️⃣ Total Profit per Region
# -----------------------------
profit_region = (filtered_orders.groupby('region')['profit']
                 .sum()
                 .reset_index()
                 .sort_values(by='profit', ascending=False))
fig4 = px.bar(profit_region, x='region', y='profit', text='profit', title='Total Profit per Region')
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# 10️⃣ Average Sales per Customer
# -----------------------------
avg_sales_customer = (filtered_orders.groupby(['customer_id','customer_name'])['sales']
                      .mean()
                      .reset_index()
                      .sort_values(by='sales', ascending=False)
                      .head(10))
fig5 = px.bar(avg_sales_customer, x='customer_name', y='sales', text='sales', title='Top 10 Customers by Average Sales')
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# 11️⃣ Aggregate + Condition + Filter (Region West)
# -----------------------------
west_orders = filtered_orders[filtered_orders['region'] == 'West']
agg_west = (west_orders.groupby(['product_id','product_name'])
            .agg(total_quantity=('quantity','sum'),
                 total_sales=('sales','sum'),
                 total_profit=('profit','sum'))
            .reset_index())
agg_west['profit_category'] = agg_west['total_profit'].apply(lambda x: 'High Profit' if x > 1000 else 'Low/Medium Profit')

st.subheader("Region West: Product Aggregates")
st.dataframe(agg_west)
