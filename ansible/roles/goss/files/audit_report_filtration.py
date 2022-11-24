import os
import json
import sys


class AuditReportFilter:
    def __init__(self, os_report, raw_report):
        self.os_report = os_report
        self.raw_report = raw_report

        # set enum for os type for readability
        self.os_type = self.enum(UBUNTU18=0, UBUNTU20=1, UBUNTU22=2,
                                 AMZLNX2=3, RHEL7=4, RHEL8=5, RHEL9=6)

        self.load_preconditions()

    def enum(self, **named_values):
        """
        Enum-liked python function
        """
        return type("Enum", (), named_values)

    def load_preconditions(self):
        """
        Load certain pre conditions for each os-audit report, includes the CIS-manual audit
        """
        with open(f"{os.path.abspath(os.curdir)}/preconditions/audit_preconditions.json", "r+") as audit_data:
            audit_conditions = json.load(audit_data)
        audit_data.close()

        if self.os_report == self.os_type.UBUNTU18:
            self.preconditions = audit_conditions["ubuntu18"]
        elif self.os_report == self.os_type.UBUNTU20:
            self.preconditions = audit_conditions["ubuntu20"]
        elif self.os_report == self.os_type.UBUNTU22:
            self.preconditions = audit_conditions["ubuntu22"]
        elif self.os_report == self.os_type.AMZLNX2:
            self.preconditions = audit_conditions["amazon_linux2"]
        elif self.os_report == self.os_type.RHEL7:
            self.preconditions = audit_conditions["rhel7"]
        elif self.os_report == self.os_type.RHEL8:
            self.preconditions = audit_conditions["rhel8"]
        elif self.os_report == self.os_type.RHEL9:
            self.preconditions = audit_conditions["rhel9"]

        # Load lookup table for determining pass fail for each CIS rule
        with open(f"{os.path.abspath(os.curdir)}/lookup_table/CIS_rule_lookup_table.json", "r+") as lookup_data:
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
        # lockdown_manual_list = self.preconditions["lockdown_manual_list"]
        # cis_manual_list = self.preconditions["cis_manual_list"]
        # pass_condition_dict = self.preconditions["special_pass_conditions"]
        cis_manual_list = []
        new_report = {}

        for i in range(0, len(self.raw_report['results'])):
            title = self.raw_report['results'][i]['title']
            if title != 'Benchmark MetaData':
                if not title in list(new_report.keys()):
                    new_report[title] = {"result": {}}
                cis_id = self.raw_report['results'][i]['meta']['CIS_ID']
                result = self.raw_report['results'][i]['successful']
                audit_type = self.raw_report['results'][i]['property']

                if "Manual" in self.raw_report['results'][i]['summary-line']:
                    actual_title = title.split("|")[1].strip()
                    actual_id = title.split("|")[0].strip()
                    actual_manual_title = actual_id + " | " + actual_title
                    cis_manual_list.append(actual_manual_title)

                #                if isinstance(cis_id, str):
                #                    new_report[title]["cid_id"] = cis_id
                #                    if cis_id in lockdown_manual_list:
                #                        # If it is a manual test no need to report pass or fail, just 'manual' will do
                #                        if "pass" in new_report[title]["result"] and "fail" in new_report[title]["result"]:
                #                            new_report[title]["result"].pop("pass")
                #                            new_report[title]["result"].pop("fail")
                #                        new_report[title]["result"] = "manual"
                #                elif isinstance(cis_id, list):
                #                    if len(cis_id) == 1:
                #                        new_report[title]["cid_id"] = str(cis_id[0])
                #                        # if cis_id length only 1 we can proceed to pop the result
                #                        if str(cis_id[0]) in lockdown_manual_list:
                #                            if "pass" in new_report[title]["result"] and "fail" in new_report[title]["result"]:
                #                                new_report[title]["result"].pop("pass")
                #                                new_report[title]["result"].pop("fail")
                #                            new_report[title]["result"] = "manual"
                #                    else:
                #                        # cis_id list that dont have manual test
                #                        new_report[title]["cid_id"] = []
                #                        for id in cis_id:
                #                            new_report[title]["cid_id"].append(str(id))
                #
                #                else:
                #                    # for cis_id that is integer
                #                    new_report[title]["cid_id"] = str(cis_id)
                #                    if str(cis_id) in lockdown_manual_list:
                #                        if "pass" in new_report[title]["result"] and "fail" in new_report[title]["result"]:
                #                            new_report[title]["result"].pop("pass")
                #                            new_report[title]["result"].pop("fail")
                #                        new_report[title]["result"] = "manual"

                #                # if the result is str it is a manual audit, can be ignored
                #                if not isinstance(new_report[title]['result'], str):
                #                    if not result:
                #                        new_report[title]["result"]["fail"] = new_report[title]["result"]["fail"] + 1
                #                    elif result:
                #                        new_report[title]["result"]["pass"] = new_report[title]["result"]["pass"] + 1
                # add audit_type to result directly
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
    # Only for temporay usage       #
    #################################
    if len(sys.argv) == 4:
        audit_os_type = sys.argv[1]
        # refined_report_name = sys.argv[2]
        raw_report_name = sys.argv[2]
    else:
        print("Usage:\npython3 audit_report_filtration.py {audit_os_type} {refined_report_name} {raw_report_name}")
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

    # raw_report_list = os.listdir(f"{os.path.abspath(os.curdir)}/raw_report")
    # if raw_report_name not in raw_report_list:
    #     print(
    #         f"[Error] Unable to find the raw_report: {raw_report_name}, please make sure it is in json format and located in raw_report folder")
    #     exit(1)
    #################################
    #    for file in os.listdir(f"{os.path.abspath(os.curdir)}/raw_report"):
    #        if not (files.endswith('.json')) or not (files == raw_report_name):
    #            print("[Error] Unable to find the raw_report: {raw_report_name}, please make sure it is json format and located in raw_report folder")
    #            exit(1)

    #    read_raw_report = open(f"{os.path.abspath(os.curdir)}/{f_name}",)
    read_raw_report = open(f"{raw_report_name}", )
    audit_raw_report = json.load(read_raw_report)
    read_raw_report.close()
    report = AuditReportFilter(audit_os, audit_raw_report)
    report.extract_data()
    print(report.refined_report)
    # report.write_report(refined_report_name, f"{os.getcwd()}/report_refined")
