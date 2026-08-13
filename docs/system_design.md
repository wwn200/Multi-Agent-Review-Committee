
## 1. Architecture

                     User provides XLSX
                           │
                           ▼
                    Rubric Importer
                           │
                    Parse + Validate
                           │
                           ▼
                    configs/rubrics/
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        Technical       Manager       Owner
          Agent           Agent         Agent
              │            │            │
       Stakeholder      Stakeholder   Stakeholder
          Profile          Profile       Profile
              │            │            │
              └────────────┼────────────┘
                           ▼
                    Individual Scores