# Azure Document Intelligence PDF Practice Task

## Goal

Create a small standalone Python practice script that sends a local insurance PDF directly to Azure Document Intelligence, without Azure Blob Storage, Temporal, database, or project-specific infrastructure.

The script should:

1. Read a local PDF file from disk.
2. Send the PDF bytes directly to Azure Document Intelligence using the Python SDK.
3. Use the `prebuilt-layout` model.
4. Request Markdown output.
5. Save the extracted Markdown to a `.md` file.
6. Save the full raw Azure result to a `.raw.json` file.
7. Print basic execution details such as output paths and page count.

---

## Requirements

Use Python.

Install dependencies:

```bash
pip install azure-ai-documentintelligence python-dotenv
```

---

## Environment Variables

Create a `.env` file in the same directory as the script:

```env
DOCUMENTINTELLIGENCE_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
DOCUMENTINTELLIGENCE_API_KEY=<your-key>
```

Do not hardcode secrets in the Python script.

---

## Expected Input

The script should accept a local PDF path as a command-line argument.

Example:

```bash
python analyze_pdf.py ./documents/sample-insurance-policy.pdf
```

Optionally, it should accept an output directory as a second argument:

```bash
python analyze_pdf.py ./documents/sample-insurance-policy.pdf ./output
```

If no output directory is provided, default to:

```text
output/
```

---

## Expected Output

For an input PDF named:

```text
sample-insurance-policy.pdf
```

The script should create:

```text
output/sample-insurance-policy.md
output/sample-insurance-policy.raw.json
output/sample-insurance-policy.txt
```

The `.md` file should contain the Azure Markdown extraction.

The `.raw.json` file should contain the full serialized Azure response for debugging and inspection.

The `.txt` file can be a plain copy of `result.content` for convenience.

---

## Implementation File

Create a file named:

```text
analyze_pdf.py
```

Use this implementation:

```python
import base64
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    DocumentContentFormat,
)


def analyze_pdf(input_pdf_path: str, output_dir: str = "output") -> None:
    load_dotenv()

    endpoint = os.environ.get("DOCUMENTINTELLIGENCE_ENDPOINT")
    key = os.environ.get("DOCUMENTINTELLIGENCE_API_KEY")

    if not endpoint:
        raise RuntimeError("Missing DOCUMENTINTELLIGENCE_ENDPOINT in environment")

    if not key:
        raise RuntimeError("Missing DOCUMENTINTELLIGENCE_API_KEY in environment")

    input_path = Path(input_pdf_path)

    if not input_path.exists():
        raise FileNotFoundError(f"PDF not found: {input_path}")

    if input_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {input_path}")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    pdf_bytes = input_path.read_bytes()

    request = AnalyzeDocumentRequest(
        bytes_source=base64.b64encode(pdf_bytes)
    )

    poller = client.begin_analyze_document(
        model_id="prebuilt-layout",
        body=request,
        output_content_format=DocumentContentFormat.MARKDOWN,
    )

    result = poller.result()

    markdown_path = out_dir / f"{input_path.stem}.md"
    json_path = out_dir / f"{input_path.stem}.raw.json"
    text_path = out_dir / f"{input_path.stem}.txt"

    content = result.content or ""

    markdown_path.write_text(content, encoding="utf-8")
    text_path.write_text(content, encoding="utf-8")

    result_dict = result.as_dict()
    json_path.write_text(
        json.dumps(result_dict, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    page_count = len(result.pages) if result.pages else 0
    content_format = getattr(result, "content_format", None)

    print("Done")
    print(f"Markdown: {markdown_path}")
    print(f"Raw JSON: {json_path}")
    print(f"Text copy: {text_path}")
    print(f"Content format: {content_format}")
    print(f"Pages: {page_count}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_pdf.py path/to/document.pdf [output_dir]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"

    analyze_pdf(pdf_path, output_dir)
```

---

## How It Works

The script reads the local PDF into memory:

```python
pdf_bytes = input_path.read_bytes()
```

Then it sends those bytes directly to Azure Document Intelligence:

```python
request = AnalyzeDocumentRequest(
    bytes_source=base64.b64encode(pdf_bytes)
)
```

The script uses the `prebuilt-layout` model:

```python
model_id="prebuilt-layout"
```

It requests Markdown output:

```python
output_content_format=DocumentContentFormat.MARKDOWN
```

The extracted Markdown is available at:

```python
result.content
```

---

## Test Command

Run:

```bash
python analyze_pdf.py ./sample-insurance-policy.pdf
```

Expected terminal output:

```text
Done
Markdown: output/sample-insurance-policy.md
Raw JSON: output/sample-insurance-policy.raw.json
Text copy: output/sample-insurance-policy.txt
Content format: markdown
Pages: 3
```

The exact page count depends on the PDF.

---

## Notes

For this practice task, do not use:

- Azure Blob Storage
- Temporal
- A database
- FastAPI or NestJS
- Project-specific Valora/xproj code

This is only a standalone local experiment.

The simple flow is:

```text
local PDF
  -> Python SDK
  -> Azure Document Intelligence
  -> Markdown file
  -> raw JSON file
```

---

## Suggested Follow-up Experiment

After the Markdown output works, create a second script that reads the generated `.md` file and extracts insurance fields into a JSON shape like this:

```json
{
  "provider_name": null,
  "policy_number": null,
  "policy_type": null,
  "premium_amount": null,
  "currency": null,
  "billing_period": null,
  "deductible_amount": null,
  "valid_from": null,
  "valid_until": null,
  "coverage_summary": [],
  "exclusions": []
}
```

Keep that as a separate step. First confirm that PDF-to-Markdown works correctly.
