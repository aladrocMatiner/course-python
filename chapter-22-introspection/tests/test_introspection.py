import inspect
import unittest

from chapter_22 import describe2, require_named_params


def accepts_named(user_id, payload):
    return user_id, payload


def positional_only(user_id, payload, /):
    return user_id, payload


class HookedValue:
    property_calls = 0

    @property
    def status(self):
        type(self).property_calls += 1
        return "ready"


class IntrospectionTests(unittest.TestCase):
    def test_real_module_import_and_signature_contract(self) -> None:
        require_named_params(accepts_named, ["user_id", "payload"])
        with self.assertRaises(TypeError):
            require_named_params(positional_only, ["user_id", "payload"])

    def test_static_lookup_does_not_execute_property(self) -> None:
        value = HookedValue()
        HookedValue.property_calls = 0
        descriptor = inspect.getattr_static(value, "status")
        self.assertIsInstance(descriptor, property)
        self.assertEqual(0, HookedValue.property_calls)
        self.assertEqual("ready", getattr(value, "status"))
        self.assertEqual(1, HookedValue.property_calls)

    def test_describe2_handles_empty_sequence(self) -> None:
        self.assertFalse(describe2([])["has_items"])


if __name__ == "__main__":
    unittest.main()
