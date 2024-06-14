# -*- coding: utf-8 -*-

"""
Author: Deniz Aydin, @daydin on GitHub.

--------------------------------------------
Code based on

(c) Varun Malhotra 2013
Source Code: https://github.com/softvar/json2html


Contributors:
-------------
1. Michel Müller (@muellermichel), https://github.com/softvar/json2html/pull/2
2. Daniel Lekic (@lekic), https://github.com/softvar/json2html/pull/17


--------
"""
import collections
import json as json_parser
from html import escape as html_escape
from jinja2 import Environment, select_autoescape, FileSystemLoader

templateLoader = FileSystemLoader(searchpath="./templates")

env = Environment(
    loader=templateLoader,
    autoescape=select_autoescape()
)

template = env.get_template("entry.html")

text = str
text_types = (str,)


class JSON2html:
    def __init__(self):

        self.escape = None
        self.style = None

    def convert(self, json="", table_attributes='border="1"', encode=False, escape=True, style='MLA'):
        """
            Convert JSON to HTML Table, formatted as per the specification.
            :param style: describes the desired citation output style
        """

        self.escape = escape
        self.style = style
        json_input = None
        if not json:
            json_input = {}
        elif type(json) in text_types:
            try:
                json_input = json_parser.loads(json)
            except ValueError as e:
                # so the string passed here is actually not a json string
                # - let's analyze whether we want to pass on the error or use the string as-is as a text node
                if u"Expecting property name" in text(e):
                    # if this specific json loads error is raised, then the user probably actually wanted to pass
                    # json, but made a mistake
                    raise e
                json_input = json
        else:
            json_input = json
        converted = self.convert_json_node(json_input)
        if encode:
            return converted.encode('ascii', 'xmlcharrefreplace')
        return converted

    def convert_json_node(self, json_input):
        # todo: edit the docstring once you figure out what to do with non-dict JSONs, if they exist
        """
            Dispatch JSON input according to the outermost type and process it
            to generate the super awesome HTML format.
            We try to adhere to duck typing such that users can just pass all kinds
            of funky objects to json2html that *behave* like dicts and lists and other
            basic JSON types.
        """
        if type(json_input) in text_types:
            if self.escape:
                return html_escape(text(json_input))
            else:
                return text(json_input)
        if hasattr(json_input, 'items'):
            return self.convert_object(json_input)

        # if hasattr(json_input, '__iter__') and hasattr(json_input, '__getitem__'):
        #     return self.convert_list(json_input)
        return text(json_input)

    def convert_object(self, json_input):
        """
            Call out to the appropriate formatter function to output biblios in the desired citation style.
        """
        if not json_input:
            return ""  # avoid empty tables

        try:
            if self.style == 'MLA':
                return self.format_mla(json_input)
        except ValueError:
            raise ValueError(f'The supplied citation style {self.style} is not recognized.')

        return

    @staticmethod
    def format_mla(json_input):
        """
            MLA-style citation formatter.
        """
        entries = json_input["items"]

        for entry in entries:
            f = open(f"content/{'_'.join(str.split(entry['key'], '/'))}.html", "w")

            desired_key_order = ['creators', 'title', 'publisher',
                                 'place', 'volume', 'doi', 'url', 'accessDate', 'date', 'key']
            order = dict(enumerate(desired_key_order))
            selected_entry = {k: v for k, v in entry.items() for desired_key in desired_key_order if k == desired_key}
            mapping = {i: {k: v} for k, v in selected_entry.items() for i, j in order.items() if j == k and v}

            ordered_dict = collections.OrderedDict(sorted(mapping.items()))

            simplified_dict = {field: field_value for key, value in ordered_dict.items() for field, field_value in
                               value.items()}

            output_text = template.render(
                creators=simplified_dict.get('creators'),
                title=simplified_dict.get('title'),
                publisher=simplified_dict.get('publisher'),
                physical_location=simplified_dict.get('place'),
                publication_date=simplified_dict.get('date'),
                volume=simplified_dict.get('volume'),
                doi=simplified_dict.get('doi'),
                url=simplified_dict.get('url'),
                entry_id=simplified_dict.get('key'),
                accessed_date=simplified_dict.get('accessDate')
            )

            f.write(output_text)
            f.close()
