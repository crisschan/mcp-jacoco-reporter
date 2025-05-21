import unittest
import os
import json
import sys
from io import StringIO
from contextlib import redirect_stderr

# Adjust path to import JaCoCoReport from the parent directory or the location of jacoco_reporter.py
# This assumes test_jacoco_reporter.py is in the same directory as jacoco_reporter.py or the path is set up
try:
    from jacoco_reporter import JaCoCoReport
except ImportError:
    # Fallback for cases where the script is run from a different context
    # You might need to adjust this based on your project structure
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from jacoco_reporter import JaCoCoReport


class TestJaCoCoReport(unittest.TestCase):
    SAMPLE_VALID_XML_PATH = "sample_valid_report.xml"
    SAMPLE_INVALID_XML_PATH = "sample_invalid_report.xml"
    TEMP_FILES = [SAMPLE_VALID_XML_PATH, SAMPLE_INVALID_XML_PATH]

    SAMPLE_VALID_XML_CONTENT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.1//EN" "report.dtd">
<report name="Sample Report">
    <package name="com/example/package1">
        <sourcefile name="ClassA.java">
            <line nr="10" mi="0" ci="5" mb="0" cb="2"/>
            <line nr="11" mi="1" ci="0" mb="1" cb="0"/>
            <line nr="12" mi="1" ci="1" mb="1" cb="1"/>
            <line nr="13" mi="0" ci="3" mb="0" cb="0"/>
            <line nr="14" mi="0" ci="4" mb="1" cb="1"/>
        </sourcefile>
        <sourcefile name="ClassB.java">
            <line nr="20" mi="0" ci="0" mb="0" cb="0"/>
            <line nr="21" mi="0" ci="invalid" mb="0" cb="0"/>
            <line nr="22" mi="0" ci="1" mb="0" cb="0"/> <!-- Valid line after invalid 'nr' on next -->
            <line mi="1" ci="0" mb="0" cb="0"/> <!-- Missing 'nr' -->
        </sourcefile>
    </package>
    <package name="com/example/empty_package">
        <sourcefile name="EmptyFile.java">
        </sourcefile>
    </package>
    <package> 
        <sourcefile name="NoPackageName.java">
            <line nr="30" mi="0" ci="1" mb="0" cb="1"/>
        </sourcefile>
    </package>
    <package name="com/example/no_lines_in_file_attribs_missing">
        <sourcefile> 
             <line nr="40" mi="0" ci="1" mb="0" cb="1"/>
        </sourcefile>
    </package>
    <package name="com/example/missing_attributes">
        <sourcefile name="MissingAttributes.java">
            <line nr="50" ci="1"/> <!-- mi missing, mb missing, cb missing -->
            <line nr="51" mi="1"/> <!-- ci missing, mb missing, cb missing -->
            <line nr="52" mb="1"/> <!-- ci missing, mi missing, cb missing -->
            <line nr="53" cb="1"/> <!-- ci missing, mi missing, mb missing -->
            <line nr="54" /> <!-- all missing -->
        </sourcefile>
    </package>
</report>
    """

    SAMPLE_INVALID_XML_CONTENT = "<report><unclosed_tag></report>"

    def _write_temp_xml(self, filepath, content):
        with open(filepath, "w") as f:
            f.write(content)

    def setUp(self):
        self._write_temp_xml(self.SAMPLE_VALID_XML_PATH, self.SAMPLE_VALID_XML_CONTENT)
        self._write_temp_xml(self.SAMPLE_INVALID_XML_PATH, self.SAMPLE_INVALID_XML_CONTENT)

    def tearDown(self):
        for temp_file in self.TEMP_FILES:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        # Clean up any other specific files created in tests
        if os.path.exists("specific_test.xml"):
            os.remove("specific_test.xml")

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            JaCoCoReport("non_existent_file.xml")

    def test_invalid_xml(self):
        with self.assertRaises(ValueError) as context: # The class wraps ET.ParseError in ValueError
            JaCoCoReport(self.SAMPLE_INVALID_XML_PATH)
        self.assertTrue("Failed to parse the XML file" in str(context.exception))

    def test_basic_parsing_all_types(self):
        reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH) # Default is all types
        data = json.loads(reporter.jacoco_to_json())

        self.assertGreater(len(data), 0)
        
        class_a_data = next((item for item in data if item["sourcefile"] == "ClassA.java"), None)
        self.assertIsNotNone(class_a_data)
        self.assertEqual(class_a_data["package"], "com/example/package1")
        
        # Line 10: mi="0" ci="5" (full) / mb="0" cb="2" (full)
        self.assertIn(10, class_a_data["lines"]["fullcovered"])
        self.assertIn(10, class_a_data["branch"]["fullcovered"])
        # Line 11: mi="1" ci="0" (no) / mb="1" cb="0" (no)
        self.assertIn(11, class_a_data["lines"]["nocovered"])
        self.assertIn(11, class_a_data["branch"]["nocovered"])
        # Line 12: mi="1" ci="1" (partial) / mb="1" cb="1" (partial)
        self.assertIn(12, class_a_data["lines"]["partiallycovered"])
        self.assertIn(12, class_a_data["branch"]["partiallycovered"])
        # Line 13: mi="0" ci="3" (full) / mb="0" cb="0" (no actual branch, so not in branch output)
        self.assertIn(13, class_a_data["lines"]["fullcovered"])
        self.assertNotIn(13, class_a_data["branch"].get("fullcovered", []))
        self.assertNotIn(13, class_a_data["branch"].get("nocovered", []))
        self.assertNotIn(13, class_a_data["branch"].get("partiallycovered", []))
        # Line 14: mi="0" ci="4" (full) / mb="1" cb="1" (partial)
        self.assertIn(14, class_a_data["lines"]["fullcovered"])
        self.assertIn(14, class_a_data["branch"]["partiallycovered"])

    def test_covered_types_filtering_nocovered(self):
        reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH, covered_types=['nocovered'])
        data = json.loads(reporter.jacoco_to_json())
        class_a_data = next((item for item in data if item["sourcefile"] == "ClassA.java"), None)
        self.assertIsNotNone(class_a_data)
        self.assertIn(11, class_a_data["lines"]["nocovered"])
        self.assertNotIn("fullcovered", class_a_data["lines"])
        self.assertNotIn("partiallycovered", class_a_data["lines"])
        self.assertIn(11, class_a_data["branch"]["nocovered"])
        self.assertNotIn("fullcovered", class_a_data["branch"])
        self.assertNotIn("partiallycovered", class_a_data["branch"])

    def test_covered_types_filtering_partiallycovered(self):
        reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH, covered_types=['partiallycovered'])
        data = json.loads(reporter.jacoco_to_json())
        class_a_data = next((item for item in data if item["sourcefile"] == "ClassA.java"), None)
        self.assertIsNotNone(class_a_data)
        self.assertIn(12, class_a_data["lines"]["partiallycovered"])
        self.assertIn(14, class_a_data["branch"]["partiallycovered"]) # from line 14
        self.assertNotIn("fullcovered", class_a_data["lines"])
        self.assertNotIn("nocovered", class_a_data["lines"])

    def test_covered_types_filtering_fullcovered(self):
        reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH, covered_types=['fullcovered'])
        data = json.loads(reporter.jacoco_to_json())
        class_a_data = next((item for item in data if item["sourcefile"] == "ClassA.java"), None)
        self.assertIsNotNone(class_a_data)
        self.assertIn(10, class_a_data["lines"]["fullcovered"])
        self.assertIn(13, class_a_data["lines"]["fullcovered"])
        self.assertIn(14, class_a_data["lines"]["fullcovered"])
        self.assertIn(10, class_a_data["branch"]["fullcovered"])
        self.assertNotIn("nocovered", class_a_data["lines"])
        self.assertNotIn("partiallycovered", class_a_data["lines"])

    def test_covered_types_filtering_empty(self):
        reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH, covered_types=[])
        data = json.loads(reporter.jacoco_to_json())
        # Expect data to be empty or sourcefiles to have empty lines/branch lists
        for item in data:
            self.assertEqual(len(item["lines"]), 0)
            self.assertEqual(len(item["branch"]), 0)
        
        # More robust: check if ClassA.java is present but has empty coverage
        class_a_item = next((item for item in data if item["sourcefile"] == "ClassA.java"), None)
        if class_a_item: # It might be filtered out if it has no reportable lines/branches
             self.assertEqual(len(class_a_item["lines"]), 0)
             self.assertEqual(len(class_a_item["branch"]), 0)


    def test_edge_case_empty_sourcefile(self):
        reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH)
        data = json.loads(reporter.jacoco_to_json())
        empty_file_data = next((item for item in data if item["sourcefile"] == "EmptyFile.java"), None)
        # As per current implementation, if a sourcefile has no lines, it might not be in the output
        # if it results in empty filtered_lines and filtered_branch.
        # If it *is* there, its lines/branches should be empty.
        if empty_file_data:
            self.assertEqual(empty_file_data["lines"], {})
            self.assertEqual(empty_file_data["branch"], {})
        else:
            # This is also acceptable if the filtering logic removes it.
            # To be more precise, we should check that it's not there because it had no lines to begin with.
            # The current code adds to result if filtered_lines or filtered_branch is non-empty.
            # EmptyFile.java will result in empty lines and branch, so it should not be in the result.
            self.assertIsNone(empty_file_data, "EmptyFile.java should not be in the output if it has no coverage lines.")


    def test_edge_case_zero_counts(self): # mi=0, ci=0, mb=0, cb=0
        reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH, covered_types=['nocovered', 'partiallycovered', 'fullcovered'])
        data = json.loads(reporter.jacoco_to_json())
        class_b_data = next((item for item in data if item["sourcefile"] == "ClassB.java"), None)
        self.assertIsNotNone(class_b_data)
        # Line 20: mi="0" ci="0" mb="0" cb="0" - this is not nocovered, partially, or full. It's "not covered" but has 0 missed.
        # The _classify_coverage_item returns None for status_type in this case.
        # So line 20 should not appear in any list.
        self.assertNotIn(20, class_b_data["lines"].get("nocovered", []))
        self.assertNotIn(20, class_b_data["lines"].get("partiallycovered", []))
        self.assertNotIn(20, class_b_data["lines"].get("fullcovered", []))
        self.assertNotIn(20, class_b_data["branch"].get("nocovered", []))
        self.assertNotIn(20, class_b_data["branch"].get("partiallycovered", []))
        self.assertNotIn(20, class_b_data["branch"].get("fullcovered", []))


    def test_edge_case_missing_package_sourcefile_names(self):
        reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH)
        data = json.loads(reporter.jacoco_to_json())
        
        no_pkg_name_data = next((item for item in data if item["sourcefile"] == "NoPackageName.java"), None)
        self.assertIsNotNone(no_pkg_name_data)
        self.assertEqual(no_pkg_name_data["package"], "UnknownPackage")

        no_src_name_data = next((item for item in data if item["package"] == "com/example/no_lines_in_file_attribs_missing"), None)
        self.assertIsNotNone(no_src_name_data)
        self.assertEqual(no_src_name_data["sourcefile"], "UnknownSourcefile")

    def test_attribute_conversion_errors_and_missing_nr(self):
        f = StringIO()
        with redirect_stderr(f):
            reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH, covered_types=['nocovered','fullcovered','partiallycovered'])
            data = json.loads(reporter.jacoco_to_json())
        
        stderr_output = f.getvalue()
        
        # For ClassB.java, line 21 (invalid 'ci')
        self.assertIn("Warning: Invalid number format for attributes in line 21", stderr_output)
        self.assertIn("ClassB.java", stderr_output)
        
        # For ClassB.java, line with missing 'nr'
        self.assertIn("Warning: Missing 'nr' attribute for a line in ClassB.java", stderr_output)

        class_b_data = next((item for item in data if item["sourcefile"] == "ClassB.java"), None)
        self.assertIsNotNone(class_b_data)
        
        # Line 21 should be skipped, so not in any list
        self.assertNotIn(21, class_b_data["lines"].get("fullcovered", []))
        self.assertNotIn(21, class_b_data["lines"].get("nocovered", []))
        self.assertNotIn(21, class_b_data["lines"].get("partiallycovered", []))
        
        # Line 22 (valid) should still be processed
        self.assertIn(22, class_b_data["lines"]["fullcovered"]) # Assuming ci=1, mi=0 -> fullcovered based on sample

    def test_missing_numeric_attributes_default_to_zero(self):
        # Test based on <line nr="50" ci="1"/> (mi, mb, cb missing -> default to 0)
        # ci=1, mi=0 -> line fullcovered
        # cb=0, mb=0 -> no branch info
        # Test based on <line nr="51" mi="1"/> (ci, mb, cb missing -> default to 0)
        # ci=0, mi=1 -> line nocovered
        # cb=0, mb=0 -> no branch info
        # Test based on <line nr="52" mb="1"/> (ci, mi, cb missing -> default to 0)
        # ci=0, mi=0 -> no line info
        # cb=0, mb=1 -> branch nocovered
        # Test based on <line nr="53" cb="1"/> (ci, mi, mb missing -> default to 0)
        # ci=0, mi=0 -> no line info
        # cb=1, mb=0 -> branch fullcovered
        # Test based on <line nr="54" /> (all missing -> default to 0)
        # ci=0, mi=0 -> no line info
        # cb=0, mb=0 -> no branch info
        f = StringIO()
        with redirect_stderr(f): # Capture potential warnings if attributes are treated as "invalid" vs "defaulted"
            reporter = JaCoCoReport(self.SAMPLE_VALID_XML_PATH, covered_types=['nocovered', 'partiallycovered', 'fullcovered'])
            data = json.loads(reporter.jacoco_to_json())
        
        stderr_output = f.getvalue()
        # We expect no warnings for these missing attributes as they should default to '0'
        self.assertNotIn("Warning: Invalid number format for attributes in line 50", stderr_output)
        self.assertNotIn("Warning: Invalid number format for attributes in line 51", stderr_output)
        self.assertNotIn("Warning: Invalid number format for attributes in line 52", stderr_output)
        self.assertNotIn("Warning: Invalid number format for attributes in line 53", stderr_output)
        self.assertNotIn("Warning: Invalid number format for attributes in line 54", stderr_output)


        missing_attr_data = next((item for item in data if item["sourcefile"] == "MissingAttributes.java"), None)
        self.assertIsNotNone(missing_attr_data, "MissingAttributes.java should be in the report")

        # Line 50: ci="1" (mi=0) -> line fullcovered. mb=0, cb=0 -> no branch data
        self.assertIn(50, missing_attr_data["lines"]["fullcovered"])
        self.assertNotIn(50, missing_attr_data["branch"].get("fullcovered", []))
        self.assertNotIn(50, missing_attr_data["branch"].get("nocovered", []))
        self.assertNotIn(50, missing_attr_data["branch"].get("partiallycovered", []))

        # Line 51: mi="1" (ci=0) -> line nocovered. mb=0, cb=0 -> no branch data
        self.assertIn(51, missing_attr_data["lines"]["nocovered"])
        self.assertNotIn(51, missing_attr_data["branch"].get("fullcovered", []))
        self.assertNotIn(51, missing_attr_data["branch"].get("nocovered", []))
        self.assertNotIn(51, missing_attr_data["branch"].get("partiallycovered", []))

        # Line 52: mb="1" (cb=0) -> branch nocovered. ci=0, mi=0 -> no line data
        self.assertIn(52, missing_attr_data["branch"]["nocovered"])
        self.assertNotIn(52, missing_attr_data["lines"].get("fullcovered", []))
        self.assertNotIn(52, missing_attr_data["lines"].get("nocovered", []))
        self.assertNotIn(52, missing_attr_data["lines"].get("partiallycovered", []))
        
        # Line 53: cb="1" (mb=0) -> branch fullcovered. ci=0, mi=0 -> no line data
        self.assertIn(53, missing_attr_data["branch"]["fullcovered"])
        self.assertNotIn(53, missing_attr_data["lines"].get("fullcovered", []))
        self.assertNotIn(53, missing_attr_data["lines"].get("nocovered", []))
        self.assertNotIn(53, missing_attr_data["lines"].get("partiallycovered", []))

        # Line 54: all missing (ci=0, mi=0, cb=0, mb=0) -> no line data, no branch data
        self.assertNotIn(54, missing_attr_data["lines"].get("fullcovered", []))
        self.assertNotIn(54, missing_attr_data["lines"].get("nocovered", []))
        self.assertNotIn(54, missing_attr_data["lines"].get("partiallycovered", []))
        self.assertNotIn(54, missing_attr_data["branch"].get("fullcovered", []))
        self.assertNotIn(54, missing_attr_data["branch"].get("nocovered", []))
        self.assertNotIn(54, missing_attr_data["branch"].get("partiallycovered", []))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
