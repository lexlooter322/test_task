import multiprocessing
import sys
import re
from multiprocessing import Pool, cpu_count
from typing import Dict, List

class Reports:
    def __init__(self, paths_to_logs: List[str], name_report="handlers") -> None:
        self.paths_to_logs: List[str] = paths_to_logs
        self.name_report: str = name_report
        self.total_number_of_requests:Dict[str,int] = {}
        self.report: Dict[str, Dict[str, int]]  = None



    def manager(self) -> Dict[str, Dict[str, int]] :
        report: str = "Такого отчета нет"

        if self.name_report == "handlers":
            report: Dict[str, Dict[str, int]] = self.multiproc_report_handler()

        return report


    def view_report(self) -> None:
        title:str = f"{self.name_report.upper():<20}"

        for key in self.total_number_of_requests.keys():
            title += f"{key:<10}"

        print(title)

        for key in sorted(self.report):
            row_report:str = f"{key:<20}"

            for val in self.report[key].values():
                row_report += f"{val:<10}"

            print(row_report)

        total_requests:str = " " * 20
        for key in self.total_number_of_requests:
            total_requests += f"{self.total_number_of_requests[key]:<10}"
        print(total_requests)




    def parse_log_file(self, path_to_log:str) -> Dict[str, Dict[str, int]]:
        data_dict: dict = {}

        with open(path_to_log) as log:

            handler:str = ""
            for row in log:
                if "django.request" in row:
                    handler: str = re.search(r"/.+/", row).group(0)
                    data_dict.setdefault(handler, {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0})

                list_of_row: List[str] = row.split()
                data_dict[handler][list_of_row[2]] = data_dict[handler][list_of_row[2]] + 1

        return data_dict


    def multiproc_report_handler(self) -> Dict[str, Dict[str, int]] :
        pool: multiprocessing.Pool = Pool(processes=cpu_count())

        result: List[Dict[str:Dict[str:int]]] = pool.map(self.parse_log_file, self.paths_to_logs)

        pool.close()
        pool.join()

        final_report: Dict[str: Dict[str:int]] = {}

        for report in result:
            for k, v in report.items():
                if k in final_report:
                    for level, val in v.items():
                        final_report[k][level] = final_report[k][level] + val
                else:
                    final_report[k] = v
                for level, count in v.items():
                    self.total_number_of_requests[level] = self.total_number_of_requests.get(level, 0) + count

        return final_report


if __name__ == '__main__':
    args_cmd = sys.argv
    args = []
    if len(args_cmd) > 1:
        if args_cmd[-2] == "--report":
            args.append(args_cmd[1: -2])
            args.append(args_cmd[-1])
        else:
            args.append(args_cmd[1:])

    report = Reports(*args)

    report.view_report()



