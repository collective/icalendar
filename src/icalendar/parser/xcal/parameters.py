from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar.parser.parameter import Parameters
from icalendar.parser.xcal.base import XCalParser

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from icalendar.parser.xcal.adapter import ElementAdapter
    from icalendar.prop.factory import TypesFactory


class XCalParametersParser(XCalParser):
    """A parser for <parameters>.

    Parameters:
        element: The xCal element to parse.
        types_factory: The types factory to use.
            If ``None`` is passed, the default TypesFactory is used.

    Example:

        The parameter ``element`` can be a ``parameters`` tag as shown below:

        .. code-block:: xml

            <parameters>
                <tzid>
                    <text>US/Eastern</text>
                </tzid>
            </parameters>

    """

    def __init__(
        self,
        element: Element | ElementAdapter,
        types_factory: TypesFactory | None = None,
    ) -> None:
        from icalendar.prop.factory import TypesFactory

        super().__init__(element)
        self._types_factory = (
            TypesFactory.instance() if types_factory is None else types_factory
        )
        self._parameters = Parameters()

    def parse_parameters(self) -> Parameters:
        """Parse all parameters until finished.

        Parameters are parsed once and are the same for all
        property values inside a property tag.
        This method parses the whole ``parameters`` tag collects them
        and returns them as a :class:`~icalendar.prop.parameters.Parameters` object.

        Returns:
            The parsed parameters.

        Raises:
            ~icalendar.error.XCalParsingError: If the provided xCal is invalid.
        """
        while not self.is_finished():
            self.parse_parameter()
        return self._parameters

    def parse_parameter(self) -> None:
        """Parse the next parameter that has not been parsed, yet.

        This function only parses one parameter inside the parser's ``element``
        parameter and adds it to the collected parameters.
        Each call parses a single parameter.

        Raises:
            ~icalendar.error.XCalParsingError: If the provided xCal is invalid.
            ~icalendar.parser.xcal.base.InvalidParserState:
                If all parameters have been parsed.

        Example:

            The example below shows a ``parameters`` tag with a
            ``tzid`` parameter.
            This function would only parse the ``tzid`` parameter.

            .. code-block:: xml

                <parameters>
                    <tzid>
                        <text>US/Eastern</text>
                    </tzid>
                </parameters>

        """
        parameters_parser = XCalParameterParser(self.child, self._types_factory)
        values = []
        while not parameters_parser.is_finished():
            values.append(parameters_parser.parse_parameter())
        if values:
            self._parameters[self.child.tag] = values[0] if len(values) == 1 else values
        self.done()


class XCalParameterParser(XCalParser):
    """A parser for one parameter."""

    def __init__(
        self,
        element: Element | ElementAdapter,
        types_factory: TypesFactory | None = None,
    ) -> None:
        from icalendar.prop.factory import TypesFactory

        super().__init__(element)
        self._types_factory = (
            TypesFactory.instance() if types_factory is None else types_factory
        )
        self._element_is_parsed = False

    def parse_parameter(self) -> str:
        """Parse one parameter value if present.

        Returns:
            The parsed parameters.

        Example:

        .. code-block:: xml

            <tzid>
                <text>US/Eastern</text>
            </tzid>
        """
        child = self.parse_tag()
        result = child.get_xsd_string()
        if child.tag == "boolean":
            result = result.upper()
        return result
