#!/bin/bash

check_os() {
    os_type=$(uname)
    if [ "$os_type" == "Darwin" ]; then
        echo "The host operating system is macOS."
    elif [ "$os_type" == "Linux" ]; then
        echo "The host operating system is Linux."
    else
        echo "The host operating system is not suppported."
        exit 1
    fi
}

check_git() {
    if command -v git &> /dev/null; then
        echo "Git is installed."
    else
        echo "Git is not installed."
        exit 1
    fi
}

clean_readme() {
    if [ -f "README.md" ]; then
        first_line=$(head -n 1 README.md)
        echo "$first_line" > README.md
        echo "README.md has been cleaned."
    else
        echo "README.md does not exist in the current directory."
    fi
}

check_os
check_git
clean_readme

echo "Removing workflows"
rm ./.github/workflows/*

echo "Removing tests"
rm ./tests/*

echo "Ready to start the tutorial"

