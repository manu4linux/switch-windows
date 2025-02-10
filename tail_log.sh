FILE_L=$(jq -r '.logfilepath' config.json) && [ -f "$FILE_L" ] && tail -f "$FILE_L" || echo "File $FILE_L does not exist."
