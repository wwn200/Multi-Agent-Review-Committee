import argparse

from src.evaluation.rubric_importer import RubricImporter
from src.evaluation.rubric_loader import RubricLoader


def main():
    parser = argparse.ArgumentParser(
        description="Evaluation Agent"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # --------------------------------------------------
    # import-rubric command
    # --------------------------------------------------

    import_parser = subparsers.add_parser(
        "import-rubric",
        help="Import an evaluation rubric from an XLSX file.",
    )

    import_parser.add_argument(
        "file",
        help="Path to the XLSX rubric file.",
    )

    # --------------------------------------------------
    # Parse arguments
    # --------------------------------------------------

    args = parser.parse_args()

    # --------------------------------------------------
    # Execute command
    # --------------------------------------------------

    if args.command == "import-rubric":

        importer = RubricImporter()

        output_path = importer.import_rubric(
            args.file
        )

        print(
            f"Rubric imported to: {output_path}"
        )

        loader = RubricLoader()

        print(loader.list_rubrics())

        print(loader.load(args.file))



if __name__ == "__main__":
    main()