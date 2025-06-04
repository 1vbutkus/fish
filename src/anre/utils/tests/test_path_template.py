import unittest
from datetime import date, datetime

from anre.utils.path_template import PathTemplate


class TestPathTemplate(unittest.TestCase):
    def test_parse_template(self) -> None:
        template = "/path/{to}/{file}"
        pt = PathTemplate(template)
        self.assertEqual(pt.parameters, {"to", "file"})

    def test_parse_template_invalid_curly_braces(self) -> None:
        template = "/path/{to}/{file}/{invalid}}"
        with self.assertRaises(ValueError):
            PathTemplate(template)

    def test_format_arg(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        self.assertEqual(pt._format_arg("to", "value"), "value")
        self.assertEqual(pt._format_arg("to", 123), "123")
        self.assertEqual(
            pt._format_arg("to", datetime(2023, 10, 1, 12, 30, 45)), "2023-10-01T12_30_45"
        )
        self.assertEqual(pt._format_arg("to", date(2023, 10, 1)), "2023-10-01")

    def test_format_arg_invalid_slash(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        with self.assertRaises(ValueError):
            pt._format_arg("to", "in/valid")

    def test_format_arg_invalid_type(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        with self.assertRaises(ValueError) as cm:
            pt._format_arg("to", 1.23)  # type: ignore[arg-type]
        self.assertIn("Unsupported to value type", str(cm.exception))

        with self.assertRaises(ValueError):
            pt._format_arg("to", ["list"])  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            pt._format_arg("to", {"dict": "value"})  # type: ignore[arg-type]

    def test_format(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        self.assertEqual(pt.format(to="value", file="name"), "/path/value/name")

    def test_format_missing_params(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        with self.assertRaises(ValueError):
            pt.format(to="value")

    def test_format_extra_params(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        with self.assertRaises(ValueError):
            pt.format(to="value", file="name", extra="param")

    def test_format_with_integers(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        self.assertEqual(pt.format(to=123, file=456), "/path/123/456")

    def test_format_with_dates(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        self.assertEqual(
            pt.format(to=date(2023, 10, 1), file=date(2023, 10, 2)), "/path/2023-10-01/2023-10-02"
        )

    def test_format_with_datetimes(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        self.assertEqual(
            pt.format(to=datetime(2023, 10, 1, 12, 30, 45), file=datetime(2023, 10, 2, 12, 30, 45)),
            "/path/2023-10-01T12_30_45/2023-10-02T12_30_45",
        )

    def test_format_with_mixed_types(self) -> None:
        pt = PathTemplate("/path/{to}/{file}")
        self.assertEqual(pt.format(to="value", file=123), "/path/value/123")
