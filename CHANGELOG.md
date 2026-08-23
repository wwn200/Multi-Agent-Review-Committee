All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-08-23
This release establishes the first complete version of the model evaluation framework, integrating rubric processing, 
model assumption management, evaluator agent generation, and model evaluation into a unified workflow.

### Key Features
- Integrated end-to-end model evaluation workflow.
- Configurable evaluator committees with different roles and backgrounds.
- Structured rubric loading, validation, and prompt generation.
- Model assumption import and evaluation.
- YAML-based project configuration.
- CLI interfaces for importing rubrics and models and running model evaluation.

### Added
- Added an integrated evaluation workflow for orchestrating the complete model evaluation process.
- Added the import-model CLI interface for importing model assumption configurations.
- Added workflow tests covering the integrated evaluation process.
- Added support for YAML-based configuration across the project.

### Changed
- Updated the evaluate-model CLI interface to execute the integrated evaluation workflow.
- Updated rubric and model importers to generate YAML configuration files.
- Updated configuration loaders and related components to work with YAML-based configurations.
- Retained legacy JSON loading support for existing configuration files.
- Updated existing tests to reflect the YAML-based configuration format and integrated workflow.

### Documentation
- Updated the README to reflect the current project workflow, configuration structure, and available CLI interfaces.
- Updated project documentation under docs to reflect the new evaluation workflow and configuration architecture.

### Released
- This release establishes the first complete, integrated version of the model evaluation pipeline.


## [0.4.0] - 2026-08-21

### Added
- Added structured rubric loading, validation, and prompt generation.


## [0.3.0] - 2026-08-21

### Added
- Added a configurable evaluator profile framework with role and background definitions.
- Added YAML-based loading and combination of evaluator roles and backgrounds.
- Added stochastic evaluator profile sampling with configurable traits and attention weights.
- Added evaluator agent construction for individual evaluators and evaluator populations.
- Added structured system and user prompt generation based on evaluator profiles.
- Added LLM-based evaluation of model assumptions.
- Added API tests for evaluator generation and evaluation.


## [0.2.0] - 2026-08-14

### Added
- Added evaluation rubric import functionality, supporting the import of XLSX-based evaluation criteria and conversion to standardized JSON configurations.
- Added model assumption import functionality, supporting the import of XLSX-based assumption sets and conversion to standardized JSON configurations.


## [0.1.0] - 2026-08-13

### Added
- Added basic LLM client for OpenAI API integration.
- Added API connectivity test.