from typing import Tuple, List
import csv, io
from pypdf import PdfReader

def parse_uploaded(filename: str, content: bytes) -> Tuple[str, str]:
    name = (filename or '').lower()
    if name.endswith('.txt'):
        return ('text', content.decode('utf-8', errors='ignore')[:10000])
    if name.endswith('.csv'):
        try:
            sample = content.decode('utf-8', errors='ignore')
            rows = list(csv.reader(io.StringIO(sample)))
            head = rows[0] if rows else []
            preview = rows[1:6] if len(rows) > 1 else []
            head_line = ', '.join(head)
            preview_lines = [' | '.join(r) for r in preview]
            text = "CSV headers: " + head_line + "\nPreview:\n" + "\n".join(preview_lines)
            return ('csv', text[:10000])
        except Exception:
            return ('csv', 'Could not parse CSV (encoding/format issue).')
    if name.endswith('.pdf'):
        try:
            reader = PdfReader(io.BytesIO(content))
            txt = []
            for i, page in enumerate(reader.pages[:10]):  # cap pages
                try:
                    txt.append(page.extract_text() or '')
                except Exception:
                    continue
            return ('pdf', '\n'.join(txt)[:12000])
        except Exception:
            return ('pdf', 'Could not parse PDF.')
    # fallback: treat as binary blob summary
    return ('file', f'Uploaded file {filename} ({len(content)} bytes).')
