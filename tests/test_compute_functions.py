import json
import unittest
from pathlib import Path

from consts import COMPUTE_FUNCTIONS, planet_parser
from logger import L
from transform import DatapackGenerater, filedata, modify_file_data


class ComputeFunctionsTest(unittest.TestCase):
    def compile(self, source, version="26.3"):
        filedata.clear()
        generator = DatapackGenerater(
            version, filename=str(Path("example/test2.planet")), logger_level=L())
        tree = planet_parser.parse(modify_file_data(source))
        generator.pre_scan_functions(tree)
        generator.transform(tree)
        return dict(filedata)

    def test_all_math_functions_and_provider_shapes(self):
        for name, (mode, fields) in COMPUTE_FUNCTIONS.items():
            with self.subTest(name=name):
                args = "2, 3, 4" if fields == ("inputs",) else ", ".join("2" for _ in fields)
                output = "".join(self.compile(f"var result = {name}({args})\n").values())
                line = next(line for line in output.splitlines() if "set compute" in line)
                provider = json.loads(line.split(f"set compute default {mode} ")[1])
                self.assertEqual(provider["type"], f"minecraft:{name}")
                self.assertEqual(set(provider), {"type", *fields})
                if fields == ("inputs",):
                    self.assertEqual(provider["inputs"], [2, 3, 4])

    def test_float_literals_are_not_rounded(self):
        output = "".join(self.compile("var a = avg(1.5, 2.25f, -3.5d)\n").values())
        provider = json.loads(next(line.split("set compute default float ")[1]
                                  for line in output.splitlines() if "set compute" in line))
        self.assertEqual(provider["inputs"], [1.5, 2.25, -3.5])
        self.assertNotIn("run data get", output)

    def test_nested_calls_use_macros_and_preserve_values(self):
        files = self.compile("var a = -2.5\nvar result = avg(abs(a), sqrt(9), 4.5)\n")
        output = "".join(files.values())
        self.assertEqual(output.count('"type":"minecraft:abs"'), 1)
        self.assertEqual(output.count('"type":"minecraft:sqrt"'), 1)
        self.assertEqual(output.count('"type":"minecraft:avg"'), 1)
        self.assertIn("with storage 40planet:value data", output)
        self.assertIn('$data modify storage', output)
        self.assertNotIn("run data get", output)
        self.assertIn("data remove storage 40planet:value data.", output)

    def test_repeated_function_return_is_captured_before_next_call(self):
        files = self.compile("def number() { return 3 }\nvar result = avg(number(), number())\n")
        load = next(text for path, text in files.items() if path.endswith("load.mcfunction"))
        calls = [i for i, line in enumerate(load.splitlines()) if line == "function pack:number"]
        self.assertEqual(len(calls), 2)
        between = load.splitlines()[calls[0] + 1:calls[1]]
        self.assertTrue(any("set from storage" in line for line in between))

    def test_version_gate_and_legacy_round(self):
        for name in COMPUTE_FUNCTIONS:
            if name == "round":
                continue
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "26.3 or later"):
                    self.compile(f"var x = {name}(1)\n", "26.2")
        output = "".join(self.compile("var x = round(2.5)\n", "26.2").values())
        self.assertNotIn("compute", output)
        self.assertIn("compute default float", "".join(self.compile("var x = abs(-2)\n", 260400).values()))

    def test_invalid_arguments(self):
        for expression, message in [("abs()", "expected"), ("sqrt(1,2)", "expected"),
                                    ("avg()", "at least"), ('abs("text")', "numeric"),
                                    ("abs(missing)", "not defined"),
                                    ("floor_div(1.5,2)", "32-bit integer")]:
            with self.subTest(expression=expression):
                with self.assertRaisesRegex(ValueError, message):
                    self.compile(f"var x = {expression}\n")

    def test_numeric_conversion_providers(self):
        cases = [
            ("int(-2.9)", "integer", {"type": "minecraft:from_float", "input": -2.9}),
            ("float(7)", "float", {"type": "minecraft:from_int", "input": 7}),
            ("int(2147483647)", "integer", 2147483647),
            ("int(-2147483648)", "integer", -2147483648),
            ("float(2.5)", "float", 2.5),
            ('int("-2.9")', "integer", {"type": "minecraft:from_float", "input": -2.9}),
            ('float("7")', "float", {"type": "minecraft:from_int", "input": 7}),
            ("int(2.0f)", "integer", {"type": "minecraft:from_float", "input": 2.0}),
        ]
        for expression, mode, expected in cases:
            with self.subTest(expression=expression):
                output = "".join(self.compile(f"var x = {expression}\n").values())
                line = next(line for line in output.splitlines() if "set compute" in line)
                self.assertEqual(json.loads(line.split(f"set compute default {mode} ")[1]), expected)

    def test_conversion_variables_keep_integer_precision_and_fractional_values(self):
        output = "".join(self.compile(
            "var n = 2147483647\nvar same = int(n)\n"
            "var f = -2.9\nvar truncated = int(f)\nvar same_float = float(f)\n"
        ).values())
        self.assertIn('"type":"minecraft:from_float"', output)
        self.assertIn('"type":"minecraft:from_int"', output)
        self.assertIn('"type":"minecraft:constant","value":$(', output)
        self.assertIn("execute store success storage", output)
        self.assertIn("execute unless data storage", output)
        self.assertIn("set compute default integer {\"type\":\"minecraft:storage\"", output)
        self.assertNotIn("function basic:", output)

    def test_nested_conversions_and_legacy_versions(self):
        output = "".join(self.compile("var x = float(int(avg(1, 2)))\n").values())
        self.assertEqual(output.count('"type":"minecraft:avg"'), 1)
        for version in ("1.21", "26.2"):
            self.assertNotIn("compute", "".join(self.compile("var x = int(2.9)\n", version).values()))
        self.assertNotIn("compute", "".join(self.compile("var x = float(2)\n", "1.21").values()))
        with self.assertRaises(ValueError):
            self.compile("var x = float(2)\n", "26.2")
        self.assertIn("compute", "".join(self.compile("var x = float(2)\n", 260400).values()))

    def test_conversion_invalid_arguments(self):
        for expression, message in [("int()", "expected"), ("float(1,2)", "expected"),
                                    ('int("text")', "number"), ('float("text")', "number"),
                                    ("float(missing)", "not defined")]:
            with self.subTest(expression=expression):
                with self.assertRaisesRegex(ValueError, message):
                    self.compile(f"var x = {expression}\n")


if __name__ == "__main__":
    unittest.main()
