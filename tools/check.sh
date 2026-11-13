#!/bin/bash
# Run on the build VPS. Type-check the native crate in its staged worktree:
# server flavour (the crate alone, horizon-client without default features),
# its unit tests, then the client flavour (the native game with default
# features).
. ~/.cargo/env
export CARGO_TARGET_DIR=/opt/build/target CARGO_BUILD_JOBS=4
cd /opt/build/wt/deeperdarker
echo "== check mod-deeperdarker (server flavour)"; date
nice -n 10 cargo check -p mod-deeperdarker --message-format short 2>&1 | grep -vE "^\s+(Compiling|Checking)"
echo "check_server_exit=${PIPESTATUS[0]}"; date
if [ "$1" = "full" ]; then
echo "== test mod-deeperdarker"
nice -n 10 cargo test -p mod-deeperdarker --message-format short 2>&1 | grep -vE "^\s+(Compiling|Checking)" | tail -40
echo "test_exit=${PIPESTATUS[0]}"; date
echo "== check horizon-native-game (client flavour, default features)"
nice -n 10 cargo check -p horizon-native-game --message-format short 2>&1 | grep -vE "^\s+(Compiling|Checking)"
echo "check_client_exit=${PIPESTATUS[0]}"; date
fi
echo DONE
