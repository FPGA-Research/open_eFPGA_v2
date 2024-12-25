import subprocess
import os


class DockerProcess:
    def __init__(self, image_name, user_project_path=None, sim_path=None) -> None:
        self.image_name = image_name
        self.user_project_path = user_project_path
        self.sim_path = sim_path

    def run(self):
        # pull/update docker image
        self.pull_docker_image()
        # update docker image with pip commands if requirements.txt exists
        if os.path.exists(
            f"{self.user_project_path}/verilog/dv/cocotb/requirements.txt"
        ):
            self.write_docker_file()
            self.build_docker_image()

    def pull_docker_image(self):
        # Check if the image exists locally
        try:
            subprocess.run(
                ["docker", "inspect", self.image_name],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print(f"check update for docker image {self.image_name}.")
            command = ["docker", "pull", "-q", f"{self.image_name}"]
        except subprocess.CalledProcessError:
            print(f"pulling  docker image {self.image_name}.")
            command = ["docker", "pull", f"{self.image_name}"]
        except FileNotFoundError:
            print("Error: Docker is not installed.")
            print("Please install Docker and try again.")
            exit(0)
        try:
            # Run the docker pull command
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to pull {self.image_name}")
            print(e)

    def build_docker_image(self):
        try:
            # Build the Docker image using subprocess
            subprocess.run(
                [
                    "docker",
                    "build",
                    "-t",
                    self.image_name,
                    "-f",
                    f"{self.sim_path}/Dockerfile",
                    ".",
                ],
                check=True,
            )
            print(f"Docker image '{self.image_name}' built successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error building Docker image: {e}")

    def write_docker_file(self):
        with open(f"{self.sim_path}/Dockerfile", "w") as f:
            with open("requirements.txt", "r") as file:
                requirements = file.readlines()
            requirements = [requirement.strip() for requirement in requirements]

            f.write("# Use the efabless/dv:cocotb base image\n")
            f.write("FROM efabless/dv:cocotb\n")
            f.write("\n")
            # f.write("# Copy requirements.txt into the container\n")
            # f.write("WORKDIR /app\n")
            # f.write(f"COPY {self.user_project_path}/verilog/dv/cocotb/requirements.txt .\n")
            f.write("\n")
            f.write("# Install additional packages\n")
            f.write(f"RUN pip install --upgrade {' '.join(requirements)}")
            f.write("\n")
