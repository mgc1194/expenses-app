"""
tests/banking/test_utils.py — Unit tests for banking.utils.
"""

from banking.utils import detect_account_type


class TestDetectAccountType:
    def test_detects_capital_one_checking(self):
        assert detect_account_type('360Checking.csv') == 'co-checking'

    def test_detects_capital_one_savings(self):
        assert detect_account_type('360PerformanceSavings.csv') == 'co-savings'

    def test_detects_quicksilver(self):
        assert detect_account_type('transaction_download.csv') == 'co-quicksilver'

    def test_detects_sofi_checking(self):
        assert detect_account_type('SOFI-Checking-123.csv') == 'sofi-checking'

    def test_detects_sofi_savings(self):
        assert detect_account_type('SOFI-Savings-456.csv') == 'sofi-savings'

    def test_detects_wells_fargo_checking(self):
        assert detect_account_type('WF-Checking.csv') == 'wf-checking'

    def test_detects_wells_fargo_savings(self):
        assert detect_account_type('WF-Savings.csv') == 'wf-savings'

    def test_detects_amex_activity(self):
        assert detect_account_type('activity.csv') == 'amex-delta'

    def test_detects_chase(self):
        assert detect_account_type('Chase1234.csv') == 'chase'

    def test_detects_discover(self):
        assert detect_account_type('Discover-Export.csv') == 'discover'

    def test_returns_none_for_unknown_filename(self):
        assert detect_account_type('unknown_bank.csv') is None

    def test_returns_none_for_empty_filename(self):
        assert detect_account_type('') is None

    def test_detection_is_case_sensitive(self):
        # Our patterns are case-sensitive
        assert detect_account_type('sofi-checking.csv') is None

    def test_matches_substring_anywhere_in_filename(self):
        assert detect_account_type('SOFI-Savings-0000-2020-01-01T00_00_00.csv') == 'sofi-savings'
