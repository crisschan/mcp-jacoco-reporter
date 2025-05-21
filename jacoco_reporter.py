import xml.etree.ElementTree as ET
import json
import os
import sys # Import sys for stderr

class JaCoCoReport:
    def __init__(self, jacoco_xmlreport_path:str,covered_types:list = ['nocovered', 'partiallycovered', 'fullcovered']):
        if not os.path.isfile(jacoco_xmlreport_path):
            raise FileNotFoundError(f"The file '{jacoco_xmlreport_path}' does not exist or is not a valid file.")
        
        try:
            self.tree = ET.parse(jacoco_xmlreport_path)
            self.root = self.tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse the XML file: {e}")
        
        self.covered_types = covered_types

    def _classify_coverage_item(self, covered_count, missed_count):
        """
        Classifies a coverage item based on covered and missed counts.

        Args:
            covered_count (int): The count of covered items (e.g., ci or cb).
            missed_count (int): The count of missed items (e.g., mi or mb).

        Returns:
            tuple: (status_type, should_add_to_list)
                   status_type (str): 'nocovered', 'partiallycovered', or 'fullcovered'.
                   should_add_to_list (bool): True if the status_type is in self.covered_types.
        """
        status_type = None
        if covered_count == 0 and missed_count > 0:
            status_type = 'nocovered'
        elif covered_count > 0 and missed_count == 0:
            status_type = 'fullcovered'
        elif covered_count > 0 and missed_count > 0:
            status_type = 'partiallycovered'
        
        should_add_to_list = status_type is not None and status_type in self.covered_types
        return status_type, should_add_to_list

    def jacoco_to_json(self):
        data = self.__parse_jacoco_xml()
        return json.dumps(data, indent=4)

    def __parse_jacoco_xml(self):
        result = []
        for package in self.root.findall('package'):
            package_name = package.get('name') if package.get('name') is not None else "UnknownPackage"
            for sourcefile in package.findall('sourcefile'):
                sourcefile_name = sourcefile.get('name') if sourcefile.get('name') is not None else "UnknownSourcefile"
                
                lines={}
                branch={}
                for covered_type in self.covered_types: # Initialize keys based on requested covered_types
                    lines[covered_type] =  []
                    branch[covered_type] =  []

                for line in sourcefile.findall('line'):
                    try:
                        # Attempt to get and convert all necessary attributes first
                        line_number_str = line.get('nr')
                        if line_number_str is None:
                            print(f"Warning: Missing 'nr' attribute for a line in {sourcefile_name}, package {package_name}. Skipping line.", file=sys.stderr)
                            continue
                        line_number = int(line_number_str)

                        ci_str = line.get('ci', '0')
                        mi_str = line.get('mi', '0')
                        mb_str = line.get('mb', '0')
                        cb_str = line.get('cb', '0')

                        ci = int(ci_str)
                        mi = int(mi_str)
                        mb = int(mb_str)
                        cb = int(cb_str)

                    except ValueError as e:
                        print(f"Warning: Invalid number format for attributes in line {line.get('nr', 'N/A')} for {sourcefile_name}, package {package_name}. Error: {e}. Skipping line.", file=sys.stderr)
                        continue

                    # Line coverage classification
                    line_status_type, should_add_line = self._classify_coverage_item(ci, mi)
                    if line_status_type and should_add_line: # Ensure status_type is not None
                        if line_status_type not in lines: # Ensure list exists if not pre-initialized for all possible types
                             lines[line_status_type] = []
                        lines[line_status_type].append(line_number)

                    # Branch coverage classification
                    branch_status_type, should_add_branch = self._classify_coverage_item(cb, mb) # Note: cb is covered, mb is missed for branches
                    if branch_status_type and should_add_branch: # Ensure status_type is not None
                        if branch_status_type not in branch: # Ensure list exists
                            branch[branch_status_type] = []
                        branch[branch_status_type].append(line_number)
                
                # Filter out empty lists for lines and branch before adding to result
                filtered_lines = {k: v for k, v in lines.items() if v}
                filtered_branch = {k: v for k, v in branch.items() if v}

                if filtered_lines or filtered_branch: # Only add if there's some coverage data
                    result.append({
                        "sourcefile": sourcefile_name,
                        "package": package_name,
                        "lines": filtered_lines,
                        "branch": filtered_branch
                    })
        return result

if __name__ == "__main__":
    # Create a dummy jacoco.xml for testing
    dummy_xml_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.1//EN" "report.dtd">
<report name="dummmy_report">
    <package name="com/example/package1">
        <sourcefile name="MyClass.java">
            <line nr="10" mi="0" ci="5" mb="0" cb="2"/>
            <line nr="11" mi="1" ci="0" mb="1" cb="0"/>
            <line nr="12" mi="1" ci="1" mb="1" cb="1"/>
            <line nr="13" mi="invalid" ci="5" mb="0" cb="2"/> <!-- Invalid data -->
            <line nr="14" ci="5"/> <!-- Missing mi -->
        </sourcefile>
        <sourcefile name="AnotherClass.java">
            <line nr="20" mi="0" ci="3" mb="0" cb="0"/>
        </sourcefile>
    </package>
    <package name="com/example/package2">
        <sourcefile name="YetAnotherClass.java">
             <line nr="30" mi="0" ci="10" mb="0" cb="4"/>
        </sourcefile>
    </package>
    <package> <!-- Missing package name -->
        <sourcefile name="NoPackageSource.java">
            <line nr="40" mi="0" ci="1" mb="0" cb="1"/>
        </sourcefile>
    </package>
     <package name="com/example/empty">
        <sourcefile name="Empty.java">
            <!-- No line elements -->
        </sourcefile>
    </package>
</report>
    """
    dummy_xml_path = "dummy_jacoco.xml"
    with open(dummy_xml_path, "w") as f:
        f.write(dummy_xml_content)

    print("Testing with all coverage types:")
    jac_all = JaCoCoReport(dummy_xml_path)
    print(jac_all.jacoco_to_json())
    print("\nTesting with 'nocovered' and 'partiallycovered':")
    jac_filtered = JaCoCoReport(dummy_xml_path, covered_types=['nocovered', 'partiallycovered'])
    print(jac_filtered.jacoco_to_json())
    
    # Test with a non-existent file
    try:
        JaCoCoReport("non_existent_file.xml")
    except FileNotFoundError as e:
        print(f"\nSuccessfully caught error: {e}")

    # Test with an invalid XML file
    invalid_xml_path = "invalid_jacoco.xml"
    with open(invalid_xml_path, "w") as f:
        f.write("<report><unclosed_tag></report>")
    try:
        JaCoCoReport(invalid_xml_path)
    except ValueError as e:
        print(f"\nSuccessfully caught error: {e}")

    # Clean up dummy files
    os.remove(dummy_xml_path)
    os.remove(invalid_xml_path)
