from enum import IntEnum
from typing import Any

from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.ext.autodoc import ClassDocumenter, bool_option, get_class_members

from roles_royce.constants import StrEnum
from roles_royce.protocols.base import ContractMethod


class ContractMethodDocumenter(ClassDocumenter):
    objtype = "evmmethod"
    directivetype = ClassDocumenter.objtype
    priority = 10 + ClassDocumenter.priority
    option_spec = dict(ClassDocumenter.option_spec)

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        try:
            return issubclass(member, ContractMethod)
        except TypeError:
            return False

    def get_object_members(self, want_all: bool):
        return False, []

    def add_content(self, more_content) -> None:
        super().add_content(more_content)

        source_name = self.get_sourcename()
        method_object: ContractMethod = self.object
        self.add_line("", source_name)

        if isinstance(method_object.target_address, property):
            target_addres_text = method_object.target_address.__doc__
        else:
            target_addres_text = repr(method_object.target_address)
        self.add_line(f"**target_address**: {target_addres_text}", source_name)
        self.add_line("", source_name)
        self.add_line(f"**fixed_arguments**: {method_object.fixed_arguments}", source_name)


class EnumDocumenter(ClassDocumenter):
    priority = 10 + ClassDocumenter.priority
    _obj_type = None

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        try:
            return issubclass(member, cls._obj_type)
        except TypeError:
            return False

    def get_object_members(self, want_all: bool):
        members_check_module, members = super().get_object_members(want_all)
        # filter the enum members so they are not documented twice
        members = filter(lambda member: not isinstance(member[1], self.object), members)
        return members_check_module, members

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header("")

    def format_member_value(self, value):
        return value

    def add_content(self, more_content: StringList | None) -> None:
        super().add_content(more_content)
        source_name = self.get_sourcename()
        enum_object = self.object
        self.add_line("", source_name)

        for the_member_name, enum_member in enum_object.__members__.items():
            the_member_value = self.format_member_value(enum_member.value)

            self.add_line(f"**{the_member_name}**: {the_member_value}", source_name)
            self.add_line("", source_name)


class IntEnumDocumenter(EnumDocumenter):
    objtype = "intenum"
    _obj_type = IntEnum
    option_spec = dict(ClassDocumenter.option_spec)
    directivetype = ClassDocumenter.objtype
    option_spec["hex"] = bool_option

    def format_member_value(self, value):
        if self.options.hex:
            value = hex(value)
        return value


class StrEnumDocumenter(EnumDocumenter):
    objtype = "strenum"
    _obj_type = StrEnum
    option_spec = dict(ClassDocumenter.option_spec)
    directivetype = ClassDocumenter.objtype


def setup(app: Sphinx) -> None:
    app.setup_extension("sphinx.ext.autodoc")  # Require autodoc extension
    app.add_autodocumenter(ContractMethodDocumenter)
    app.add_autodocumenter(IntEnumDocumenter)
    app.add_autodocumenter(StrEnumDocumenter)
