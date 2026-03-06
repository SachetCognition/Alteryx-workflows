# Alteryx Workflow Repository

Welcome to the Alteryx Workflow Repository! This repository hosts a collection of Alteryx workflows designed to streamline data processing, analysis, and automation tasks.

## Overview

In this repository, you will find:

- **Alteryx Workflows**: .yxmd or .yxzp files containing data workflows for data preparation, blending, analysis, and reporting.
- **Data Files**: Sample data files or connections used within the workflows.
- **Documentation**: Guides, tutorials, and explanations on how to use, customize, and deploy the workflows.
- **Scripts**: Any additional scripts or tools used alongside Alteryx workflows.

## Usage

To utilize the Alteryx workflows in this repository:

1. **Clone or Download**: Clone this repository to your local machine or download it as a ZIP file.
2. **Install Alteryx Designer**: If you haven't already, download and install [Alteryx Designer](https://www.alteryx.com/designer-trial).
3. **Open Workflow**: Open the desired Alteryx workflow (.yxmd or .yxzp file) using Alteryx Designer.
4. **Configure Input and Output**: If necessary, configure input connections to your data sources and output destinations.
5. **Run the Workflow**:

   1. Open Alteryx Designer and go to **File → Open Workflow**. Navigate to the directory where you cloned this repository.
   2. Select the desired `.yxmd` file. The available workflows are:
      - `Accident Workflow.yxmd` — Timezone-based accident summarization and batch CSV output
      - `Accident-user-input.yxmd` — Day/hour accident analysis with interactive date-range filtering
      - `Ted talk Workflow.yxmd` — TED talk analysis (top talks, speaker frequency, monthly trends)
      - `New Workflow2.yxmd` — Superstore sales analysis with PDF report generation
      - `New Workflow1.yxmd` — Purchase registration data cleansing
   3. **Configure input data paths**: If any **Input Data** tool shows a red error icon (`!`), double-click it and update the file path to point to the correct local file in the `Datasets/` directory (or to your local copy of the external dataset).
   4. **Ensure macro files are resolvable**: Keep all `.yxmc` macro files (`accident-macro.yxmc`, `user-input-macro.yxmc`, `TD-input-macro.yxmc`) in the same directory as the `.yxmd` workflow files so that Alteryx can locate them automatically.
   5. Click the **Run** button (green arrow) in the toolbar, or press **Ctrl+R**, to execute the workflow.
   6. Monitor progress in the **Results** pane at the bottom of Alteryx Designer. Once the run completes, tool-level record counts will appear on the connectors between tools in the canvas.

6. **Review Results**:

   - **Browse Tools**: After execution, click on any **Browse** or **BrowseV2** tool in the workflow canvas to inspect output records directly within Alteryx Designer. Each Browse tool shows a table of the records that passed through that point in the workflow.
   - **Output Files** (`Accident Workflow.yxmd`): This workflow uses the batch macro (`accident-macro.yxmc`) to generate one CSV file per timezone (e.g., `o1_time_Eastern.csv`, `o1_time_Central.csv`, etc.). Check the output directory configured in the macro's Output Data tool for the generated files.
   - **Reports & Visualizations** (`New Workflow2.yxmd` — Superstore Sales): This workflow generates a **Plotly bar chart** of sales data, a **ComposerTable** with conditional formatting (highlighting the minimum sales value), and a **ComposerText** block with cumulative sales information. These components are assembled into a PDF report via the **ComposerRender** tool — check the configured output path for the rendered PDF.
   - **Interactive Workflows** (`Accident-user-input.yxmd` and `Ted talk Workflow.yxmd`): When you run these workflows, Alteryx will present **input prompts** (date-range pickers or dropdowns) before execution begins. Fill in the requested parameters (e.g., start/end dates, or MTD/YTD/WTD selection), then click OK. After the workflow completes, inspect the **Browse** tools for filtered results.

## Formatting

To maintain consistency and readability across Alteryx workflows, please adhere to the following formatting guidelines:

- Organize the workflow with clear and logical workflows.
- Use meaningful names for tools, inputs, outputs, and macros.
- Include annotations and comments to explain complex workflows or logic.
- Follow best practices for efficient data processing and optimization.

## Git Commands for Alteryx Workflows

When collaborating on Alteryx workflows within this repository, consider using Git commands to manage changes efficiently:

- `git clone <repository_url>`: Clone the repository to your local machine.
- `git add <file>`: Add the modified Alteryx workflow file (.yxmd or .yxzp) to the staging area.
- `git commit -m "Your commit message"`: Commit the changes along with a descriptive message indicating the purpose of the modifications.
- `git push origin <branch>`: Push the committed changes to the remote repository, making them available to other team members.
- `git pull origin <branch>`: Pull the latest changes from the remote repository to your local machine.


## Feedback

Your feedback is valuable to us! If you have any questions, suggestions, or encounter any issues while using our Alteryx workflows, please don't hesitate to
[open an issue](https://github.com/nandita2000/Alteryx-workflows/issues) in this repository.

## License

This repository is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the workflows and resources as needed, but please attribute the original work appropriately.

## Contact

For any inquiries or further assistance, please contact [nanditasharma182@gmail.com].

## Troubleshooting

Below are common issues you may encounter and how to resolve them:

| Problem | Solution |
|---|---|
| **Red `!` on Input Data tool** | The file path is invalid. Double-click the Input Data tool and reconfigure the path to point to the correct file in your local `Datasets/` directory (or to your local copy of the external dataset). |
| **Macro not found warning** | Alteryx cannot locate a `.yxmc` file. Ensure all macro files (`accident-macro.yxmc`, `user-input-macro.yxmc`, `TD-input-macro.yxmc`) remain in the same directory as the `.yxmd` workflow files, preserving the original repository structure. |
| **Empty Browse output** | No records reached the Browse tool. Check the filter expressions and upstream record counts on connectors to identify where records are being dropped. |
| **Batch macro produces zero output files** | The batch macro (`accident-macro.yxmc`) received no records. Verify that the upstream Summarize and Filter steps are passing records into the macro by clicking on intermediate Browse tools or checking connector record counts. |

Thank you for using our Alteryx workflows! We hope they streamline your data processing and analysis tasks effectively. Happy workflow building!
