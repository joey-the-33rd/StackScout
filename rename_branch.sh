#!/bin/bash

OLD_BRANCH="blackboxai/fix-selenium-timeout"
NEW_BRANCH="blackbops/fix-webdriver-timeout"

# Checkout old branch
git checkout "$OLD_BRANCH" || exit

# Rename locally
git branch -m "$NEW_BRANCH"

# Push new branch to origin and track it
git push origin -u "$NEW_BRANCH"

# Delete old remote branch
git push origin --delete "$OLD_BRANCH"

echo "✅ Renamed branch and updated remote."
echo "👉 If there was a PR, check GitHub to confirm it's pointing to $NEW_BRANCH."
