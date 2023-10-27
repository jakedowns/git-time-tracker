import os
import git
import csv
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

total_time_worked = 0

def convert_time_to_minutes(time_str):
    # Convert time string in format HH:MM to minutes
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def generate_summary(time_data_by_date):
    # Initialize summaries
    weekly_summary = defaultdict(int)
    daily_summary = defaultdict(int)

    for date, commit_data in time_data_by_date.items():
        week_num = date.isocalendar()[1]
        total_time = sum(time for _, _, time in commit_data)  # Sum up the time worked for each date
        weekly_summary[week_num] += total_time
        daily_summary[date] += total_time

    return weekly_summary, daily_summary

def generate_total_summary(time_data_by_date):
    total_summary = defaultdict(int)

    for date, commit_data in time_data_by_date.items():
        total_time = sum(time for _, _, time in commit_data)
        total_summary[date] = total_time

    return total_summary

def estimate_time_worked(current_commit, previous_commit, max_timeout):
    time_difference = (current_commit.committed_date - previous_commit.committed_date) / 60  # in minutes

    if time_difference > max_timeout:
        return max_timeout
    return time_difference

def round_time_to_nearest(time_worked, min_unit_worked):
    return round(time_worked / min_unit_worked) * min_unit_worked

def main(args=None):
    parser = argparse.ArgumentParser(description="Generate time-worked estimates from Git commits.")
    parser.add_argument('-f', '--filter', help="Filter for commit lines (e.g., author's name/email).", default="")
    parser.add_argument('-s', '--start', help="Start date in format YY-MM-DD.", default=None)
    parser.add_argument('-e', '--end', help="End date in format YY-MM-DD.", default=None)
    parser.add_argument('--max-timeout', help="Maximum time (in minutes) between commits before they're considered incongruent.", type=int, default=60)
    parser.add_argument('--min-unit-worked', help="Round time worked to the nearest specified minutes.", type=int, default=60)
    parser.add_argument('--repo-path', help="Path to the Git repository.", default="")

    args = parser.parse_args(args)

    repo = git.Repo(args.repo_path)  # Assuming the script is run in the repo directory
    start_date = args.start if args.start else '1970-01-01'  # Default to a date far in the past if no start date is provided
    end_date = args.end if args.end else datetime.now().strftime('%Y-%m-%d')  # Default to today's date if no end date is provided

    commits = list(repo.iter_commits(since=start_date, until=end_date))

    time_data_by_date = defaultdict(list)
    commit_count_by_date = defaultdict(int)

    commit_count = len(commits);

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
            time_data_by_date[date].append((commit.hexsha[:7], commit.message, time_estimate))
            commit_count_by_date[date] += 1  # Increment the commit count for this date
        
        previous_commit = commit

    filtered_commits = len(time_data_by_date)
    print(f"Number of commits checked: {commit_count}")
    print(f"Number of commits filtered: {filtered_commits}")

    print("Number of commits per day:")
    for date, count in commit_count_by_date.items():
        print(f"{date}: {count} commits")

    print("Generating summaries...")
    weekly_summary, daily_summary = generate_summary(time_data_by_date)

    print("Writing to CSV files...")

    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open("output/output_detailed.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Commit Hash", "Commit Message", "Time Worked (in hours)"])
        for date, commit_data in time_data_by_date.items():
            for commit_hash, commit_message, time in commit_data:
                writer.writerow([date, commit_hash, commit_message, time / 60])  # Convert to hours

    with open("output/output_weekly_summary.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Week Number", "Time Worked (in hours)"])
        for week_num, time in weekly_summary.items():
            writer.writerow([week_num, time / 60])  # Convert to hours

    with open("output/output_daily_summary.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Time Worked (in hours)"])
        for date, time in daily_summary.items():
            writer.writerow([date, time / 60])  # Convert to hours

    print("Generating total summary...")
    total_summary = generate_total_summary(time_data_by_date)

    print("Writing to total summary CSV file...")
    with open("output/output_total_summary.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "Total Time Worked (in hours)"])
        for date, total_time in total_summary.items():
            writer.writerow([date, total_time / 60])  # Convert to hours

    print("Process complete. Check the generated CSV files.")

    # print("Printing contents of all output files...")
    # for filename in os.listdir(output_dir):
    #     if filename.endswith(".csv"):
    #         print(f"\nContents of {filename}:")
    #         with open(os.path.join(output_dir, filename), "r") as f:
    #             print(f.read())

    total_time_worked = sum(total_summary.values())
    print(f"\nTotal time worked: {total_time_worked // 60} hours and {total_time_worked % 60} minutes")

if __name__ == "__main__":
    main()