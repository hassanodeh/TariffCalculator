import os
import re
import pdfplumber
## Parse Pdf into a markdown
def parse_pdf() :
    pdf_path ='PortTariff.pdf'
    markdown_path='port_tariff.md'
    skip_pages=4
    raw_segments = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            if page_idx < skip_pages:
                continue
            w, h = page.width, page.height
            mid_x = w / 2
            for x0, x1 in ((0, mid_x), (mid_x, w)):
                col = page.crop((x0, 0, x1, h))
                text = col.extract_text()
                if text:
                    raw_segments.append(text)
                for table in col.extract_tables():
                    if not any(cell for row in table for cell in row):
                        continue
                    header, *rows = table
                    md_tbl = "| " + " | ".join(cell or "" for cell in header) + " |"
                    md_tbl += "\n| " + " | ".join("---" for _ in header) + " |"
                    for row in rows:
                        md_tbl += "\n| " + " | ".join(cell or "" for cell in row) + " |"
                    raw_segments.append(md_tbl)

    full_text = "\n\n".join(raw_segments)

    # Split only on numeric ALL-CAPS subsection headers
    split_rx = r'(?m)(?=^(?!0\.)\d+\.\d+\s+[A-Z0-9 ,\-–\/&()\'"\. ]+$)'
    parts = re.split(split_rx, full_text)

    heading_rx = re.compile(r'^(?!0\.)\d+\.\d+\s+[A-Z0-9 ,\-–\/&()\'"\. ]+$')
    md_sections = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.splitlines()
        header = lines[0].strip()
        if heading_rx.match(header):
            md_sections.append(f"## {header}")
            body = "\n".join(lines[1:]).strip()
            if body:
                md_sections.append(body)

    # Write out the final Markdown to current directory
    output_dir = os.path.dirname(markdown_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(markdown_path, 'w', encoding='utf-8') as md_file:
        md_file.write("\n\n".join(md_sections))

    print(f" Parsed and saved {len(md_sections)//2} sections to {markdown_path}")

if __name__ == '__main__':
    

    parse_pdf()
