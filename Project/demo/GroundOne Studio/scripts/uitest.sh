#!/bin/zsh
# Runs the UI tests. Floating windows (e.g. Activity Monitor's GPU History) can cover the app and swallow clicks, so
# Activity Monitor is hidden for the duration and shown again afterwards. Usage: scripts/uitest.sh [test-name ...]
cd "$(dirname "$0")/.."
osascript -e 'tell application "System Events" to if exists process "Activity Monitor" then set visible of process "Activity Monitor" to false' 2>/dev/null
xcodegen generate >/dev/null
args=()
for t in "$@"; do args+=(-only-testing:GroundOneStudioUITests/GroundOneStudioUITests/$t); done
rm -rf build/ui.xcresult
# XCTest can hang while symbolicating a failure: cap the run, the log still shows the failing step.
( sleep ${UITEST_TIMEOUT:-900}; pkill -f "xcodebuild test"; pkill -f UITests-Runner ) &
watchdog=$!
xcodebuild test -project GroundOneStudio.xcodeproj -scheme GroundOneStudio -destination 'platform=macOS' \
  -derivedDataPath build/app -resultBundlePath build/ui.xcresult -skipPackagePluginValidation -skipMacroValidation \
  "${args[@]}" > build/ui.log 2>&1
code=$?
kill $watchdog 2>/dev/null
pkill -f "GroundOne Studio.app/Contents/MacOS" 2>/dev/null
osascript -e 'tell application "System Events" to if exists process "Activity Monitor" then set visible of process "Activity Monitor" to true' 2>/dev/null
rm -rf build/ui-shots && mkdir -p build/ui-shots
xcrun xcresulttool export attachments --path build/ui.xcresult --output-path build/ui-shots >/dev/null 2>&1
grep -E "error:|Test Case .*(passed|failed)|TEST (SUCCEEDED|FAILED)|Assertion Failure|XCTAssert" build/ui.log
exit $code
