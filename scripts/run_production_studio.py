"""CLI Runner for Tales of Wonder Kids Production Studio.

Usage:
  python scripts/run_production_studio.py --theme "التعاون ومساعدة الأصدقاء" --pillar "الآداب والأخلاق"
  python scripts/run_production_studio.py --interactive
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from production_studio.orchestrator import StudioOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Tales of Wonder Multi-Agent Studio Runner")
    parser.add_argument("--theme", type=str, default="التعاون ومساعدة الأصدقاء في الروضة", help="Episode curriculum theme")
    parser.add_argument("--pillar", type=str, default="الآداب والأخلاق (Manners)", help="Pedagogical curriculum pillar")
    parser.add_argument("--upload", action="store_true", help="Automatically upload to YouTube as Private/Draft")

    args = parser.parse_args()

    orchestrator = StudioOrchestrator()
    orchestrator.produce_episode(
        theme=args.theme,
        pillar=args.pillar,
        upload_to_youtube=args.upload
    )

if __name__ == "__main__":
    main()
