import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Superstore Dashboard Advanced", layout="wide")
st.title("Superstore Interactive Dashboard - Advanced")

# -----------------------------
# 1️⃣ Load Excel Data dari GitHub
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
# 2️⃣ Sidebar Filters
# -----------------------------
selected_region = st.sidebar.multiselect("Select Region", order_df['region'].dropna().unique(), default=order_df['region'].dropna().unique())
selected_segment = st.sidebar.multiselect("Select Customer Segment", customer_df['segment'].dropna().unique(), default=customer_df['segment'].dropna().unique())

filtered_orders = order_df[order_df['region'].isin(selected_region)]
filtered_customers = customer_df[customer_df['segment'].isin(selected_segment)]

# -----------------------------
# 3️⃣ Summary Metrics
# -----------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${filtered_orders['sales'].sum():,.2f}")
col2.metric("Total Profit", f"${filtered_orders['profit'].sum():,.2f}")
col3.metric("Total Quantity", f"{filtered_orders['quantity'].sum():,.0f}")
col4.metric("Average Sales", f"${filtered_orders['sales'].mean():,.2f}")

# -----------------------------
# 4️⃣ Profit Category Distribution
# -----------------------------
def profit_category(p):
    if p > 100:
        return 'High Profit'
    elif 50 <= p <= 100:
        return 'Medium Profit'
    else:
        return 'Low Profit'

filtered_orders['profit_category'] = filtered_orders['profit'].apply(profit_category)
profit_counts = filtered_orders['profit_category'].value_counts().reset_index()
profit_counts.columns = ['Category','Count']

fig1 = px.pie(profit_counts, names='Category', values='Count', title='Profit Category Distribution')
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# 5️⃣ Order Size Distribution
# -----------------------------
def order_size(qty):
    return 'Large Order' if qty >= 10 else 'Small Order'

filtered_orders['order_size'] = filtered_orders['quantity'].apply(order_size)
size_counts = filtered_orders['order_size'].value_counts().reset_index()
size_counts.columns = ['Order Size','Count']

fig2 = px.bar(size_counts, x='Order Size', y='Count', text='Count', title='Order Size Distribution', color='Order Size')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 6️⃣ Low Stock Products → Line Chart
# -----------------------------
low_stock = stock_df[stock_df['stock'] < 50]
if not low_stock.empty:
    fig3 = px.line(low_stock.sort_values('stock'), x='product_name', y='stock', markers=True, title='Low Stock Products (<50)')
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# 7️⃣ Top 10 Products by Sales → Bar + Line (Trend)
# -----------------------------
top_products = (filtered_orders.groupby('product_name')['sales'].sum().reset_index().sort_values('sales', ascending=False).head(10))
fig4 = go.Figure()
fig4.add_trace(go.Bar(x=top_products['product_name'], y=top_products['sales'], name='Total Sales', marker_color='indianred'))
fig4.add_trace(go.Scatter(x=top_products['product_name'], y=top_products['sales'], mode='lines+markers', name='Trend', line=dict(color='blue')))
fig4.update_layout(title='Top 10 Products by Sales with Trend', xaxis_title='Product', yaxis_title='Sales')
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# 8️⃣ Sales vs Profit Scatter
# -----------------------------
fig5 = px.scatter(filtered_orders, x='sales', y='profit', color='profit_category', hover_data=['product_name', 'region'], title='Sales vs Profit per Order')
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# 9️⃣ Total Profit per Region → Treemap
# -----------------------------
profit_region = filtered_orders.groupby('region')['profit'].sum().reset_index()
fig6 = px.treemap(profit_region, path=['region'], values='profit', color='profit', title='Total Profit per Region')
st.plotly_chart(fig6, use_container_width=True)

# -----------------------------
# 🔟 Sales Trend of Top Products → Line Chart
# -----------------------------
top_product_names = top_products['product_name'].tolist()
trend_df = filtered_orders[filtered_orders['product_name'].isin(top_product_names)]
trend_df['order_date'] = pd.to_datetime(trend_df['order_date'])
trend_grouped = trend_df.groupby(['order_date','product_name'])['sales'].sum().reset_index()
fig7 = px.line(trend_grouped, x='order_date', y='sales', color='product_name', markers=True, title='Sales Trend of Top 10 Products')
st.plotly_chart(fig7, use_container_width=True)

# -----------------------------
# 11️⃣ Aggregate West Region Products → Area Chart
# -----------------------------
west_orders = filtered_orders[filtered_orders['region']=='West']
agg_west = west_orders.groupby('product_name').agg(total_quantity=('quantity','sum'), total_sales=('sales','sum')).reset_index()
fig8 = px.area(agg_west, x='product_name', y='total_sales', title='Region West: Sales by Product', markers=True)
st.plotly_chart(fig8, use_container_width=True)

# -----------------------------
# 12️⃣ Total Quantity per Product Category → Stacked Bar
# -----------------------------
if 'category' in order_df.columns:
    category_qty = filtered_orders.groupby(['category','product_name'])['quantity'].sum().reset_index()
    fig9 = px.bar(category_qty, x='category', y='quantity', color='product_name', title='Total Quantity per Product Category', barmode='stack')
    st.plotly_chart(fig9, use_container_width=True)
