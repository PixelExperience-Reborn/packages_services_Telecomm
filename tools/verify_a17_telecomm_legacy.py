#!/usr/bin/env python3
"""Historical Telecomm source-inventory check, not Android17 telephony validation."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ANDROID = "{http://schemas.android.com/apk/res/android}"


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print("PASS INVENTORY:", message)


def main():
    bp = (ROOT / "Android.bp").read_text()
    manifest = ET.parse(ROOT / "AndroidManifest.xml").getroot()
    calllog = (ROOT / "src/com/android/server/telecom/CallLogManager.java").read_text()
    impl = (ROOT / "src/com/android/server/telecom/TelecomServiceImpl.java").read_text()
    testmap = (ROOT / "TEST_MAPPING").read_text()
    check('name: "Telecom"' in bp and 'name: "TelecomUnitTests"' in bp,
          "legacy Telecom APK and unit tests")
    check('name: "TelecomLib"' not in bp and 'name: "TelecomShim"' not in bp
          and 'name: "TelecomUi"' not in bp,
          "historical source lacks Android17 Telecom split")
    check('"SettingsLibDefaults"' in bp, "legacy TelecomUnitTests SettingsLib dependency")
    check(manifest.get("package") == "com.android.server.telecom"
          and manifest.get(ANDROID + "sharedUserId") == "android.uid.system",
          "system Telecom identity")
    check("mContext.sendBroadcastAsUser(callAddIntent, UserHandle.SYSTEM" in calllog,
          "old cross-user call-log broadcast patch recorded (NOT PORTED)")
    check("validateAccountIconUserBoundary(account.getIcon())" in impl
          and "private void validateAccountIconUserBoundary(Icon icon)" in impl,
          "old PhoneAccount icon user-boundary security check")
    for name in ("TelecomUnitTests", "CtsTelecomTestCases", "CtsTelephony2TestCases"):
        check(name in testmap, "historical test mapping: " + name)
    check(not (ROOT / "shim").exists() and not (ROOT / "TelecomUi").exists(),
          "AOSP17 Mainline/TelecomUi directories absent in old tree")
    print("PASS: legacy markers only. Android17 Soong/APEX/calls/security NOT TESTED.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ET.ParseError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        sys.exit(1)
