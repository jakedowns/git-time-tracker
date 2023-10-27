# git-time-tracker
Use Git for Time Tracking / Time Worked Estimations

A simple Python script that analyzes Git commits to generate estimates of time worked. This script reads commit messages to extract work hours and then provides a summarized report of work hours categorized by day and week.

## Requirements

- Python 3.7 or newer
- GitPython library (specified in `requirements.txt`)

## Getting Started

### 1. Setup

First, you'll want to set up a virtual environment for this project:

```
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

Next, install the required libraries:

```
pip install -r requirements.txt
```

### 2. Usage

Navigate to your Git repository directory and run:

```
python path_to_script/git_commit_time_tracker.py --filter "John Doe" --start 23-01-01 --end 23-12-31
```

Here's a breakdown of the available flags:

- `-f` or `--filter`: Filter commits by a fuzzy match string such as an author's name or email.
- `-s` or `--start`: Specify the start date for commits to consider (format: YY-MM-DD).
- `-e` or `--end`: Specify the end date for commits to consider (format: YY-MM-DD).
- `--repo`: Specify the remote repo path if it's not the cwd

The script will produce four CSV files:

1. `output_detailed.csv`: Time worked for each day.
2. `output_weekly_summary.csv`: Total time worked per week.
3. `output_daily_summary.csv`: Time worked categorized by day.
4. `output_total_summary.csv`: Total time worked

## Feedback and Contribution

Feedback and contributions are welcome! Please open an issue or pull request on our GitHub repository.
