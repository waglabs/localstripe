import contextvars


# The version used when a request sends no Stripe-Version header. It matches
# the version wagapi pins today.
DEFAULT_API_VERSION = '2018-11-08'

CUSTOMER_BALANCE_RENAMED = '2019-10-17'
CUSTOMER_LISTS_EXPANDABLE = '2020-08-27'
PAYMENT_INTENT_CHARGES_REMOVED = '2022-11-15'
CHARGE_REFUNDS_EXPANDABLE = '2022-11-15'
CAPTURE_METHOD_DEFAULTS_TO_ASYNC = '2024-04-10'
PARTIAL_CAPTURE_CREATES_NO_REFUND = '2025-03-31'
PAYMENT_METHOD_TYPES_REMOVED = '2026-09-30'

_api_version = contextvars.ContextVar('api_version',
                                      default=DEFAULT_API_VERSION)


def set_api_version(version):
    _api_version.set(version or DEFAULT_API_VERSION)


def current_api_version():
    return _api_version.get()


def api_version_is_at_least(date):
    # Named versions such as 2025-03-31.basil order by their date part.
    return current_api_version().split('.')[0] >= date
