# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
FROM fedora:30

RUN dnf --disablerepo updates-modular --disablerepo fedora-modular \
    install -y git gcc python3-devel nmap-ncat

#RUN apt install ansible
WORKDIR /usr/app

COPY ./requirements.txt /usr/app/requirements.txt

RUN git clone https://github.com/ansible/ansible --branch v2.8.0rc3 && \
    git clone https://review.opendev.org/openstack/openstacksdk && \
    cd openstacksdk && \
    git fetch https://review.opendev.org/openstack/openstacksdk \
      refs/changes/41/659841/2 && git checkout FETCH_HEAD

RUN cd openstacksdk && python3 setup.py install --user
RUN cd ansible && python3 setup.py install --user

RUN pip3 install --user -r /usr/app/requirements.txt

#FROM fedora:30

#RUN dnf --disablerepo updates-modular --disablerepo fedora-modular \
#    install -y ansible

#COPY --from=builder /root/.local/ /root/.local

COPY ./entrypoint.sh /usr/app
COPY ./test.py /usr/app
# COPY ./proxy.py /root/.local/lib/python3.7/site-packages/openstack/proxy.py

ENV OS_CLOUD=otc
ENV PATH=/root/.local/bin:$PATH

CMD ["/usr/app/entrypoint.sh"]
