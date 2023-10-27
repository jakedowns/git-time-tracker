import os
import git
import csv
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

def parse_commit_message(message):
    # Extract time information
    return time

def convert_time_to_minutes(time_str):
    # Convert to minutes
    return minutes

def generate_summary(time_data_by_date):
    # Initialize summaries
    weekly_summary = defaultdict(int)
    daily_summary = defaultdict(int)

    for date, time in time_data_by_date.items():
        week_num = date.isocalendar()[1]
        weekly_summary[week_num] += time
        daily_summary[date] += time

    return weekly_summary, daily_summary

def estimate_time_worked(current_commit, previous_commit, max_timeout):
    time_difference = (current_commit.committed_date - previous_commit.committed_date) / 60  # in minutes

    if time_difference > max_timeout:
        return max_timeout
    return time_difference

def round_time_to_nearest(time_worked, min_unit_worked):
    return round(time_worked / min_unit_worked) * min_unit_worked

def main():
    parser = argparse.ArgumentParser(description="Generate time-worked estimates from Git commits.")
    parser.add_argument('-f', '--filter', help="Filter for commit lines (e.g., author's name/email).", default="")
    parser.add_argument('-s', '--start', help="Start date in format YY-MM-DD.", default=None)
    parser.add_argument('-e', '--end', help="End date in format YY-MM-DD.", default=None)
    parser.add_argument('--max-timeout', help="Maximum time (in minutes) between commits before they're considered incongruent.", type=int, default=60)
    parser.add_argument('--min-unit-worked', help="Round time worked to the nearest specified minutes.", type=int, default=60)
    parser.add_argument('--repo-path', help="Path to the Git repository.", default="")

    args = parser.parse_args()

    repo = git.Repo(args.repo_path)  # Assuming the script is run in the repo directory
    commits = list(repo.iter_commits())

    time_data_by_date = defaultdict(int)

    previous_commit = None
    for commit in reversed(commits):  # We need to process commits in chronological order
        if args.filter.lower() not in commit.message.lower() and args.filter.lower() not in commit.author.email.lower():
            previous_commit = commit
            continue
        
        date = datetime.fromtimestamp(commit.committed_date).date()
        if args.start and date < datetime.strptime(args.start, '%y-%m-%d').date():
            previous_commit = commit
            continue
        if args.end and date > datetime.strptime(args.end, '%y-%m-%d').date():
            previous_commit = commit
            continue

        if previous_commit:
            time_estimate = estimate_time_worked(commit, previous_commit, args.max_timeout)
            time_estimate = round_time_to_nearest(time_estimate, args.min_unit_worked)
            time_data_by_date[date] += time_estimate
        
        previous_commit = commit

    print("Generating summaries...")
    weekly_summary, daily_summary = generate_summary(time_data_by_date)

    print("Writing to CSV files...")

    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open("output/output_detailed.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Time Worked (in minutes)"])
        for date, time in time_data_by_date.items():
            writer.writerow([date, time])

    with open("output/output_weekly_summary.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Week Number", "Time Worked (in minutes)"])
        for week_num, time in weekly_summary.items():
            writer.writerow([week_num, time])

    with open("output/output_daily_summary.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Time Worked (in minutes)"])
        for date, time in daily_summary.items():
            writer.writerow([date, time])

    print("Process complete. Check the generated CSV files.")

if __name__ == "__main__":
    main()
