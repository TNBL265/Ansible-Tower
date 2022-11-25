import os
import json
import sys


class AuditReportFilter:
    def __init__(self, os_report, raw_report, lookup_data_filename):
        self.os_report = os_report
        self.raw_report = raw_report

        # set enum for os type for readability
        self.os_type = self.enum(UBUNTU18=0, UBUNTU20=1, UBUNTU22=2,
                                 AMZLNX2=3, RHEL7=4, RHEL8=5, RHEL9=6)

        self.load_preconditions(lookup_data_filename)

    def enum(self, **named_values):
        """
        Enum-liked python function
        """
        return type("Enum", (), named_values)

    def load_preconditions(self, lookup_data_filename):
        """
        Load certain pre conditions for each os-audit report, includes the CIS-manual audit
        """
        # Load lookup table for determining pass fail for each CIS rule
        with open(f"{lookup_data_filename}", "r+") as lookup_data:
            self.lookup_table = json.load(lookup_data)
        lookup_data.close()

    def write_report(self, new_report_name, report_dir):
        with open(f"{report_dir}/{new_report_name}", "w") as save_file:
            json.dump(self.refined_report, save_file, indent=4)
        save_file.close()

    def extract_data(self):
        """
        By default extract only property, success, title from the raw report, upon request can 
        extract more info if found from the raw report
        """
        cis_manual_list = []
        new_report = {}

        for i in range(0, len(self.raw_report['results'])):
            title = self.raw_report['results'][i]['title']
            if title != 'Benchmark MetaData':
                if not title in list(new_report.keys()):
                    new_report[title] = {"result": {}}
                result = self.raw_report['results'][i]['successful']
                audit_type = self.raw_report['results'][i]['property']

                if "Manual" in self.raw_report['results'][i]['summary-line']:
                    actual_title = title.split("|")[1].strip()
                    actual_id = title.split("|")[0].strip()
                    actual_manual_title = actual_id + " | " + actual_title
                    cis_manual_list.append(actual_manual_title)
                new_report[title]["result"][audit_type] = str(result)

        # Pass fail criteria for each audit based on audit type, if found a fail in each audit type, result is fail
        filtered_report = {}
        for audit in new_report:
            result = new_report[audit]["result"]
            if "False" in list(result.values()):
                filtered_report[audit] = "False"
            else:
                filtered_report[audit] = "True"

        # Grouping of audits to CIS rule(one cis rule can have multiple audit), and list down total pass and fail in each CIS rule
        lockdown_multiaudit_list = {}
        for filtered_result in filtered_report:
            cis_id = filtered_result.split("|")[0].strip()
            title = filtered_result.split("|")[1].strip()
            report_key = cis_id + " | " + title
            if report_key in lockdown_multiaudit_list:
                if filtered_report[filtered_result] == "True":
                    lockdown_multiaudit_list[report_key]["pass"] += 1
                else:
                    lockdown_multiaudit_list[report_key]["fail"] += 1
            else:
                lockdown_multiaudit_list[report_key] = {}
                if filtered_report[filtered_result] == "True":
                    lockdown_multiaudit_list[report_key]["pass"] = 1
                    lockdown_multiaudit_list[report_key]["fail"] = 0
                else:
                    lockdown_multiaudit_list[report_key]["pass"] = 0
                    lockdown_multiaudit_list[report_key]["fail"] = 1

        # Determination of pass fail criteria for each CIS rule based on lookup table
        # Here we use 2 for-loop to check lookup table string is in lockdown multiaudit list
        # Future can consider if can reduce 2 for-loop to a much efficient algorithm
        JH_template_report = {}
        for CIS_rule in lockdown_multiaudit_list:
            if lockdown_multiaudit_list[CIS_rule]["pass"] + lockdown_multiaudit_list[CIS_rule]["fail"] == 1:
                if lockdown_multiaudit_list[CIS_rule]["pass"]:
                    JH_template_report[CIS_rule] = "Pass"
                else:
                    JH_template_report[CIS_rule] = "Fail"
            else:
                for lookup_of in self.lookup_table["onefail"]:
                    if lookup_of in CIS_rule:
                        if lockdown_multiaudit_list[CIS_rule]["fail"] > 0:
                            JH_template_report[CIS_rule] = "Fail"
                        else:
                            JH_template_report[CIS_rule] = "Pass"
                for lookup_af in self.lookup_table["allfail"]:
                    if lookup_af in CIS_rule:
                        if lockdown_multiaudit_list[CIS_rule]["pass"] > 0:
                            JH_template_report[CIS_rule] = "Pass"
                        else:
                            JH_template_report[CIS_rule] = "Fail"

        # Add Manual test as result 
        for manual_test in cis_manual_list:
            JH_template_report[manual_test] = "Manual"

        # Set report 
        self.refined_report = JH_template_report


if __name__ == "__main__":
    #################################
    # Only for temporary usage      #
    #################################
    if len(sys.argv) == 4:
        lookup_data_filename = sys.argv[1]
        audit_os_type = sys.argv[2]
        raw_report_name = sys.argv[3]
    else:
        print("Usage:\npython3 {lookup_data_filename} {audit_os_type} {raw_report_name}")
        exit(1)

    support_os_type = ["ubuntu18", "ubuntu20", "ubuntu22", "amazon_linux2", "rhel7", "rhel8", "rhel9"]
    audit_os = 0
    if not audit_os_type.lower() in support_os_type:
        print(f"Supported os type: {support_os_type}")
        exit(1)
    else:
        for os_type in support_os_type:
            if audit_os_type.lower() == "ubuntu18":
                audit_os = 0
            elif audit_os_type.lower() == "ubuntu20":
                audit_os = 1
            elif audit_os_type.lower() == "ubuntu22":
                audit_os = 2
            elif audit_os_type.lower() == "amazon_linux2":
                audit_os = 3
            elif audit_os_type.lower() == "rhel7":
                audit_os = 4
            elif audit_os_type.lower() == "rhel8":
                audit_os = 5
            elif audit_os_type.lower() == "rhel9":
                audit_os = 6

    read_raw_report = open(f"{raw_report_name}", )
    audit_raw_report = json.load(read_raw_report)
    read_raw_report.close()
    report = AuditReportFilter(audit_os, audit_raw_report, lookup_data_filename)
    report.extract_data()
    print(json.dumps(report.refined_report))
