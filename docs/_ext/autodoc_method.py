from __future__ import annotations

from roles_royce.protocols.base import Method
from typing import Any

from sphinx.ext.autodoc import ObjectMember
from sphinx.ext.autodoc import ClassDocumenter, get_class_members
from sphinx.application import Sphinx


class MethodDocumenter(ClassDocumenter):
    objtype = 'evmmethod'
    directivetype = ClassDocumenter.objtype
    priority = 10 + ClassDocumenter.priority
    option_spec = dict(ClassDocumenter.option_spec)

    @classmethod
    def can_document_member(cls,
                            member: Any, membername: str,
                            isattr: bool, parent: Any) -> bool:
        try:
            return issubclass(member, Method)
        except TypeError:
            return False

    def get_object_members(self, want_all: bool):
        return False, []
        all_members = get_class_members(self.object, self.objpath, self.get_attr,
                                    self.config.autodoc_inherit_docstrings)
        members = []
        for member_name, member_value in all_members.items():
            if member_name in ['target_address', 'fixed_arguments']:
                if isinstance(member_value.object, property) and member_name == "target_address":
                    member_value = ObjectMember(name="target_address", obj=member_value.object.__doc__)
                members.append(member_value)
                member_value.docstring = " a"

        return False, members

    def add_content(self, more_content) -> None:
        super().add_content(more_content)

        source_name = self.get_sourcename()
        method_object: Method = self.object
        self.add_line('', source_name)

        if isinstance(method_object.target_address, property):
            target_addres_text = method_object.target_address.__doc__
        else:
            target_addres_text = repr(method_object.target_address)
        self.add_line(f"**target_address**: {target_addres_text}", source_name)
        self.add_line('', source_name)
        self.add_line(f"**fixed_arguments**: {method_object.fixed_arguments}", source_name)


from enum import IntEnum
from typing import TYPE_CHECKING, Any

from sphinx.ext.autodoc import ClassDocumenter, bool_option

if TYPE_CHECKING:
    from docutils.statemachine import StringList

    from sphinx.application import Sphinx


class IntEnumDocumenter(ClassDocumenter):
    objtype = 'intenum'
    directivetype = ClassDocumenter.objtype
    priority = 10 + ClassDocumenter.priority
    option_spec = dict(ClassDocumenter.option_spec)
    option_spec['hex'] = bool_option

    @classmethod
    def can_document_member(cls,
                            member: Any, membername: str,
                            isattr: bool, parent: Any) -> bool:
        try:
            return issubclass(member, IntEnum)
        except TypeError:
            return False

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header("")

    def add_content(self, more_content: StringList | None) -> None:

        super().add_content(more_content)

        source_name = self.get_sourcename()
        enum_object: IntEnum = self.object
        use_hex = self.options.hex
        self.add_line('', source_name)

        for the_member_name, enum_member in enum_object.__members__.items():
            the_member_value = enum_member.value
            if use_hex:
                the_member_value = hex(the_member_value)

            self.add_line(f"**{the_member_name}**: {the_member_value}", source_name)
            self.add_line('', source_name)

def setup(app: Sphinx) -> None:
    app.setup_extension('sphinx.ext.autodoc')  # Require autodoc extension
    app.add_autodocumenter(MethodDocumenter)
    app.add_autodocumenter(IntEnumDocumenter)






