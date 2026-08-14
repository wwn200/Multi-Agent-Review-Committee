import argparse

from src.evaluation.rubric_importer import RubricImporter
from src.evaluation.rubric_loader import RubricLoader
from src.evaluation.assumption_importer import AssumptionImporter
from src.evaluation.assumption_loader import AssumptionLoader


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
    # evaluate-model command
    # --------------------------------------------------

    evaluate_parser = subparsers.add_parser(
        "evaluate-model",
        help="Evaluate a model.",
    )

    evaluate_parser.add_argument(
        "model_name",
        help="Name of the model to evaluate.",
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

    if args.command == "evaluate-model":
    
        importer = AssumptionImporter()
    
        output_path = importer.import_assumption(
            args.model_name
        )
    
        print(
            f"Rubric imported to: {output_path}"
        )
    
        loader = AssumptionLoader()
    
        print(loader.list_assumptions())
    
        print(loader.load(args.model_name))
    




if __name__ == "__main__":
    main()