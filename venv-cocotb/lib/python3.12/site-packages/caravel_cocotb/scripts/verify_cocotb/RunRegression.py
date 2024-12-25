#!/usr/bin/python3

from datetime import datetime
import os
import sys
from subprocess import PIPE, run

try:
    sys.path.append(os.getcwd())
    from user_run_test import UserRunTest as RunTest
except ImportError:
    from caravel_cocotb.scripts.verify_cocotb.RunTest import RunTest
from caravel_cocotb.scripts.verify_cocotb.Test import Test
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import socket
import yaml
from caravel_cocotb.scripts.merge_coverage import merge_fun_cov
from caravel_cocotb.scripts.test_defaults.test_defaults import TestDefaults
from rich.live import Live
from rich.table import Table
from rich.console import Console
import glob
import subprocess

class RunRegression:
    def __init__(self, args, paths, logger) -> None:
        self.args = args
        self.paths = paths
        self.logger = logger
        self.is_first_test_run = False
        self.total_start_time = datetime.now()
        self.write_command_log()
        self.write_git_log()
        self.get_tests()
        self.set_common_macros()
        self.unzip_sdf_files()
        self.run_defaults_script()
        self.run_regression()
        self.send_mail()

    def set_common_macros(self):
        if self.args.macros is None:
            self.args.macros = list()
        simulation_macros = ["USE_POWER_PINS", "UNIT_DELAY=#1", "COCOTB_SIM"]
        paths_macros = [
            f'RUN_PATH=\\"{self.paths.RUN_PATH}\\"',
            f'TAG=\\"{self.args.tag}\\"',
            f'CARAVEL_ROOT=\\"{self.paths.CARAVEL_ROOT}\\"',
            f'MCW_ROOT=\\"{self.paths.MCW_ROOT}\\"',
            f'USER_PROJECT_ROOT=\\"{self.paths.USER_PROJECT_ROOT}\\"',
        ]

        paths_macros.append(f'SIM_PATH=\\"{self.paths.SIM_PATH}/\\"')
        if self.args.pdk != "gf180":
            simulation_macros.append("FUNCTIONAL")

        if self.args.caravan:
            simulation_macros.append("CARAVAN")
        # don't dumb waves if tests are more than 10
        if not self.args.no_wave and len(self.tests) < 10:
            simulation_macros.append("WAVE_GEN")

        if self.args.sdf_setup:
            simulation_macros.append("MAX_SDF")

        if self.args.iverilog:
            simulation_macros.append("IVERILOG")
        elif self.args.vcs:
            simulation_macros.append("VCS")

        simulation_macros.append(self.args.pdk)

        simulation_macros.extend([f"CPU_TYPE_{self.args.cpu_type}"])
        if self.args.cpu_type == "ARM":
            simulation_macros.append("AHB")

        self.args.macros += simulation_macros + paths_macros

    def get_tests(self):
        self.tests = list()
        self.passed_tests = 0
        self.failed_tests = 0
        # test
        if self.args.test is not None:
            if isinstance(self.args.test, list):
                for test in self.args.test:
                    if isinstance(self.args.sim, list):
                        for sim_type in self.args.sim:
                            if sim_type == "GL_SDF":
                                for corner in self.args.corner:
                                    self.add_new_test(
                                        test_name=test, sim_type=sim_type, corner=corner
                                    )
                            else:
                                self.add_new_test(
                                    test_name=test,
                                    sim_type=sim_type,
                                    corner=self.args.corner[0],
                                )
                    else:
                        if self.args.sim == "GL_SDF":
                            for corner in self.args.corner:
                                self.add_new_test(
                                    test_name=test, sim_type=sim_type, corner=corner
                                )
                        else:
                            self.add_new_test(
                                test_name=test,
                                sim_type=sim_type,
                                corner=self.args.corner[0],
                            )
            else:
                if isinstance(self.args.sim, list):
                    for sim_type in self.args.sim:
                        self.add_new_test(
                            test_name=self.args.test,
                            sim_type=sim_type,
                            corner=self.args.corner[0],
                        )
                else:
                    self.add_new_test(
                        test_name=self.args.test,
                        sim_type=self.args.sim,
                        corner=self.args.corner[0],
                    )
        if self.args.testlist is not None:
            for testlist in self.args.testlist:
                self.get_testlist(testlist)
            if len(self.tests) == 0:
                raise RuntimeError(
                    "test list {self.args.testlist} doesn't have any valid tests please review the format of the yaml file"
                )
        if len(self.tests) == 0:
            raise RuntimeError("There is no test provided to run")
        self.update_run_log()

    def add_new_test(self, test_name, sim_type, corner, macros=None):
        self.tests.append(Test(test_name, sim_type, corner, self.args, self.paths, self.logger, macros))

    def get_testlist(self, testlist_f):
        directory = os.path.dirname(testlist_f)
        testlist_f = open(testlist_f, "r")
        testlist = yaml.safe_load(testlist_f)
        if "includes" in testlist:
            for include in testlist["includes"]:
                if directory == "":
                    self.get_testlist(f"{include}")
                else:
                    self.get_testlist(f"{directory}/{include}")
        if "Tests" in testlist:
            for test in testlist["Tests"]:
                for corner in self.args.corner:
                    data = {
                        "test_name": test["name"],
                        "sim_type": "RTL",
                        "corner": corner,
                    }
                    if "sim" in test:
                        data["sim_type"] = test["sim"]
                    if "corner" in test:
                        data["corner"] = test["corner"]
                    if "macros" in test:
                        data["macros"] = test["macros"]
                    self.add_new_test(**data)
                    # add sim to args to detect that this testlist has GL or sdf sims
                    if data["sim_type"] not in self.args.sim:
                        self.args.sim.append(data["sim_type"])

    def run_defaults_script(self):
        if not ("GL_SDF" in self.args.sim or "GL" in self.args.sim):
            return
        if self.args.no_gen_defaults:
            return
        current_dir = os.getcwd()
        if self.args.gen_defaults_dir is None:
            root_script = f"{self.paths.CARAVEL_ROOT}/"
        else:
            root_script = self.args.gen_defaults_dir
        os.chdir(root_script)
        self.logger.info("Running gen_gpio_defaults script")
        os.system(
            f"python3 scripts/gen_gpio_defaults.py {self.paths.USER_PROJECT_ROOT}"
        )
        os.chdir(current_dir)

    def run_regression(self):
        # threads = list()
        if self.args.verbosity == "quiet" and not self.args.CI:  # run live screen
            with Live(self.live_table(), auto_refresh=False) as self.live_screen:
                self.run_all_tests()
        else:
            self.run_all_tests()
            # Print the table in the top-left corner
            Console().print(self.live_table(), justify="left")

        # for index, thread in enumerate(threads):
        #     thread.join()
        # # Coverage
        if "RTL" in self.args.sim and self.args.vcs:
            try:
                self.logger.info("\nStart merging coverage\n")
                self.cov_dir = f"{self.paths.SIM_PATH}/{self.args.tag}/coverage"
                # merge line coverage
                old_path = os.getcwd()
                os.chdir(f"{self.paths.SIM_PATH}/{self.args.tag}")
                os.system(
                    f"urg -dir */*.vdb -format both -show tests -report {self.cov_dir}/line_cov"
                )
                os.chdir(old_path)
                # merge functional coverage
                merge_fun_cov(
                    f"{self.paths.SIM_PATH}/{self.args.tag}",
                    reports_path=f"{self.cov_dir}/functional_cov",
                )
            except Exception as e:
                self.logger.error(e)

    def run_all_tests(self):
        if self.args.compile_only:  # run only the first test to compile
            self.test_run_function(self.tests[0])
        else:
            for test in self.tests:
                if self.args.iverilog:  # threading
                    # x = threading.Thread(target=self.test_run_function,args=(test,sim_type,corner))
                    # threads.append(x)
                    # x.start()
                    # time.sleep(10)
                    self.test_run_function(test)
                else:
                    self.test_run_function(test)
                # run defaults
                if self.args.run_defaults:
                    self.args.compile = True
                    TestDefaults(self.args, self.paths, self.test_run_function, self.tests, self.logger)

    def test_run_function(self, test):
        test.start_of_test()
        if not self.args.compile_only:
            self.update_run_log()
            self.update_live_table()
        RunTest(self.args, self.paths, test, self.logger).run_test()
        if not self.args.compile_only:
            self.update_run_log()
            self.update_live_table()
        if self.args.progress:
            self.logger.info(f"Total: {f'passed ({test.passed_count})':12} {f'failed ({test.failed_count})':12} {f'unknown ({test.unknown_count})':13} elapsed time ({('%.10s' % (datetime.now() - self.total_start_time))})")

    def update_run_log(self):
        file_name = f"{self.paths.SIM_PATH}/{self.args.tag}/runs.log"
        f = open(file_name, "w")
        name_size = self.tests[0].max_name_size
        f.write(
            f"{'Test':<{name_size}} {'status':<10} {'start':<15} {'end':<15} {'duration':<13} {'p/f':<8} {'seed':<10} \n"
        )
        for test in self.tests:
            f.write(
                f"{test.full_name:<{name_size}} {test.status:<10} {test.start_time:<15} {test.endtime:<15} {test.duration:<13} {test.passed:<8} {test.seed:<10}\n"
            )
        f.write(
            f"\n\nTotal: {f'passed ({test.passed_count})':12} {f'failed ({test.failed_count})':12} {f'unknown ({test.unknown_count})':13} elapsed time ({('%.10s' % (datetime.now() - self.total_start_time))})"
        )
        f.close()

    def live_table(self):
        table = Table()
        table.add_column("Total")
        table.add_column("Passed")
        table.add_column("Failed")
        table.add_column("Unknown")
        table.add_column("duration")
        table.add_column(" ")
        table.add_column(" ")
        table.add_row(
            str(len(self.tests)),
            str(self.tests[0].passed_count),
            str(self.tests[0].failed_count),
            str(self.tests[0].unknown_count),
            f"{('%.10s' % (datetime.now() - self.total_start_time))}",
            "",
            "",
            style="bold",
        )
        table.add_row("", "", "", "", "", "", "", style="on white bold")
        table.add_row(
            "Test",
            "status",
            "start",
            "end",
            "duration",
            "p/f",
            "seed",
            style="white bold",
        )
        for row in self.tests:
            style = (
                "green"
                if row.passed == "passed"
                else "red bold" if row.passed == "failed" else "cyan italic"
            )
            table.add_row(
                row.full_name,
                row.status,
                row.start_time,
                row.endtime,
                row.duration,
                row.passed,
                row.seed,
                style=style,
            )
        return table

    def update_live_table(self):
        if self.args.verbosity != "quiet" or self.args.CI:
            return
        self.live_screen.update(self.live_table(), refresh=True)

    def write_command_log(self):
        file_name = f"{self.paths.SIM_PATH}/{self.args.tag}/command.log"
        f = open(file_name, "w")
        f.write("command used to run this sim:\n% ")
        f.write(f"{' '.join(sys.argv)}")
        f.close()

    def write_git_log(self):
        file_name = f"{self.paths.SIM_PATH}/{self.args.tag}/repos_info.log"
        f = open(file_name, "w")
        f.write(f"{'#'*4} Caravel repo info {'#'*4}\n")
        url = "https://github.com/" + f"{run(f'cd {self.paths.CARAVEL_ROOT};git ls-remote --get-url', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout}".replace(
            "git@github.com:", ""
        ).replace(
            ".git", ""
        )
        repo = f"Repo: {run(f'cd {self.paths.CARAVEL_ROOT};basename -s .git `git config --get remote.origin.url`', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout} ({url})".replace(
            "\n", " "
        )
        f.write(f"{repo}\n")
        f.write(
            f"Branch name: {run(f'cd {self.paths.CARAVEL_ROOT};git symbolic-ref --short HEAD', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout}"
        )
        f.write(
            run(
                f"cd {self.paths.CARAVEL_ROOT};git show --quiet HEAD",
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True,
                shell=True,
            ).stdout
        )

        f.write(f"\n\n{'#'*4} Caravel Managment repo info {'#'*4}\n")
        url = "https://github.com/" + f"{run(f'cd {self.paths.MCW_ROOT};git ls-remote --get-url', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout}".replace(
            "git@github.com:", ""
        ).replace(
            ".git", ""
        )
        repo = f"Repo: {run(f'cd {self.paths.MCW_ROOT};basename -s .git `git config --get remote.origin.url`', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout} ({url})".replace(
            "\n", " "
        )
        f.write(f"{repo}\n")
        f.write(
            f"Branch name: {run(f'cd {self.paths.MCW_ROOT};git symbolic-ref --short HEAD', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout}"
        )
        f.write(
            run(
                f"cd {self.paths.MCW_ROOT};git show --quiet HEAD",
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True,
                shell=True,
            ).stdout
        )

        f.write(f"\n\n{'#'*4} User repo info {'#'*4}\n")
        url = "https://github.com/" + f"{run(f'cd {self.paths.USER_PROJECT_ROOT};git ls-remote --get-url', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout}".replace(
            "git@github.com:", ""
        ).replace(
            ".git", ""
        )
        repo = f"Repo: {run(f'cd {self.paths.USER_PROJECT_ROOT};basename -s .git `git config --get remote.origin.url`', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout} ({url})".replace(
            "\n", " "
        )
        f.write(f"{repo}\n")
        f.write(
            f"Branch name: {run(f'cd {self.paths.USER_PROJECT_ROOT};git symbolic-ref --short HEAD', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout}"
        )
        f.write(
            run(
                f"cd {self.paths.USER_PROJECT_ROOT};git show --quiet HEAD",
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True,
                shell=True,
            ).stdout
        )

        f.write(f"\n\n{'#'*4} caravel-dynamic-sims repo info {'#'*4}\n")
        url = "https://github.com/" + f"{run(f'cd {self.paths.RUN_PATH};git ls-remote --get-url', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout}".replace(
            "git@github.com:", ""
        ).replace(
            ".git", ""
        )
        repo = f"Repo: {run(f'cd {self.paths.RUN_PATH};basename -s .git `git config --get remote.origin.url`', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout} ({url})".replace(
            "\n", " "
        )
        f.write(f"{repo}\n")
        f.write(
            f"Branch name: {run(f'cd {self.paths.RUN_PATH};git symbolic-ref --short HEAD', stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).stdout}"
        )
        f.write(
            run(
                f"cd {self.paths.RUN_PATH};git show --quiet HEAD",
                stdout=PIPE,
                stderr=PIPE,
                universal_newlines=True,
                shell=True,
            ).stdout
        )
        f.close()

    def send_mail(self):
        if self.args.emailto is None or self.args.emailto == []:
            return
        # get commits
        showlog = f"{self.paths.SIM_PATH}/{self.args.tag}/repos_info.log"
        commits = ""
        lines = open(showlog, "r").readlines()
        for line in lines:
            if "Repo" in line:
                repo = line.replace(")", "").split("(")
                repo_name = repo[0]
                repo_url = repo[1].replace(" ", "").replace("\n", "")
            elif "commit" in line:
                commit = line.split()[-1]
                commits += f"<th> {repo_name} commit</th> <th><a href='{repo_url}/commit/{commit}'>{commit}<a></th> <tr>  "
        tag = f"{self.paths.SIM_PATH}/{self.args.tag}"
        mail_sub = (
            "<html><head><style>table {border-collapse: collapse;width: 50%;} th, td {text-align: left;padding: 8px;} tr:nth-child(even) {background-color: #D6EEEE;}"
            f"</style></head><body><h2>Run info:</h2> <table border=2 bgcolor=#D6EEEE> "
            f"<th>location</th> <th><strong>{socket.gethostname()}</strong>:{tag}</th> <tr>  "
            f"{commits}</table> "
        )
        mail_sub += self.set_html_test_table()
        mail_sub += "<p>best regards, </p></body></html>"
        # print(mail_sub)
        msg = MIMEMultipart("alternative", None, [MIMEText(mail_sub, "html")])
        all_pass = self.tests[0].failed_count == 0 and self.tests[0].unknown_count == 0
        if all_pass:
            msg["Subject"] = f"Pass: {self.args.tag} run results"
        else:
            msg["Subject"] = f"Fail: {self.args.tag} run results"
        msg["From"] = "verification@efabless.com"
        msg["To"] = ", ".join(self.args.emailto)
        docker = False
        if docker:
            mail_command = f'echo "{mail_sub}" | mail -a "Content-type: text/html;" -s "{msg["Subject"]}" {self.args.emailto[0]}'
            docker_command = f"docker run -it -u $(id -u $USER):$(id -g $USER) efabless/dv:mail sh -c '{mail_command}'"
            print(docker_command)
            os.system(docker_command)
        else:
            # Send the message via our own SMTP server.
            s = smtplib.SMTP("localhost")
            s.send_message(msg)
            s.quit()

    def set_html_test_table(self):
        html_test_table = "<h2>Tests Table:</h2><table border=2 bgcolor=#D6EEEE>"
        html_test_table += (
            "<th>Test</th> <th>duration</th> <th>status</th> <th>seed</th> <tr> "
        )
        for test in self.tests:
            if test.passed == "passed":
                html_test_table += f"<th>{test.full_name}</th><th>{test.duration}</th> <th style='background-color:#16EC0C'> {test.passed} </th><th>{test.seed}</th><tr>"
            else:
                html_test_table += f"<th>{test.full_name}</th><th>{test.duration}</th> <th style='background-color:#E50E0E'> {test.passed} </th><th>{test.seed}</th><tr>"
        html_test_table += "</table>"
        html_test_table += (
            f"<h2>Total status Table:</h2><table border=2 bgcolor=#D6EEEE><th>Passed</th> <th>failed</th> <th>unknown</th> <th>duration</th> <tr>"
            f"<th style='background-color:#16EC0C' >{test.passed_count}</th> <th style='background-color:#E50E0E' >{test.failed_count} </th> "
            f"<th style='background-color:#14E5F2'>{test.unknown_count}</th> <th>{('%.10s' % (datetime.now() - self.total_start_time))}</th> <tr></table>"
        )
        return html_test_table

    def unzip_sdf_files(self):
        # proceed only if sim type is GL_SDF
        if isinstance(self.args.sim, list):
            if "GL_SDF" not in self.args.sim:
                return
        elif self.args.sim != "GL_SDF":
            return
        # keep caravel sdf dir
        sdf_dir = f"{self.paths.CARAVEL_ROOT}/signoff/{'caravan' if self.args.caravan else 'caravel'}/primetime/sdf"
        if self.args.sdfs_dir is None:
            pass
        else:
            sdf_dir = self.args.sdfs_dir
        if isinstance(sdf_dir, list):
            gz_files = []
            for dir in sdf_dir:
                gz_files += glob.glob(f"{dir}/**/*.gz".replace('"', ''), recursive=True)
        else:
            gz_files = glob.glob(f"{sdf_dir}/**/*.gz".replace('"', ''), recursive=True)
        print("unzipping files {}".format(gz_files))
        for gz_file in gz_files:
            subprocess.run(f"gzip {gz_file} -d".split())
        self.args.macros.append(f'SDF_PATH=\\"{sdf_dir}\\"')
