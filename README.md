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
5. **Run the Workflow**: Execute the workflow to perform data processing, blending, or analysis tasks.
6. **Review Results**: Review the output data and any generated reports or visualizations to gain insights.

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


## Data Loading & Configuration

Each workflow requires specific input datasets. The table below maps each workflow to its required dataset(s) and expected file location:

| Workflow | Required Dataset(s) | Expected Location |
|---|---|---|
| `Accident Workflow.yxmd` | `US_Accidents_March23.csv`, `Cleanse.yxmc`, `accident-macro.yxmc` | Root or `Datasets/` directory |
| `Accident-user-input.yxmd` | `US_Accidents_March23.csv` | Root or `Datasets/` directory |
| `Ted talk Workflow.yxmd` | `ted_main.csv` | `Datasets/` directory |
| `New Workflow2.yxmd` | `Sample - Superstore.xls` | Root or `Datasets/` directory |
| `New Workflow1.yxmd` | Purchase registration CSV (`updated1_pur_reg_2200_2300.csv`) | Root or `Datasets/` directory |

### Loading Data Instructions

1. Ensure all required datasets are placed in the correct directories relative to the workflow files.
2. Open each workflow in Alteryx Designer, double-click on every **Input Data** tool (usually the leftmost tool on the canvas), and verify or update the file path to point to the correct local file.
3. For `.csv` files, confirm the delimiter (comma) and encoding settings are correct in the Input Data tool configuration.
4. For `.xls` files, confirm the correct sheet name is selected.
5. Click "Run" or press `Ctrl+R` after configuring inputs to test the data loads correctly.

### Designer Cloud Conversion (Ted Talk Workflow)

The Ted Talk Workflow has been successfully converted and verified in **Alteryx Designer Cloud**. The cloud version is available at:

- **Workflow URL**: [Ted Talk Workflow in Designer Cloud](https://us1.alteryxcloud.com/designer/workflows/01KK0C8WRRK5WQCFJWWWJ9ATPJ)
- **Dataset**: `ted_main.csv` (2,550 rows, 12 columns) uploaded to Alteryx Cloud (Dataset ID: 624443)

The cloud workflow includes 13 tools across 4 analytical branches:
- **Top Talks**: Sort by views (descending) → Sample first 5 rows → Sort by Year (descending)
- **Top Speakers**: Summarize count by `main_speaker` → Sort by count (descending) → Sample first 5 → Running Total (Rank)
- **Monthly Trends**: Summarize count by `Month`/`Month_name` → Sort by Month (ascending)
- **Social Entrepreneurs**: RegEx match on `speaker_occupation` for "social entrepreneur" pattern

**Note**: Desktop-only tools (ComposerTable, PlotlyCharting, macros) were replaced with cloud-compatible Browse endpoints. The core data transformation logic is preserved.

## Workflow Verification Checklist

### General Verification Steps (All Workflows)

After running any workflow, verify the following:

1. No tools show red error icons on the canvas.
2. Record counts appear on all connectors between tools (non-zero counts expected).
3. Click on each Browse tool to confirm output data is populated and looks reasonable.
4. Check the Results/Messages pane at the bottom for any warnings or errors.

### Per-Workflow Verification

**`Accident Workflow.yxmd`**
- Verify the batch macro (`accident-macro.yxmc`) produces one output CSV per timezone.
- Check that the Cleanse macro (`Cleanse.yxmc`) runs without errors.
- Confirm output CSVs contain cleaned, timezone-grouped accident data.

**`Accident-user-input.yxmd`**
- Verify the interface prompts appear (date range picker).
- Enter a valid date range, run, and confirm the Browse tool shows filtered accident records within that range.

**`Ted talk Workflow.yxmd`** (Desktop)
- Verify interface dropdowns/selectors appear.
- Confirm Browse tools show speaker and engagement analysis results with non-empty data.

**`Ted talk Workflow.yxmd`** (Designer Cloud — Verified)
- **Summarize #7**: "2550 records were summarized to 2156 groups" (Top Speakers branch)
- **Summarize #11**: "2550 records were summarized to 12 groups" (Monthly Trends — 12 months)
- **RegEx #13**: "5 matched and 2545 were not" (Social Entrepreneurs — 5 speakers matched)
- **Messages pane**: 0 Warnings, 0 Errors, 0 Conversion Errors
- All 4 branches produce non-empty output data with correct record counts

**`New Workflow2.yxmd`**
- Verify the Plotly bar chart renders (check the Interactive Chart tool output).
- Confirm the ComposerTable shows sales data with orange conditional formatting on the minimum-sales row.
- Verify the report layout tool assembles all components.

**`New Workflow1.yxmd`**
- Verify the Cleanse tool processes the purchase CSV.
- Confirm Browse output shows cleaned, properly formatted data.

### Common Data Loading Issues and Fixes

| Issue | Fix |
|---|---|
| "File not found" error | Update the Input Data tool path to the correct local path |
| "No records returned" | Check that the dataset file is not empty and the correct sheet/delimiter is configured |
| Macro errors | Ensure `.yxmc` files are in the same directory as the `.yxmd` workflow files; do not rename or move them |
| Date parsing errors | Verify date columns in the CSV match the expected format (check the DateTime tool or formula configurations in the workflow) |
| Desktop-to-Cloud conversion errors | Use `AlteryxSpatialPluginsGui.Summarize.Summarize` (not Base) for Summarize tools; add `CaseInsensitve` (misspelled) field for RegEx tools |

## Feedback

Your feedback is valuable to us! If you have any questions, suggestions, or encounter any issues while using our Alteryx workflows, please don't hesitate to
[open an issue](https://github.com/nandita2000/Alteryx-workflows/issues) in this repository.

## License

This repository is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the workflows and resources as needed, but please attribute the original work appropriately.

## Contact

For any inquiries or further assistance, please contact [nanditasharma182@gmail.com].

Thank you for using our Alteryx workflows! We hope they streamline your data processing and analysis tasks effectively. Happy workflow building!
