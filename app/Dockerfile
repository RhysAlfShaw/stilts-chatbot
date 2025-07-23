FROM condaforge/mambaforge:latest AS development

# Set timezone
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy environment.yml to a temp location so we can set up the Conda
# environment in the container.
COPY environment.yml /tmp/conda-tmp/

RUN mamba env create -n devcontainer -f /tmp/conda-tmp/environment.yml \
    && rm -rf /tmp/conda-tmp \
    && mamba clean -afy


WORKDIR /workspace/app

EXPOSE 1007
# This line is overriden by docker-compose.yml
CMD ["/opt/conda/envs/devcontainer/bin/python3", "-u", "-m", "src", "--reload"]
