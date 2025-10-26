"""Link property.

The link property is specified in :rfc:`9253`.
"""


class vLink(str):  # noqa: N801
    """Link

    Value Name: LINK

    Purpose:
        This property provides a reference to external
        information related to a component.

    Value type:
        URI, UID, or XML-REFERENCE


    """

    __slots__ = ()


__all__ = ["vLink"]
