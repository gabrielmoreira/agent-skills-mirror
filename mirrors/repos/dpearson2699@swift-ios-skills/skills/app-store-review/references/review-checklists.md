# App Store Review Checklists

## Contents
- App Review Information Checklist
- Privacy Manifest Checklist
- In-App Purchase Checklist
- HIG Compliance Checklist
- Pre-Submission Checklist

## App Review Information Checklist

Use this to avoid Guideline 2.1 rejections:

- [ ] Demo credentials provided in App Review Information notes (if login required)
- [ ] Demo account works and has access to all features
- [ ] All screens have real content (no placeholders or Lorem Ipsum)
- [ ] No broken links or dead-end flows
- [ ] All hardware-required features have fallback or reviewer instructions

## Privacy Manifest Checklist

Verify PrivacyInfo.xcprivacy completeness:

- [ ] `PrivacyInfo.xcprivacy` exists in app bundle
- [ ] All required API categories are declared with reason codes
- [ ] `NSPrivacyTracking` is true only if tracking occurs
- [ ] Third-party SDK manifests present and up to date
- [ ] Privacy nutrition labels match actual data collection

## In-App Purchase Checklist

- [ ] All digital goods use StoreKit IAP
- [ ] Subscription pricing and auto-renewal terms shown before purchase
- [ ] Restore purchases button present and functional
- [ ] Ask-to-buy and interrupted purchases handled
- [ ] Transaction verification uses StoreKit 2 or server-side verification

## HIG Compliance Checklist

### Navigation
- [ ] `NavigationStack` used (not `NavigationView`)
- [ ] System back chevron used; no custom back icons
- [ ] Tab bar uses <= 5 tabs; use More tab if needed
- [ ] Avoid hamburger menus

### Modals and Sheets
- [ ] Sheets have a visible dismiss control
- [ ] Full-screen modals have close/done button
- [ ] Alerts use system alert styles

### System Feature Support
- [ ] Dark Mode renders correctly
- [ ] Dynamic Type supported throughout
- [ ] iPad multitasking supported (Slide Over, Split View)
- [ ] Dynamic Island / Live Activities render correctly when used
- [ ] System gestures not disabled

### Widgets and Live Activities
- [ ] Widgets show real content (not placeholders)
- [ ] Timelines update meaningfully
- [ ] Live Activities show time-sensitive info
- [ ] Lock Screen widgets are legible at small sizes

## Pre-Submission Checklist

### Completeness
- [ ] No placeholder or test content
- [ ] All features functional without special hardware
- [ ] Demo credentials provided
- [ ] No dead-end screens

### Metadata
- [ ] App name matches functionality
- [ ] Screenshots are real app screenshots
- [ ] Description contains no prices or competitor mentions
- [ ] Category is correct

### Privacy
- [ ] Privacy manifest present with required reason codes
- [ ] Third-party SDK manifests verified
- [ ] Privacy policy URL present and accessible
- [ ] Nutrition labels match actual data collection
- [ ] ATT prompt only if tracking occurs

### Payments
- [ ] Digital content uses IAP
- [ ] Subscription terms visible before purchase
- [ ] No external payment links
- [ ] Free trial terms clear
- [ ] Restore purchases implemented

### Design
- [ ] Standard navigation patterns used
- [ ] Dark Mode supported
- [ ] Dynamic Type supported
- [ ] No custom alerts mimicking system alerts
- [ ] Launch screen not an ad
- [ ] Empty states provide guidance

### Technical
- [ ] Built with current Xcode GM
- [ ] No private API usage
- [ ] No dynamic code execution
- [ ] Entitlements justified with usage descriptions
- [ ] Background modes justified and used
- [ ] Minimum deployment target covers latest two major iOS versions
