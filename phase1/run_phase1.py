from __future__ import annotations

import argparse
import os

from phase1.graph_builder.pipeline import run_pipeline
from phase1.config import DEFAULT_CONFIG, Phase1Config


def build_config_from_args() -> Phase1Config:
    parser = argparse.ArgumentParser(description="Phase 1 graph builder")
    parser.add_argument("--input", dest="input_csv", default=DEFAULT_CONFIG.input_csv)
    parser.add_argument("--output", dest="output_dir", default=DEFAULT_CONFIG.output_dir)
    args = parser.parse_args()

    return Phase1Config(
        input_csv=os.path.abspath(args.input_csv),
        output_dir=os.path.abspath(args.output_dir),
        id_columns=DEFAULT_CONFIG.id_columns,
    )


def main() -> None:
    config = build_config_from_args()
    run_pipeline(config)


if __name__ == "__main__":
    main()
