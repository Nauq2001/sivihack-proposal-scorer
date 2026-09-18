from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .analyst import analyze_rfp, create_gemini_analysis_model
from .criteria import create_gemini_resolution_model
from .models import CriteriaStateSnapshot, RFPAnalysis, ScoringInput, UserCriterionInput
from .service import CriteriaState
from .validation import validate_analysis


def _read(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"EMPTY_FILE: {path}")
    return text


def _load_state(path: str) -> CriteriaState:
    snapshot = CriteriaStateSnapshot.model_validate_json(_read(path))
    return CriteriaState.from_snapshot(snapshot)


def _write(path: str, payload: str, overwrite: bool) -> None:
    output = Path(path)
    if output.exists() and not overwrite:
        raise FileExistsError(f"OUTPUT_EXISTS: {path}; pass --overwrite to replace it")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload + "\n", encoding="utf-8")


def _resolver(offline: bool, model_name: str):
    return None if offline else create_gemini_resolution_model(model_name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rfp-analyst")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze an RFP with Gemini")
    analyze.add_argument("--rfp", required=True)
    analyze.add_argument("--output", required=True)
    analyze.add_argument("--model", default=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
    analyze.add_argument("--overwrite", action="store_true")

    validate = sub.add_parser("validate", help="Validate an RFPAnalysis JSON file")
    validate.add_argument("--analysis", required=True)
    validate.add_argument("--rfp", required=True)

    start = sub.add_parser("start-review", help="Create editable review state")
    start.add_argument("--analysis", required=True)
    start.add_argument("--rfp", required=True)
    start.add_argument("--output", required=True)
    start.add_argument("--overwrite", action="store_true")

    for command in ("add-criterion", "edit-criterion"):
        item = sub.add_parser(command)
        item.add_argument("--state", required=True)
        if command == "edit-criterion":
            item.add_argument("--current-name", required=True)
        item.add_argument("--name", required=True)
        item.add_argument("--description", required=True)
        item.add_argument("--weight", type=float)
        item.add_argument("--output", required=True)
        item.add_argument("--model", default=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
        item.add_argument("--offline", action="store_true", help="Use safe fallback without an AI call")
        item.add_argument("--overwrite", action="store_true")

    remove = sub.add_parser("remove-criterion")
    remove.add_argument("--state", required=True)
    remove.add_argument("--name", required=True)
    remove.add_argument("--output", required=True)
    remove.add_argument("--overwrite", action="store_true")

    package = sub.add_parser("package", help="Create ScoringInput JSON")
    package.add_argument("--state", required=True)
    package.add_argument("--proposal", required=True)
    package.add_argument("--output", required=True)
    package.add_argument("--overwrite", action="store_true")

    schema = sub.add_parser("schema", help="Export the ScoringInput JSON Schema")
    schema.add_argument("--output", required=True)
    schema.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "analyze":
            raw_rfp = _read(args.rfp)
            result = analyze_rfp(raw_rfp, create_gemini_analysis_model(args.model))
            _write(args.output, result.model_dump_json(indent=2), args.overwrite)
            print(f"ANALYZED: {len(result.requirements)} requirements -> {args.output}")
        elif args.command == "validate":
            analysis = RFPAnalysis.model_validate_json(_read(args.analysis))
            validate_analysis(analysis, _read(args.rfp))
            print("VALID")
        elif args.command == "start-review":
            analysis = RFPAnalysis.model_validate_json(_read(args.analysis))
            state = CriteriaState.from_analysis(analysis, _read(args.rfp))
            _write(args.output, state.to_snapshot().model_dump_json(indent=2), args.overwrite)
            print(f"REVIEW_STATE: {args.output}")
        elif args.command in {"add-criterion", "edit-criterion"}:
            state = _load_state(args.state)
            user_input = UserCriterionInput(
                name=args.name,
                description=args.description,
                weight=args.weight,
            )
            resolver = _resolver(args.offline, args.model)
            if args.command == "add-criterion":
                result = state.add_or_merge(user_input, resolver)
            else:
                result = state.edit(args.current_name, user_input, resolver)
            _write(args.output, state.to_snapshot().model_dump_json(indent=2), args.overwrite)
            action = "MERGED" if result.is_duplicate else "SAVED"
            print(f"{action}: {result.criterion.name} weight={result.criterion.weight:g}")
        elif args.command == "remove-criterion":
            state = _load_state(args.state)
            state.remove(args.name)
            _write(args.output, state.to_snapshot().model_dump_json(indent=2), args.overwrite)
            print(f"REMOVED: {args.name}")
        elif args.command == "package":
            state = _load_state(args.state)
            scoring_input = state.package(_read(args.proposal))
            _write(args.output, scoring_input.model_dump_json(indent=2), args.overwrite)
            print(f"PACKAGED: {args.output}")
        elif args.command == "schema":
            schema = ScoringInput.model_json_schema()
            schema["title"] = "ScoringInput"
            _write(args.output, json.dumps(schema, ensure_ascii=False, indent=2), args.overwrite)
            print(f"SCHEMA: {args.output}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
