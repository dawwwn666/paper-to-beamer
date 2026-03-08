"""
render_pages.py — 将PDF页面渲染为高分辨率PNG（用于裁剪表格）
用法: python scripts/render_pages.py Papers/your_paper.pdf [dpi]
默认dpi=200
"""
import sys
import os

if len(sys.argv) < 2:
    print("用法: python scripts/render_pages.py Papers/your_paper.pdf [dpi]")
    sys.exit(1)

pdf_path = sys.argv[1]
dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 200

base = os.path.splitext(os.path.basename(pdf_path))[0]
out_dir = f"Figures/{base}_tables"
os.makedirs(out_dir, exist_ok=True)

# 优先用pdf2image，回退到subprocess调用pdftoppm
try:
    from pdf2image import convert_from_path
    pages = convert_from_path(pdf_path, dpi=dpi)
    for i, page in enumerate(pages):
        out = f"{out_dir}/page-{i+1}.png"
        page.save(out, "PNG")
        print(f"  已保存: {out}")
    print(f"共渲染 {len(pages)} 页")
except ImportError:
    import subprocess
    prefix = f"{out_dir}/page"
    result = subprocess.run(
        ["pdftoppm", "-r", str(dpi), "-png", pdf_path, prefix],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("错误: 需要安装 pdf2image 或 pdftoppm")
        print("  pip install pdf2image")
        print("  或安装 poppler (brew install poppler / apt install poppler-utils)")
        sys.exit(1)
    pages = [f for f in os.listdir(out_dir) if f.startswith("page") and f.endswith(".png")]
    print(f"共渲染 {len(pages)} 页，保存在 {out_dir}/")
