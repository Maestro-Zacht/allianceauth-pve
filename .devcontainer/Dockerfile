ARG AA_DOCKER_TAG
FROM $AA_DOCKER_TAG

RUN cd /home/allianceauth
COPY .devcontainer/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./allianceauth_pve myauth/allianceauth_pve