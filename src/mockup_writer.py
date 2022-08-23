#!/usr/bin/env python3

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import List, Tuple

from os.path import dirname, splitext
from os import listdir


class Variable:
    def __init__(self, type: str, name: str) -> None:
        self.type = type
        self.name = name

    def get_definition(self) -> str:
        return f"{self.type} {self.name}"


class Function:
    def __init__(self, type: str, name: str, params: List[Variable]) -> None:
        self.type = type
        self.name = name
        self.params = params

    def get_signature(self) -> str:
        arguments = ", ".join(f"{param.type} {param.name}" for param in self.params)
        return f"{self.type} {self.name}({arguments})"

    def has_return_value(self) -> bool:
        return self.type != "void"

    def get_call(self) -> str:
        arguments = ", ".join(f"{param.name}" for param in self.params)
        return f"{self.name}({arguments})"

    def get_param_types(self) -> str:
        param_types = ", ".join(f"{param.type}" for param in self.params)
        return f"{param_types}"


class MockupWriter:
    def __init__(self) -> None:
        self.headers = []
        self.variables = []
        self.functions = []
        self.template_dir = f"{dirname(__file__)}/templates"
        self.mockup_style = "gmock"
        self.environment = Environment(
            loader=FileSystemLoader(f"{self.template_dir}/{self.mockup_style}"),
            keep_trailing_newline=True,
            trim_blocks=True,
        )
        self.template_mockup_h = self.environment.get_template("mockup.h.j2")
        self.template_mockup_cc = self.environment.get_template("mockup.cc.j2")

    def set_mockup_style(self, mockup_style: str) -> None:
        self.mockup_style = mockup_style

    def add_header(self, name: str) -> None:
        """Add a header to be included in mockup"""
        if name not in self.headers:
            self.headers.append(name)

    def add_variable(self, type: str, name: str) -> None:
        """Add a variable definition"""
        self.variables.append(Variable(type, name))

    def add_function(self, type: str, name: str, params: List[Tuple[str, str]] = []) -> None:
        """Add a variable definition"""
        self.functions.append(Function(type, name, [Variable(param[0], param[1]) for param in params]))

    def get_mockup_h(self) -> str:
        return self.template_mockup_h.render(
            headers=sorted(self.headers), functions=sorted(self.functions, key=lambda x: x.name)
        )

    def _take_name(self, elem):
        return elem[1]

    def get_mockup_cc(self):
        return self.template_mockup_cc.render(
            variables=sorted(self.variables, key=lambda x: x.name),
            functions=sorted(self.functions, key=lambda x: x.name),
        )
        
    def write(self, outdir: Path) -> None:
        for file in listdir(f"{self.template_dir}/{self.mockup_style}"):
            if file.endswith(".j2"):
                Path(outdir, f"{splitext(file)[0]}").write_text(self.environment.get_template(f"{file}").render(
                    headers=sorted(self.headers),
                    variables=sorted(self.variables, key=lambda x: x.name),
                    functions=sorted(self.functions, key=lambda x: x.name)
                ))
