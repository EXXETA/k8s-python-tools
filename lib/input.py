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
from abc import abstractmethod

from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, yes_no_dialog, prompt

"""This file contains files for user input mechanism and the usage of ALL external input libraries"""


class AbstractInputAdapter(object):
    """
    Abstract definition of an abstract input adapter. Any user interaction dialog or mechanism is implemented
    in subclasses
    """

    @abstractmethod
    def radio_list(self, title, text, options) -> str:
        ...

    @abstractmethod
    def string(self, title, message) -> str:
        ...

    @abstractmethod
    def yes_no(self, title, message) -> bool:
        ...

    def number(self, title, message) -> int:
        valid_input = False
        output = None
        while not valid_input:
            input = self.string(title, message)
            try:
                output = int(input)
                valid_input = True
            except ValueError:
                print("Invalid numeric integer input '%s'" % input)
        return output

    def prompt(self, message) -> str:
        return self.string("Input prompt", message)


class PromptToolkitAdapter(AbstractInputAdapter):
    """Implementation of prompt toolkit for cross plattform integration"""

    def yes_no(self, title, message) -> bool:
        ret = yes_no_dialog(
            title=title,
            text=message)
        print("User has chosen:", ret)
        return ret

    def radio_list(self, title, text, options) -> str:
        ret = radiolist_dialog("Select a " + title + ":", text, values=options)
        print("user selected:", ret)
        return ret

    def string(self, title, message) -> str:
        ret = input_dialog(title=title, text=message)
        print("user typed:", ret)
        return ret

    def prompt(self, message) -> str:
        ret = prompt(message + " ")
        return ret


class InquirerAdapter(AbstractInputAdapter):
    """Python inquirer implementation. Does not work on windows!"""

    def yes_no(self, title, message) -> bool:
        import inquirer
        options = ["No", "Yes"]
        print(title)
        questions = [
            inquirer.List(title,
                          choices=options),
        ]
        answers = inquirer.prompt(questions)
        print("User selected option:", answers[title])
        return answers[title] == "Yes"

    def radio_list(self, title, text, options) -> str:
        import inquirer
        questions = [
            inquirer.List(title,
                          message="Select a " + title + ":",
                          choices=options),
        ]
        answers = inquirer.prompt(questions)
        print("User selected:", title, answers[title])
        return answers[title]

    def string(self, title, message) -> str:
        # TODO
        pass


def get_current_input_adapter() -> AbstractInputAdapter:
    """
    Application wide definition of input mechanism - important for cross-plattform support as some
    libraries are working only on some OS.
    """
    return PromptToolkitAdapter()


def main():
    pass


if __name__ == "__main__":
    main()
