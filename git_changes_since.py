import subprocess
import argparse
import csv
import io
from datetime import datetime

def run_git_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error running command {' '.join(command)}: {result.stderr}")
        return None
    return result.stdout

def list_git_changes(since, until, folder):
    # Format the since and until parameters for git log
    since_str = f'--since={since}'
    until_str = f'--until={until}'
    
    log_output = run_git_command(['git', 'log', since_str, until_str, '--name-status', '--pretty=format:%H,%ad,%s', '--date=short', '--', folder])
    
    if not log_output:
        print("No commits in the specified period and folder.")
        return

    output = io.StringIO()
    fieldnames = ['Commit Hash', 'Date', 'Message', 'Change Type', 'File', 'Changed Lines']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    lines = log_output.splitlines()
    commit_hash, date, message = '', '', ''
    
    for line in lines:
        if line and ',' in line and not line.startswith(('A', 'M', 'D')):
            parts = line.split(',', 2)
            commit_hash, date, message = parts[0], parts[1], parts[2]
        elif line:
            change_type, file_path = line.split('\t')
            # Get the number of changed lines
            diff_output = run_git_command(['git', 'diff', f'{commit_hash}^!', '--', file_path])
            changed_lines = len(diff_output.splitlines())
            writer.writerow({
                'Commit Hash': commit_hash,
                'Date': date,
                'Message': message,
                'Change Type': change_type,
                'File': file_path,
                'Changed Lines': changed_lines
            })
    
    print(output.getvalue())
    output.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List Git changes in a specified time period and folder.")
    parser.add_argument('--start-date', type=str, help='Start date in YYYY-MM-DD format', required=True)
    parser.add_argument('--end-date', type=str, help='End date in YYYY-MM-DD format', required=True)
    parser.add_argument('--folder', type=str, help='Folder to check for changes', required=True)
    args = parser.parse_args()

    list_git_changes(args.start_date, args.end_date, args.folder)
