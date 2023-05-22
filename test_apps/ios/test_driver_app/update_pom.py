# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from pathlib import Path
if __name__ == "__main__":
    pom_path = Path(__file__).parent / "target/upload/pom.xml"
    with pom_path.open("r") as fh:
        lines = fh.readlines()
    def replace_testOutputDirectory(line: str):
        left_keyword = "<testOutputDirectory>"
        right_keyword = "</testOutputDirectory>"
        if line.find(left_keyword) >= 0:
            lindex = line.find(left_keyword) + len(left_keyword)
            rindex = line.find(right_keyword)
            return line[0:lindex]+"./test-classes" + line[rindex:len(line)]
        return line
    lines = [replace_testOutputDirectory(line) for line in lines]
    with pom_path.open("w") as fh:
        fh.writelines(lines)