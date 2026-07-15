"""Behavioral evidence for the Chapter 26 iteration companion."""

import unittest

from iteration_pipeline import (
    MAX_SQUARES,
    bounded_squares,
    countdown,
    flatten,
    managed_values,
    reciprocals,
    strict_pairs,
)


class EssentialSyntaxTests(unittest.TestCase):
    def test_comprehensions_preserve_documented_collection_semantics(self):
        scores = [3, 5, 8]
        names = ["Noor", "Frej", "Taha"]

        self.assertEqual([6, 10, 16], [score * 2 for score in scores])
        self.assertEqual(
            {"Noor": 4, "Frej": 4, "Taha": 4},
            {name: len(name) for name in names},
        )
        self.assertEqual({4}, {len(name) for name in names})
        self.assertEqual([], [value for value in []])

    def test_enumerate_uses_the_declared_display_start(self):
        self.assertEqual(
            [(1, "Noor"), (2, "Frej")],
            list(enumerate(["Noor", "Frej"], start=1)),
        )

    def test_non_strict_zip_truncation_is_deliberate_and_observable(self):
        self.assertEqual(
            [("Noor", 7)],
            list(zip(["Noor", "Frej"], [7])),
        )


class StrictPairsTests(unittest.TestCase):
    def test_preserves_equal_length_pair_order(self):
        self.assertEqual(
            [("Noor", 7), ("Frej", 9)],
            strict_pairs(["Noor", "Frej"], [7, 9]),
        )

    def test_accepts_two_empty_inputs(self):
        self.assertEqual([], strict_pairs([], []))

    def test_rejects_unequal_lengths(self):
        with self.assertRaises(ValueError):
            strict_pairs(["Noor", "Frej"], [7])


class CountdownTests(unittest.TestCase):
    def test_counts_down_to_one(self):
        self.assertEqual([3, 2, 1], list(countdown(3)))

    def test_zero_is_an_empty_boundary(self):
        self.assertEqual([], list(countdown(0)))

    def test_rejects_invalid_bounds_when_consumed(self):
        for invalid in (-1, MAX_SQUARES + 1):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    list(countdown(invalid))
        for invalid in (True, 1.5, "3"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    list(countdown(invalid))

    def test_exhaustion_is_one_shot_and_recovery_recreates_generator(self):
        cursor = countdown(1)
        self.assertEqual(1, next(cursor))
        with self.assertRaises(StopIteration):
            next(cursor)
        self.assertEqual([1], list(countdown(1)))


class BoundedSquaresTests(unittest.TestCase):
    def test_produces_first_five_squares(self):
        self.assertEqual([0, 1, 4, 9, 16], list(bounded_squares(5)))

    def test_zero_limit_consumes_nothing(self):
        self.assertEqual([], list(bounded_squares(0)))

    def test_rejects_invalid_limits_when_consumed(self):
        for invalid in (-1, MAX_SQUARES + 1):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    list(bounded_squares(invalid))
        for invalid in (False, 2.5, "5"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    list(bounded_squares(invalid))


class DelegationTests(unittest.TestCase):
    def test_flattens_finite_groups_in_order(self):
        self.assertEqual(
            ["A", "B", "C"],
            list(flatten([["A", "B"], [], ["C"]])),
        )

    def test_empty_outer_input_is_empty(self):
        self.assertEqual([], list(flatten([])))


class DelayedFailureTests(unittest.TestCase):
    def test_failure_happens_at_the_invalid_consumption_step(self):
        cursor = reciprocals([2, 0, 4])
        self.assertEqual(0.5, next(cursor))
        with self.assertRaises(ZeroDivisionError):
            next(cursor)

    def test_recovery_uses_corrected_input_and_a_new_generator(self):
        self.assertEqual([0.5, 0.25], list(reciprocals([2, 4])))


class CleanupTests(unittest.TestCase):
    def test_explicit_close_runs_cleanup_once_after_partial_consumption(self):
        events = []
        cursor = managed_values(["A", "B"], lambda: events.append("closed"))

        self.assertEqual("A", next(cursor))
        self.assertEqual([], events)
        cursor.close()
        self.assertEqual(["closed"], events)

        cursor.close()
        self.assertEqual(["closed"], events)
        with self.assertRaises(StopIteration):
            next(cursor)

    def test_normal_exhaustion_also_runs_cleanup_once(self):
        events = []
        self.assertEqual(
            ["A", "B"],
            list(managed_values(["A", "B"], lambda: events.append("closed"))),
        )
        self.assertEqual(["closed"], events)

    def test_non_callable_cleanup_is_rejected_when_consumed(self):
        cursor = managed_values(["A"], None)
        with self.assertRaisesRegex(TypeError, "close must be callable"):
            next(cursor)


if __name__ == "__main__":
    unittest.main()
