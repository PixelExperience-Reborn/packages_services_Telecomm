# P1 — Android 17 Telecomm / mondrian architectural and security audit

Date: 2026-11-04. **AUDIT ONLY — legacy `seventeen` source is not ported or selected in manifest.**

## Verified source history

- Historical PixelExperience-Reborn `packages_services_Telecomm` branch `seventeen` commit `f184dd69bb7068c66a1acefa9193cc6a81bbb4ab`, Android14 r21 merge on 2024-01-30. Repository paths, original code and build module remain untouched in `seventeen`.
- Official AOSP17 r1 `platform/packages/services/Telecomm`: commit `2353977dc28ff88d3cdc1ec636fa9c3251d2ff86`, exact tree `a89bb989bed58e9a0fcb43c1e52d950c20e849e5`. Source: https://android.googlesource.com/platform/packages/services/Telecomm/+/refs/tags/android-17.0.0_r1
- The AOSP17 source graph also contains `platform/packages/modules/Telecom` (official commit `f6ffa23d448d05d000c250251fd25b24dbee046c`) and `platform/packages/modules/Telephony`, `platform/packages/services/Telephony`, `platform/packages/providers/TelephonyProvider`. **Telecomm and Telephony/TelephonyCore cannot be audited as isolated platform-only APKs.**
- The staged PE-Reborn AOSP17 manifest currently selects official `platform/packages/services/Telecomm`, `platform/packages/modules/Telecom`, `platform/packages/modules/Telephony`, and `platform/packages/services/Telephony`. None of these is replaced in this audit.

## Critical Soong/API divergence

The historical Android14 `Android.bp` declares one app `Telecom` with `Telecom-srcs` and `services`; its `TelecomUnitTests` rely on `SettingsLibDefaults`. The Android17 `Android.bp` **splits the call stack**:
- `TelecomLib`: modern service implementation, AIDL/internal framework source groups, `telecom_module_bugfix_flags-java`, `framework-telecom.impl`, `services.core`, min SDK 36.
- `Telecom` plus `TelecomShim`: distinct system service APK/shim selection for legacy platform and modular path.
- `TelecomUi` and `TelecomServiceResources`: separately signed/packaged resources and UI with conditional certificates.
- `telecom-strings`, `shared-telecom-lib`, `telecom-proto-enums` and `telecom-resource-id-lib`, with `apex_available: ["com.android.telephonycore", "//apex_available:platform"]`.
- Product flag `RELEASE_TELECOM_MAINLINE_MODULE` controls availability and certificates. The flag's **actual product value** and assembled modules have NOT been checked; do not claim the APEX path is installed merely because its source exists.
- Official Android17 code contains `legacy-src/`, `shim/`, `TelecomUi/` and `flags/`; these source directories are absent in old PE Telecomm.

Upstream exact sources: https://android.googlesource.com/platform/packages/services/Telecomm/+/refs/tags/android-17.0.0_r1/Android.bp and https://android.googlesource.com/platform/packages/modules/Telecom/+/refs/tags/android-17.0.0_r1 .

## Historical PE deltas checked

| Commit | Old action | Android17 decision |
| --- | --- | --- |
| `70e0d533d93af5a573d00900e3b3fc7e764982e4` (2019) | `CallLogManager.sendAddCallBroadcast` uses `sendBroadcastAsUser(..., UserHandle.SYSTEM, PERMISSION_PROCESS_CALLLOG_INFO)` rather than an unqualified send | **Do not cherry-pick blind**. Cross-user call log event privacy and correct caller/user identity must be verified in the official Android17 `CallLogManager`. The legacy patch's `UserHandle.SYSTEM` assumption is not automatically valid for newer modular telecom/multiuser behavior. |
| `a604311f86ea8136ca2ac9f9ff0af7fa57ee3f42` (2023) | Reject `PhoneAccount` icon content URI using another profile's encoded user component, through `validateAccountIconUserBoundary`; adds unit test | **Security guard**: verify upstream AOSP17 `registerPhoneAccount` and tests first, including malformed encoded user, content URI validation and work-profile isolation. Never replace current protections with an old single-check implementation. |
| Android14 r21 merge | Updates old Telecom build/service APIs | **Not a port**. Android17 has different Soong/SDK, AConfig, UI and package activation model. |

This is a prioritized initial source-history audit, **not** certification that every historical commit was classified. No Telecomm runtime code was modified.

## Security and mondrian acceptance gates

1. Confirm effective product `RELEASE_TELECOM_MAINLINE_MODULE`, `com.android.telephonycore` APEX, `TelecomShim`/platform Telecom selection and matching signatures; avoid duplicate Telecom service registration.
2. Compile Android17 Soong TelecomLib, Telecom, TelecomUi, TelecomShim, Telephony module, Dialer and their AIDL/flag dependencies. Prove there are no obsolete duplicate service definitions or missing modules.
3. Verify emergency dialing, audio routes, in-call UI, call waiting, VoIP/IMS, radio/telephony integration, multi-SIM where supported, phone-account icon/profile isolation and background restriction security.
4. Verify Telecom permissions, package/signature allowlists, cross-user grants, call-log/database privacy, services, accessibility, VoIP and role-holder behavior.
5. Run `TelecomUnitTests`, `CtsTelecomTestCases`, `CtsTelephony2TestCases`, `CtsTelephony3TestCases`, role/permission and emergency/call-routing tests. Test real calls/IMS only with appropriately controlled device setups.
6. Verify all product integrations on **independent** PixelExperience-Reborn Android17 mondrian + sm8450-common trees; existing LF52406 LineageOS-based trees are *hardware reference only*, not approved product inheritance.
7. Treat call privacy, emergency and radio functionality as release blockers; do not announce functional calling/IMS until verified.

## Current result

- [x] Historical source revision, known PE patches and AOSP17 exact revision/tree identified.
- [x] Official AOSP17 Mainline/UI/APEX Soong split identified.
- [x] Source-only risk-inventory regression test created.
- [ ] Exact official Android17 Telecomm source sync / full module graph verification.
- [ ] `m Telecom`, real Android17 platform build, CTS and mondrian runtime tests.
- [ ] Independently authored PE-Reborn device trees and vendor/kernel integration.

**Decision:** keep official AOSP17 Telecomm/Telecom/Telephony sources in the staged manifest. Historical PE source is not enabled. This audit does not prove a working telephone stack.
