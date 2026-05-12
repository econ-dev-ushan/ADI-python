# Azure Document Intelligence PDF Practice

Small standalone Python script for sending a local PDF directly to Azure Document Intelligence and saving the results locally.

## What it does

- reads a local PDF file
- sends it to Azure Document Intelligence using the `prebuilt-layout` model
- requests Markdown output
- saves:
  - Markdown output
  - plain text copy
  - raw Azure JSON response
  - detected languages JSON

## Requirements

- Python 3.10+
- Azure Document Intelligence resource

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Recommended Setup

Using a virtual environment is recommended:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## Environment Variables

Create a `.env` file in the project root:

```env
DOCUMENTINTELLIGENCE_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
DOCUMENTINTELLIGENCE_API_KEY=<your-key>
```

Optional, for temporary local TLS troubleshooting only:

```env
DOCUMENTINTELLIGENCE_DISABLE_TLS_VERIFY=true
```

## Usage

Default output directory:

```powershell
python analyze_pdf.py .\sample-insurance-policy.pdf
```

Custom output directory:

```powershell
python analyze_pdf.py .\sample-insurance-policy.pdf .\output
```

## Output Files

For an input file named `sample-insurance-policy.pdf`, the script writes:

```text
output/sample-insurance-policy.md
output/sample-insurance-policy.txt
output/sample-insurance-policy.raw.json
output/sample-insurance-policy.languages.json
```

## Notes

- `.md` contains the Markdown returned by Azure
- `.txt` is a plain copy of `result.content`
- `.raw.json` contains the full Azure response
- `.languages.json` contains detected language entries from `result.languages`
