import argparse

from src.evaluation.rubric_importer import RubricImporter
from src.evaluation.rubric_loader import RubricLoader
from src.evaluation.assumption_importer import AssumptionImporter
from src.evaluation.assumption_loader import AssumptionLoader
from src.llm.client import LLMClient
from src.workflow.config import WorkflowConfigLoader
from src.workflow.workflow import EvaluationWorkflow


def _load_rubric(rubric_name: str) -> dict:
    """Load a rubric, importing its default XLSX source when needed."""
    loader = RubricLoader()

    try:
        return loader.load(rubric_name)
    except FileNotFoundError:
        RubricImporter().import_rubric(rubric_name)
        return loader.load(rubric_name)


def _load_model(model_name: str) -> dict:
    """Load a model, importing its default XLSX source when needed."""
    loader = AssumptionLoader()

    try:
        return loader.load(model_name)
    except FileNotFoundError:
        AssumptionImporter().import_assumption(model_name)
        return loader.load(model_name)


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
    # import-model command
    # --------------------------------------------------

    model_import_parser = subparsers.add_parser(
        "import-model",
        help="Import a model assumption set from an XLSX file.",
    )

    model_import_parser.add_argument(
        "model_name",
        help="Name of the model to import.",
    )

    # --------------------------------------------------
    # evaluate-model command
    # --------------------------------------------------

    evaluate_parser = subparsers.add_parser(
        "evaluate-model",
        help="Evaluate a model.",
    )

    evaluate_parser.add_argument(
        "committee_name",
        help="Name of the committee configuration.",
    )

    evaluate_parser.add_argument(
        "model_name",
        help="Name of the model to evaluate.",
    )

    evaluate_parser.add_argument(
        "rubric_name",
        help="Name of the evaluation rubric.",
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

    if args.command == "import-model":

        importer = AssumptionImporter()
        output_path = importer.import_assumption(args.model_name)

        print(f"Model imported to: {output_path}")

        loader = AssumptionLoader()
        print(loader.list_assumptions())
        print(loader.load(args.model_name))

    if args.command == "evaluate-model":

        # Check the committee first. It must already exist and is never
        # imported automatically.
        try:
            WorkflowConfigLoader().load(
                committee_name=args.committee_name,
                rubric=args.rubric_name,
                model=args.model_name,
            )
        except FileNotFoundError as exc:
            parser.error(str(exc))

        try:
            _load_model(args.model_name)
            _load_rubric(args.rubric_name)
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))

        try:
            workflow = EvaluationWorkflow(LLMClient())
            results = workflow.run(
                committee_config=args.committee_name,
                rubric_name=args.rubric_name,
                model_name=args.model_name,
            )
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))

        for result in results:
            print(f"\n=== Evaluation Result ({result.evaluator_id}) ===")
            print(result.response)
    




if __name__ == "__main__":
    main()

#python main.py import-rubric test_rubric   
#python main.py evaluate-model test_committee cutting_stock_model test_rubric
