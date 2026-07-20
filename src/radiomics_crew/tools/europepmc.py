"""Europe PMC: open-access full text, which is where the Methods section lives.

Abstracts almost never state the discretisation strategy or the PyRadiomics version.
Appraising reproducibility from abstracts alone is exactly the failure mode this tool avoids.
"""

from __future__ import annotations

import json

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ._http import cached_get, freeze

SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
FULLTEXT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{pmcid}/fullTextXML"

_METHODS_HINTS = ("method", "material", "acquisition", "segmentation", "feature", "statistic")


class EuropePMCInput(BaseModel):
    pmid: str = Field(description="A single PubMed ID")
    section: str = Field(default="methods", description="'methods' (default) or 'all'")


class EuropePMCFullTextTool(BaseTool):
    name: str = "europepmc_full_text"
    description: str = (
        "Retrieve the open-access full text of a paper from its PMID, defaulting to the Methods section. "
        "Returns 'NOT_OPEN_ACCESS' if the full text is not available — in that case, say so in the evidence "
        "table instead of guessing the methodology."
    )
    args_schema: type[BaseModel] = EuropePMCInput

    def _run(self, pmid: str, section: str = "methods") -> str:
        pmid = pmid.strip()
        raw = cached_get(SEARCH, freeze({"query": f"EXT_ID:{pmid}", "format": "json", "resultType": "core"}))
        if raw.startswith("TOOL_ERROR"):
            return raw
        try:
            results = json.loads(raw)["resultList"]["result"]
        except (KeyError, ValueError):
            return "TOOL_ERROR: unexpected Europe PMC response."
        if not results:
            return f"NOT_FOUND: no Europe PMC record for PMID {pmid}."

        record = results[0]
        pmcid = record.get("pmcid")
        if not pmcid or record.get("isOpenAccess") != "Y":
            return (
                f"NOT_OPEN_ACCESS: PMID {pmid} ('{record.get('title', '?')}') has no open-access full text. "
                "Report methodology as 'not verifiable from abstract'."
            )

        xml = cached_get(FULLTEXT.format(source="PMC", pmcid=pmcid), freeze({}))
        if xml.startswith("TOOL_ERROR"):
            return xml

        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(xml)
        except ET.ParseError as exc:
            return f"TOOL_ERROR: malformed full-text XML ({exc})"

        chunks: list[str] = []
        for sec in root.findall(".//body//sec"):
            title = (sec.findtext("title") or "").strip()
            if section == "methods" and not any(h in title.lower() for h in _METHODS_HINTS):
                continue
            body = " ".join(" ".join(sec.itertext()).split())
            chunks.append(f"## {title or '(untitled section)'}\n{body}")

        if not chunks:
            return f"NOT_FOUND: no matching '{section}' section in {pmcid}. Retry with section='all'."
        text = "\n\n".join(chunks)
        return text[:20000] + ("\n\n[TRUNCATED]" if len(text) > 20000 else "")
