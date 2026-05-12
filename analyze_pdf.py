"""Analyze a local PDF with Azure Document Intelligence and save the results."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentContentFormat
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv


def load_configuration() -> tuple[str, str]:
    """Load Azure Document Intelligence credentials from environment variables."""
    load_dotenv()

    endpoint = os.environ.get("DOCUMENTINTELLIGENCE_ENDPOINT")
    api_key = os.environ.get("DOCUMENTINTELLIGENCE_API_KEY")

    if not endpoint:
        raise RuntimeError("Missing DOCUMENTINTELLIGENCE_ENDPOINT in environment")

    if not api_key:
        raise RuntimeError("Missing DOCUMENTINTELLIGENCE_API_KEY in environment")

    return endpoint, api_key


def is_tls_verification_disabled() -> bool:
    """Return whether TLS certificate verification is disabled via environment."""
    raw_value = os.environ.get("DOCUMENTINTELLIGENCE_DISABLE_TLS_VERIFY", "")
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def validate_input_pdf(input_pdf_path: str) -> Path:
    """Validate the incoming PDF path and return it as a resolved Path object."""
    input_path = Path(input_pdf_path).expanduser().resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"PDF not found: {input_path}")

    if input_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {input_path}")

    return input_path


def create_client(endpoint: str, api_key: str) -> DocumentIntelligenceClient:
    """Create an Azure Document Intelligence client instance."""
    return DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
        connection_verify=not is_tls_verification_disabled(),
    )


def analyze_pdf(input_pdf_path: str, output_dir: str = "output") -> None:
    """Analyze a PDF with the prebuilt-layout model and save Markdown, text, and raw JSON outputs."""
    endpoint, api_key = load_configuration()
    input_path = validate_input_pdf(input_pdf_path)

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    client = create_client(endpoint=endpoint, api_key=api_key)
    with input_path.open("rb") as pdf_stream:
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout",
            body=pdf_stream,
            output_content_format=DocumentContentFormat.MARKDOWN,
        )
    result = poller.result()

    markdown_path = out_dir / f"{input_path.stem}.md"
    json_path = out_dir / f"{input_path.stem}.raw.json"
    text_path = out_dir / f"{input_path.stem}.txt"

    content = result.content or ""
    markdown_path.write_text(content, encoding="utf-8")
    text_path.write_text(content, encoding="utf-8")
    json_path.write_text(
        json.dumps(result.as_dict(), indent=2, ensure_ascii=False),
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
    print(f"TLS verify disabled: {is_tls_verification_disabled()}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the PDF analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze a local PDF with Azure Document Intelligence.",
    )
    parser.add_argument("pdf_path", help="Path to the local PDF file to analyze.")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="output",
        help="Directory where output files will be written. Defaults to ./output.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for command-line execution."""
    args = parse_args()
    analyze_pdf(input_pdf_path=args.pdf_path, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
