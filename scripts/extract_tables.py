"""
extract_tables.py — 用pdfplumber提取PDF中的表格坐标和内容
用法:
  python scripts/extract_tables.py Papers/your_paper.pdf
  python scripts/extract_tables.py Papers/your_paper.pdf --text-only
"""
import pdfplumber
import json
import sys
import os

if len(sys.argv) < 2:
    print("用法: python scripts/extract_tables.py Papers/your_paper.pdf [--text-only]")
    sys.exit(1)

pdf_path = sys.argv[1]
text_only = "--text-only" in sys.argv
if not os.path.exists(pdf_path):
    print(f"文件不存在: {pdf_path}")
    sys.exit(1)

base = os.path.splitext(os.path.basename(pdf_path))[0]
out_dir = f"Figures/{base}_tables"
os.makedirs(out_dir, exist_ok=True)

results = []
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.find_tables()
        for j, table in enumerate(tables):
            bbox = table.bbox  # (x0, y0, x1, y1)
            data = table.extract()

            entry = {
                "page": i + 1,
                "table_index": j,
                "bbox": list(bbox),
                "rows": len(data) if data else 0,
                "cols": len(data[0]) if data and data[0] else 0,
            }

            if text_only:
                entry["data"] = data  # 完整表格数据
            else:
                entry["preview"] = data[:3] if data else []  # 仅预览

            results.append(entry)

out_file = f"{out_dir}/tables_text.json" if text_only else f"{out_dir}/tables.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"找到 {len(results)} 个表格，已保存到 {out_file}")
for r in results:
    print(f"  第{r['page']}页 表格{r['table_index']}: {r['rows']}行×{r['cols']}列  bbox={r['bbox']}")
