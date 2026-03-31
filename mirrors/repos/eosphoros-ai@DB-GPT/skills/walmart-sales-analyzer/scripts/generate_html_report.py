import os
import shutil
import json
from generate_correlation_heatmap import generate_correlation_heatmap
from generate_sales_unemployment_scatter import generate_sales_unemployment_scatter
from generate_time_series_trend import generate_time_series_trend
from generate_store_avg_comparison import generate_store_avg_comparison

def generate_html_report(data_path, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate all plots into the output directory
    generate_correlation_heatmap(data_path, output_dir)
    generate_sales_unemployment_scatter(data_path, output_dir)
    generate_time_series_trend(data_path, output_dir)
    generate_store_avg_comparison(data_path, output_dir)

    images = [
        "correlation_heatmap.png",
        "sales_vs_unemployment_scatter.png",
        "time_series_trend.png",
        "store_avg_comparison.png"
    ]
    
    chunks = []
    for img in images:
        img_path = os.path.join(output_dir, img)
        if os.path.exists(img_path):
            chunks.append({
                "output_type": "image",
                "content": os.path.abspath(img_path)
            })
            
    # Read HTML template
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "report_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Save the final HTML report
    report_output_path = os.path.join(output_dir, "walmart_sales_report.html")
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    chunks.append({
        "output_type": "text",
        "content": f"HTML report and {len(images)} charts generated successfully."
    })
    
    print(json.dumps({"chunks": chunks}, ensure_ascii=False))

if __name__ == "__main__":
    import sys, json
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    data_path = args.get('input_file') or args.get('file_path') or args.get('data_path', 'Walmart_Sales.csv')
    out_dir = args.get('output_dir', os.environ.get('OUTPUT_DIR', '.'))
    generate_html_report(data_path, out_dir)
