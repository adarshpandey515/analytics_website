from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
import matplotlib.pyplot as plt
import time

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
IMG_FOLDER = os.path.join(os.getcwd(), 'static', 'img')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMG_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMG_FOLDER'] = IMG_FOLDER

def generate_graphs(df):
    # Remove old images
    for file in os.listdir(IMG_FOLDER):
        os.remove(os.path.join(IMG_FOLDER, file))

    # Generate visualizations
    graphs = []
    timestamp = int(time.time())  # Unique timestamp for filenames

    # Debug: Check for required columns
    required_columns = ['Location', 'Total Sale', 'Product', 'Date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Missing columns: {missing_columns}")
        return graphs  # Skip graph generation if columns are missing

    # 1. Bar plot: Total sales by location
    if 'Total Sale' in df.columns and 'Location' in df.columns:
        plt.figure(figsize=(10, 6))
        sales_by_location = df.groupby('Location')['Total Sale'].sum().sort_values()
        sales_by_location.plot(kind='bar', title='Total Sales by Location')
        plt.ylabel('Sales')
        bar_location_path = os.path.join(IMG_FOLDER, f'sales_by_location_{timestamp}.png')
        plt.savefig(bar_location_path)
        graphs.append(bar_location_path)
        plt.close()

    # 2. Pie chart: Percentage of sales by location
    if 'Location' in df.columns and 'Total Sale' in df.columns:
        plt.figure(figsize=(8, 8))
        sales_by_location.plot.pie(title='Percentage of Sales by Location', autopct='%1.1f%%')
        pie_chart_path = os.path.join(IMG_FOLDER, f'sales_pie_chart_{timestamp}.png')
        plt.savefig(pie_chart_path)
        graphs.append(pie_chart_path)
        plt.close()

    # 3. Bar plot: Total sales by product
    if 'Product' in df.columns and 'Total Sale' in df.columns:
        plt.figure(figsize=(10, 6))
        sales_by_product = df.groupby('Product')['Total Sale'].sum().sort_values()
        sales_by_product.plot(kind='bar', title='Total Sales by Product')
        plt.ylabel('Sales')
        bar_product_path = os.path.join(IMG_FOLDER, f'sales_by_product_{timestamp}.png')
        plt.savefig(bar_product_path)
        graphs.append(bar_product_path)
        plt.close()

    # 4. Line plot: Trend of sales over time
    if 'Date' in df.columns and 'Total Sale' in df.columns:
        try:
            df['Date'] = pd.to_datetime(df['Date'])
            df.sort_values('Date', inplace=True)
            plt.figure(figsize=(10, 6))
            df.groupby('Date')['Total Sale'].sum().plot(kind='line', title='Sales Trend Over Time')
            plt.ylabel('Total Sales')
            sales_trend_path = os.path.join(IMG_FOLDER, f'sales_trend_{timestamp}.png')
            plt.savefig(sales_trend_path)
            graphs.append(sales_trend_path)
            plt.close()
        except Exception as e:
            print(f"Error generating line plot: {e}")

    # 5. Histogram: Distribution of total sales
    if 'Total Sale' in df.columns:
        plt.figure(figsize=(10, 6))
        df['Total Sale'].plot(kind='hist', bins=20, title='Distribution of Total Sales')
        plt.xlabel('Total Sales')
        histogram_path = os.path.join(IMG_FOLDER, f'sales_distribution_{timestamp}.png')
        plt.savefig(histogram_path)
        graphs.append(histogram_path)
        plt.close()

    # 6. Box plot: Sales by location
    if 'Total Sale' in df.columns and 'Location' in df.columns:
        plt.figure(figsize=(10, 6))
        df.boxplot(column='Total Sale', by='Location')
        plt.title('Box Plot of Sales by Location')
        plt.suptitle('')  # Remove default title
        boxplot_path = os.path.join(IMG_FOLDER, f'sales_boxplot_{timestamp}.png')
        plt.savefig(boxplot_path)
        graphs.append(boxplot_path)
        plt.close()

    # 7. Scatter plot: Sales vs Quantity
    if 'Total Sale' in df.columns and 'Quantity' in df.columns:
        plt.figure(figsize=(10, 6))
        df.plot.scatter(x='Quantity', y='Total Sale', title='Sales vs Quantity')
        scatter_path = os.path.join(IMG_FOLDER, f'sales_vs_quantity_{timestamp}.png')
        plt.savefig(scatter_path)
        graphs.append(scatter_path)
        plt.close()
    
  





# --- 8. Box plot: Distribution of sales by product ---
    if 'Total Sale' in df.columns and 'Product' in df.columns:
        plt.figure(figsize=(10, 6))
        df.boxplot(column='Total Sale', by='Product', grid=False)
        boxplot_path = os.path.join(IMG_FOLDER, f'distribution_of_sales_by_product_{timestamp}.png')
        plt.savefig(boxplot_path)
        graphs.append(boxplot_path)  # Append the graph path to the list
        plt.close()

    # --- 9. Pie chart: Sales by payment method ---
    if 'Payment Method' in df.columns and 'Total Sale' in df.columns:
        sales_by_payment_method = df.groupby('Payment Method')['Total Sale'].sum()
        plt.figure(figsize=(8, 8))
        sales_by_payment_method.plot(kind='pie', autopct='%1.1f%%', title='Sales by Payment Method')
        pie_path = os.path.join(IMG_FOLDER, f'sales_by_payment_method_{timestamp}.png')
        plt.savefig(pie_path)
        graphs.append(pie_path)  # Append the graph path to the list
        plt.close()



    return graphs


def generate_recommendations(df):
    recommendations = []

    # --- Restocking Recommendations ---
    if 'Total Sale' in df.columns and 'Product' in df.columns:
        # Popular product by sales
        sales_by_product = df.groupby('Product')['Total Sale'].sum().sort_values(ascending=False)
        most_popular_product = sales_by_product.head(1)
        recommendations.append(f"Most popular product: {most_popular_product.index[0]} (Sales: INR {most_popular_product.values[0]})\n"
                               f"-> Focus on maintaining inventory of {most_popular_product.index[0]} to avoid stockouts.")
        
        # Popular product size (if size is a column)
        if 'Size' in df.columns:
            sales_by_size = df.groupby('Size')['Total Sale'].sum().sort_values(ascending=False)
            most_popular_size = sales_by_size.head(1)
            recommendations.append(f"Most popular product size: {most_popular_size.index[0]} (Sales: INR {most_popular_size.values[0]})\n"
                                   f"-> Prioritize restocking {most_popular_size.index[0]} size.")

        # Seasonal sales peak (if sales are seasonal)
        if 'Date' in df.columns:
            df['Month'] = df['Date'].dt.month
            sales_by_month = df.groupby('Month')['Total Sale'].sum()
            peak_month = sales_by_month.idxmax()
            peak_sales = sales_by_month.max()
            recommendations.append(f"There's a peak in sales around month {peak_month} (Sales: INR {peak_sales})\n"
                                   f"-> Ensure adequate stock levels before this peak period.")

        # Highest sales by location
        if 'Location' in df.columns:
            sales_by_location = df.groupby('Location')['Total Sale'].sum().sort_values(ascending=False)
            top_location = sales_by_location.head(1)
            recommendations.append(f"Highest sales are from {top_location.index[0]} (Sales: INR {top_location.values[0]})\n"
                                   f"-> Increase regional stock or work with local distributors in {top_location.index[0]}.")

    # --- Customer Behavior Insights ---
    if 'Total Sale' in df.columns and 'Payment Method' in df.columns:
        # Most preferred payment method
        sales_by_payment_method = df.groupby('Payment Method')['Total Sale'].sum().sort_values(ascending=False)
        most_preferred_payment = sales_by_payment_method.head(1)
        recommendations.append(f"Most preferred payment method: {most_preferred_payment.index[0]} (Sales: INR {most_preferred_payment.values[0]})\n"
                               f"-> Encourage online payments or provide incentives (like small discounts) for online transactions.")
    
    # --- New Recommendations ---
    if 'Customer Age' in df.columns:
        # Popular age group of customers (if age data is available)
        sales_by_age_group = df.groupby('Customer Age')['Total Sale'].sum().sort_values(ascending=False)
        most_popular_age_group = sales_by_age_group.head(1)
        recommendations.append(f"Most popular customer age group: {most_popular_age_group.index[0]} (Sales: INR {most_popular_age_group.values[0]})\n"
                               f"-> Target marketing efforts to {most_popular_age_group.index[0]} age group.")

    if 'Product Category' in df.columns:
        # Highest sales by product category
        sales_by_category = df.groupby('Product Category')['Total Sale'].sum().sort_values(ascending=False)
        top_category = sales_by_category.head(1)
        recommendations.append(f"Highest sales are from the {top_category.index[0]} category (Sales: INR {top_category.values[0]})\n"
                               f"-> Focus on expanding the {top_category.index[0]} category or launch new products in this category.")

    if 'Discount' in df.columns:
        # Impact of discounts on sales
        sales_by_discount = df.groupby('Discount')['Total Sale'].sum().sort_values(ascending=False)
        most_effective_discount = sales_by_discount.head(1)
        recommendations.append(f"Most effective discount: {most_effective_discount.index[0]}% (Sales: INR {most_effective_discount.values[0]})\n"
                               f"-> Consider running promotions with a {most_effective_discount.index[0]}% discount to boost sales.")
        
    return recommendations

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        # Process CSV file
        if file and file.filename.endswith('.csv'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            try:
                df = pd.read_csv(file_path)

                # Debug: Show loaded dataframe
                print(f"Dataframe columns: {df.columns}")

                # Generate graphs
                images = generate_graphs(df)

                # Generate recommendations
                recommendations = generate_recommendations(df)

                return render_template(
                    'index.html',
                    img_folder='static/img',
                    images=[os.path.basename(img) for img in images],
                    recommendations=recommendations
                )
            except Exception as e:
                return f"An error occurred while processing the file: {e}"

    # Default page
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

