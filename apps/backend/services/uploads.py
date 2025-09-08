from typing import Tuple, List
import csv, io
from pypdf import PdfReader

from packages.integrations.vercel_storage import upload_blob


def parse_uploaded(filename: str, content: bytes) -> Tuple[str, str, str]:
    """Parse uploaded file content and store the raw file in Vercel Blob."""

    name = (filename or '').lower()
    kind = 'file'
    summary = f'Uploaded file {filename} ({len(content)} bytes).'

    if name.endswith('.txt'):
        kind = 'text'
        summary = content.decode('utf-8', errors='ignore')[:10000]
    elif name.endswith('.csv'):
        try:
            sample = content.decode('utf-8', errors='ignore')
            rows = list(csv.reader(io.StringIO(sample)))
            head = rows[0] if rows else []
            preview = rows[1:6] if len(rows) > 1 else []
            head_line = ', '.join(head)
            preview_lines = [' | '.join(r) for r in preview]
            text = "CSV headers: " + head_line + "\nPreview:\n" + "\n".join(preview_lines)
            summary = text[:10000]
            kind = 'csv'
        except Exception:
            summary = 'Could not parse CSV (encoding/format issue).'
            kind = 'csv'
    elif name.endswith('.pdf'):
        try:
            reader = PdfReader(io.BytesIO(content))
            txt = []
            for i, page in enumerate(reader.pages[:10]):  # cap pages
                try:
                    txt.append(page.extract_text() or '')
                except Exception:
                    continue
            summary = '\n'.join(txt)[:12000]
            kind = 'pdf'
        except Exception:
            summary = 'Could not parse PDF.'
            kind = 'pdf'

    blob_url = upload_blob(filename, content)
    return (kind, summary, blob_url)
