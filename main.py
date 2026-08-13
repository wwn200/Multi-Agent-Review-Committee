from llm.client import LLMClient


def main():

    llm = LLMClient()

    # response = llm.generate(
    #     system_prompt="""
    #     You are a technical project reviewer.
    #     Evaluate the technical feasibility of a project proposal.
    #     """,
    #     user_prompt="""
    #     A company proposes an autonomous delivery robot
    #     for university campuses.

    #     Evaluate its technical feasibility.
    #     """,
    # )

    response = llm.generate(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say something you want (around 100 words)."
    )

    print(response)


if __name__ == "__main__":
    main()