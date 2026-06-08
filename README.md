# MESW SES 2025/2026 - Group 3

Hi! This is the repository for our SES project.

Our group includes:

- Gonçalo Araújo Guimarães Cardoso Sampaio
- Gonçalo de Almeida Pinto e Morais de Castro
- Afonso da Cruz Pimenta
- José Pedro Pereira da Costa

## Gatekeeper

Gatekeeper is the project idea we decided to implement.

It is a CLI tool that we developed and is able to run multiple SAST tools at once in an easy and user-friendly way. It is designed to be extensible and customizable, allowing users to choose which tools they want to run and how they want to run them.

## Evaluation Report

The project's evaluation report can be found in the [REPORT](REPORT.md) file. It contains information about the design of the tool, the achieved results (with FP/FN analysis tables) and lessons learnt during its development. The report also includes a video demonstrating the tool's functionalities.

## First steps and how to use

To get started with Gatekeeper, please refer to the [README](gatekeeper/README.md) file in the `gatekeeper` directory. It contains detailed instructions on how to set up and use the tool.

The most important files to take a look at are:

```
└── 📁 gatekeeper
    ├── 📁 docker          -> Docker utilities for the CLI
    ├── 📁 src             -> Source code for the gatekeeper CLI
    ├── DEV_DOCS.md        -> Development hints and explanations
    ├── IMPROVEMENTS.md    -> What's left to do/improve
    ├── README.md          -> Gatekeeper setup and usage instructions
    └── tools-config.yaml  -> SAST tools configuration
└── README.md              -> You are here!
```
