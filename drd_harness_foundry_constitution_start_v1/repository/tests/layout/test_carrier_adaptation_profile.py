from drd_harness.rules.layout import Carrier, CarrierAdaptationProfile, CarrierRule
from drd_harness.validators.layout_completeness import validate_carrier_adaptation_profile


def rule(label):
    return CarrierRule(
        arrangement=f"{label} arrangement keeps readable layout.",
        width_behavior="Wraps or stacks before minimum readable width is violated.",
        height_scroll_behavior="Required information remains accessible by vertical scroll.",
        navigation_placement="Navigation remains visible in the carrier-appropriate region.",
        safe_area_or_system_bars="Safe area or system bars are respected.",
        input_keyboard_behavior="Keyboard or input insets do not hide required controls.",
        platform_constraints=[f"{label} platform constraint"],
    )


def full_profile(**overrides):
    values = {
        "carrier_profile_id": "CARRIER-PROJECT",
        "required_carriers": [
            Carrier.DESKTOP,
            Carrier.TABLET,
            Carrier.MOBILE,
            Carrier.MOBILE_IOS,
            Carrier.MOBILE_MATERIAL,
        ],
        "carrier_rules": {
            Carrier.DESKTOP: rule("desktop"),
            Carrier.TABLET: rule("tablet"),
            Carrier.MOBILE: rule("mobile"),
            Carrier.MOBILE_IOS: rule("iOS"),
            Carrier.MOBILE_MATERIAL: rule("Material"),
        },
    }
    values.update(overrides)
    return CarrierAdaptationProfile(**values)


def test_full_carrier_profile_passes():
    assert validate_carrier_adaptation_profile(full_profile()) == []


def test_missing_required_carrier_profile_fails():
    profile = full_profile(carrier_rules={Carrier.DESKTOP: rule("desktop")})

    findings = validate_carrier_adaptation_profile(profile)

    assert "PL007" in {finding.code for finding in findings}


def test_ios_and_material_require_mobile_context():
    profile = full_profile(required_carriers=[Carrier.MOBILE_IOS, Carrier.MOBILE_MATERIAL])

    findings = validate_carrier_adaptation_profile(profile)

    assert "PL007" in {finding.code for finding in findings}
