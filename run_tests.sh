#!/bin/bash

# Run various test and linting tools

# Define the commands to run
commands=(
    "python -m pylint app"
    "python -m pyright app"
    "python -m pycodestyle app"
    "python -m pydocstyle --add-ignore=D107 app"
    "python -m bandit -r . --exclude=/tests/,/venv/"
    "python -m flake8 --exclude=tests/*,venv/*,migrations/versions/*"
    "python -m mypy . --explicit-package-bases --exclude 'tests/' --exclude 'venv/'"
)

# Initialize counters for success and failure
total_commands=${#commands[@]}
success_count=0
failure_count=0
skip_count=0

# Loop through each command
for cmd in "${commands[@]}"; do
    echo "Run: $cmd"

    # Execute the command and capture stdout and stderr
    output=$(eval "$cmd" 2>&1)
    exit_code=$?

    # Check the exit code
    if [ $exit_code -ne 0 ]; then
        # Command failed, print output
        echo "FAIL"
        echo "$output"
        ((failure_count++))
    else
        # Command succeeded
        echo "PASS"
        ((success_count++))
    fi

    echo "----------------------"
done

# Always print full test and coverage output:
((total_commands++))
python -m pytest --cov=. tests -p no:cacheprovider --cov-report term-missing
if [ $? -ne 0 ]; then
    ((failure_count++))
else
    ((success_count++))
fi

# System test
echo "----------------------"
echo "Run: system test"
((total_commands++))
./system_test.sh
result=$?
if [[ $result -gt 100 ]]; then
    echo "SKIP"
    ((skip_count++))
elif [[ $result -eq 0 ]]; then
    echo "PASS"
    ((success_count++))
else
    echo "FAIL"
    ((failure_count++))
fi
echo "----------------------"

# Summary
echo ""
echo "Test and lint summary:"
echo "  Total commands: $total_commands"
echo "  Passed: $success_count"
echo "  Failed: $failure_count"
echo "  Skipped: $skip_count"
