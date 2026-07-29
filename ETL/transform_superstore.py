from extraction_superstore import df
import pandas as pd
import numpy as np

#preparation Dim_Date
def dim_date_prep():
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y")

    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df['Order Date'].dt.month
    df["Day"] = df['Order Date'].dt.day
    df["Trimestre"] = ((df["Month"] - 1) // 3 + 1)
    df_date = (df[["Order Date", "Year", "Month", "Day", "Trimestre"]].drop_duplicates(subset=["Order Date"]).sort_values("Order Date"))
    return df_date

df_date = dim_date_prep()

def dim_customer_prep():
    df_customer = (df[["Customer ID", "Customer Name", "Segment"]].drop_duplicates(subset=["Customer ID"]).sort_values("Customer ID"))
    return df_customer

df_customer = dim_customer_prep()


def dim_product_prep():
    df_product = (df[["Product ID", "Product Name", "Category", "Sub-Category"]].drop_duplicates(subset=["Product ID"]).sort_values("Product ID"))
    return df_product
df_product = dim_product_prep()


def dim_shipping_prep():
    df_shipping = (df[["Ship Mode"]].drop_duplicates())
    return df_shipping
df_shipping = dim_shipping_prep()

def dim_location_prep():
    df_location = (df[["Country", "State", "City", "Region", "Postal Code"]].drop_duplicates())
    return df_location
df_location = dim_location_prep()
print(df_shipping.dtypes)
def fait_sales_prep():
    df_sales = (df[["Order ID", "Sales", "Quantity", "Discount", "Profit", "Product ID", "Customer ID", "Order Date", "Ship Mode", "Country", "State", "City", "Region", "Postal Code"]].drop_duplicates())
    return df_sales
df_sales = fait_sales_prep()
