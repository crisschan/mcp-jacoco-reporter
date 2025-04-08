import xml.etree.ElementTree as ET
import json

class JaCoCoReport:
    def __init__(self, jacoco_report_path:str,covered_types:list = ['nocovered', 'partiallycovered', 'fullcovered']):
        self.tree = ET.parse(jacoco_report_path+"/jacoco.xml")
        self.root = self.tree.getroot()
        self.covered_types = covered_types
    def jacoco_to_json(self):
        data = self.__parse_jacoco_xml()
        return json.dumps(data, indent=4)
    def __parse_jacoco_xml(self):
        result = []
        for package in self.root.findall('package'):
            package_name = package.get('name')
            for sourcefile in package.findall('sourcefile'):
                sourcefile_name = sourcefile.get('name')
                lines={}
                branch={}
                for covered_type in self.covered_types:
                    lines[covered_type] =  []
                    branch[covered_type] =  []

                for line in sourcefile.findall('line'):
                    ci = int(line.get('ci', 0))
                    mi = int(line.get('mi', 0))
                    mb = int(line.get('mb', 0))
                    cb = int(line.get('cb', 0))
                    line_number = int(line.get('nr'))

                    # Line coverage classification
                    if ci == 0 and mi > 0 and "nocovered" in self.covered_types:
                        lines["nocovered"].append(line_number)
                    elif ci > 0 and mi == 0 and "fullcovered" in self.covered_types:
                        lines["fullcovered"].append(line_number)
                    elif ci > 0 and mi > 0 and "partiallycovered" in self.covered_types:
                        lines["partiallycovered"].append(line_number)

                    # Branch coverage classification
                    if mb == 0 and cb > 0 and "fullcovered" in self.covered_types:
                        branch["fullcovered"].append(line_number)
                    elif mb > 0 and cb == 0 and  "nocovered" in self.covered_types:
                        branch["nocovered"].append(line_number)
                    elif mb > 0 and cb > 0 and "partiallycovered" in self.covered_types:
                        branch["partiallycovered"].append(line_number)

                result.append({
                    "sourcefile": sourcefile_name,
                    "package": package_name,
                    "lines": lines,
                    "branch": branch
                })

        return result
if __name__ == "__main__":
    jac=JaCoCoReport('/Users/crisschan/workspace/pyspace/mcp-jacoco-reporter',covered_types = ['nocovered', 'partiallycovered'])
    print(jac.jacoco_to_json())
