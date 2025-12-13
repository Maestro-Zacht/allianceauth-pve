ARG AA_DOCKER_TAG
FROM $AA_DOCKER_TAG

USER root
RUN apt-get update && apt-get install make gnupg2 gettext curl wget -y
USER ${AUTH_USER}

# set env
ENV NVM_DIR=${AUTH_HOME}/.nvm
ENV NODE_VERSION=22

# Install Node.js
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
RUN bash -c "source ${NVM_DIR}/nvm.sh && nvm install ${NODE_VERSION} && nvm alias default ${NODE_VERSION} && nvm use default && nvm version | xargs -I {} ln -s $NVM_DIR/versions/node/{} $NVM_DIR/versions/node/v$NODE_VERSION"
ENV PATH=${NVM_DIR}/versions/node/v${NODE_VERSION}/bin:$PATH

RUN cd ${AUTH_HOME}
COPY .devcontainer/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /workspace
RUN pip install -e /workspace

RUN allianceauth update myauth