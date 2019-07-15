#
# Copyright (c) 2019 EXXETA AG and others.
#
# This file is part of k8s-python-tools
# (see https://github.com/EXXETA/k8s-python-tools).
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import os
import re

from jinja2 import Environment, FileSystemLoader

"""load self-defined generated_library.yml and use this information to generate api methods.
   using jinja2 templating engine to generate python files
"""

__location__ = os.path.join(os.getcwd(), os.path.dirname(__file__))

try:
    from yaml import CLoader as Loader, CDumper as Dumper, load
except ImportError:
    from yaml import Loader, Dumper

text_io = open(os.path.join(__location__, 'generated_library.yml'), 'r')
data = load(text_io, Loader=Loader)
text_io.close()

env = Environment(
    loader=FileSystemLoader(os.path.join(__location__, "templates")),
    # autoescape=select_autoescape(['html'])
)


def camelcase_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


env.filters['normalize'] = camelcase_to_snake_case


# generating api methods
for i in data["lib_def"]:
    file_name = data["lib_def"][i]["file"]
    template_name = data["lib_def"][i]["template"]
    entries = data["lib_def"][i]["entries"]
    print("generated", "./lib/" + file_name)

    template = env.get_template(template_name)
    rendered = template.render(entries=entries)

    f = open(os.path.join(__location__, "./lib/" + file_name), "w")
    f.write(rendered)
    f.close()

# generating api actions
for i in data["actions"]:
    base_path = data["actions"][i]["destination"]
    template_name = data["actions"][i]["template"]
    entries = data["actions"][i]["entries"]
    print("auto-generated", len(entries), "actions in destination", base_path)

    template = env.get_template(template_name)
    for item in entries:
        rendered = template.render(item=item)
        f = open(os.path.join(__location__, "./lib/" + base_path + "/" +
                              camelcase_to_snake_case(item["name"]) + ".py"), "w")
        f.write(rendered)
        f.close()

print("OK")
