__author__ = 'Alexander Dethof'

from metaConfig.metaTableField import MetaTableField
import textwrap


class MetaTable:

    def __init__(
            self,
            file_name,
            extension='csv',
            fields=list(),
            data=list(),
            header_doc='',
            comment_symbol='#',
            column_separator = ';',
            column_separator_name = 'semicolon',
            footer_doc=''
    ):
        self.__file_name = file_name
        self.__extension = extension
        self.__comment_symbol = comment_symbol
        self.__column_separator = column_separator
        self.__column_separator_name = column_separator_name
        self.__header_doc = header_doc
        self.__fields = fields
        self.__data = data
        self.__footer_doc = footer_doc

        self.__children = []
        self.__siblings = []
        self.__parent = None
        self.__is_generated = False

    def set_parent(self, parent):
        self.__parent = parent

    def has_sibling(self, sibling):
        return sibling in self.__siblings

    def add_sibling(self, sibling):
        self.__siblings.append(sibling)

        if not sibling.has_sibling(self):
            sibling.add_sibling(self)

    def add_siblings(self, siblings):
        assert isinstance(siblings, list)
        for sibling in siblings:
            self.add_sibling(sibling)

    def add_child(self, child):
        assert isinstance(child, MetaTable)
        self.__children.append(child)
        child.set_parent(self)

    def add_children(self, children):
        assert isinstance(children, list)
        for node in children:
            self.add_child(node)

    def __create_file(self, file_path):
        assert isinstance(file_path, basestring)
        self._cfd__file_handler = open(file_path, 'w')

        return self

    def __finalize_file(self):
        self._cfd__file_handler.close()
        return self

    def __add_comment_lines(self, comment_lines):
        for comment_line in comment_lines:
            self._cfd__file_handler.write(self.__comment_symbol + ' ' + comment_line + '\n')

        return self

    def __add_comment_text(self, comment_text):
        assert isinstance(self._cfd__file_handler, file)
        assert isinstance(comment_text, basestring)

        comment_lines = comment_text.split('\n')
        self.__add_comment_lines(comment_lines)

        return self

    def __add_empty_comment_line(self):
        return self.__add_comment_text('')

    def __add_file_header(self):
        table_name_upper = self.__file_name.upper()
        doc = self.__header_doc.replace('\n', ' ')
        doc = textwrap.wrap(doc, 120)

        return self.__add_comment_text(table_name_upper) \
                   .__add_comment_text('=' * len(table_name_upper)) \
                   .__add_empty_comment_line() \
                   .__add_comment_lines(doc) \
                   .__add_empty_comment_line()

    def __add_field_description(self):
        assert isinstance(self.__fields, list)

        self.__add_comment_text('Fields:')
        self.__add_comment_text('-------\n')

        max_type_letter_count = 0
        max_name_letter_count = 0
        for field_description in self.__fields:
            assert isinstance(field_description, MetaTableField)

            type_letter_count = len(str(field_description.get_type()))
            name_letter_count = len(field_description.get_name())

            if type_letter_count > max_type_letter_count:
                max_type_letter_count = type_letter_count

            if name_letter_count > max_name_letter_count:
                max_name_letter_count = name_letter_count

        for field_description in self.__fields:
            field_name = field_description.get_name()
            field_type = str(field_description.get_type())

            type_space_count = max_type_letter_count - len(field_type)

            field_comment = '* %s%s %s' % (field_type, ' ' * type_space_count, field_name)

            line_space_count = max_name_letter_count + max_type_letter_count + 2  # + 3 for '* '

            field_doc = field_description.get_doc()
            if field_doc:
                name_space_count = max_name_letter_count - len(field_name)
                field_comment += ' ' * name_space_count + ' : '

                field_doc.replace('\n', ' ')

                field_doc_elements = textwrap.wrap(field_doc, 85)

                field_comment += field_doc_elements[0]
                del field_doc_elements[0]

                # + 3 for ' : ' + 1 separator space between type and name
                field_doc_line_spacer = '\n' + ' ' * (line_space_count + 4)
                for field_doc_element in field_doc_elements:
                    field_comment += field_doc_line_spacer + field_doc_element

            variants = field_description.get_variants()
            if isinstance(variants, list) or isinstance(variants, tuple):
                variant_values = variants
            elif isinstance(variants, dict):
                variant_values = variants.keys()
            else:
                raise Exception("Invalid variants given!")

            if variant_values:
                variant_spacer = '\n' + ' ' * (line_space_count + 5)  # + 3 for ' : ' and + 2 for tab space
                max_variant_letter_count = 0
                if isinstance(variants, dict):
                    for variant_value in variant_values:
                        variant_letter_count = len(variant_value)
                        if variant_letter_count > max_variant_letter_count:
                            max_variant_letter_count = variant_letter_count

                field_comment += '\n'
                for variant_value in variant_values:
                    variant_space_count = max_variant_letter_count - len(variant_value)

                    field_comment += variant_spacer \
                                  +  ' >> ' \
                                  +  variant_value \
                                  +  ' ' * variant_space_count

                    if isinstance(variants, dict): # there exists a documentation!!
                        variant_doc_elements = textwrap.wrap(variants[variant_value], 50)
                        field_comment += ' : ' + variant_doc_elements[0]
                        del variant_doc_elements[0]

                        # + 3 for ' : ' + 4 for ' >> '
                        variant_doc_element_spacer = variant_spacer + ' ' * (7 + max_variant_letter_count)
                        for variant_doc_element in variant_doc_elements:
                            field_comment += variant_doc_element_spacer + variant_doc_element

            field_comment += '\n'
            self.__add_comment_text(field_comment)

        return self.__add_empty_comment_line()

    def __add_column_separation_comment(self):
        return self.__add_comment_text('The table columns are separated by a %s!' % self.__column_separator_name)

    def __add_column_headers(self):
        assert isinstance(self.__fields, list)

        field_names = []
        for field_description in self.__fields:
            assert isinstance(field_description, MetaTableField)
            field_names.append(field_description.get_name())

        self._cfd__file_handler.write(self.__column_separator.join(field_names))
        return self

    def __add_annotations(self):

        self.__add_comment_text('Annotation:') \
            .__add_comment_text('-----------\n') \

        if self.__footer_doc:
            self.__add_comment_text(self.__footer_doc) \
                .__add_empty_comment_line()

        self.__add_column_separation_comment() \
            .__add_empty_comment_line()

        return self

    def generate_file(self, path):
        assert isinstance(path, basestring)

        if self.__is_generated:
            return

        print "Generate config file " + self.__file_name + " @ " + path

        # noinspection PyPep8Naming
        from os.path import extsep as FILE_EXTENSION_SEPARATOR, exists
        file_path = path + self.__file_name + FILE_EXTENSION_SEPARATOR + self.__extension

        if exists(file_path):
            raise Exception("The file `%s` already exists!")

        self.__create_file(file_path) \
            .__add_file_header() \
            .__add_field_description() \
            .__add_annotations() \
            .__add_column_headers() \
            .__finalize_file()

        self.__is_generated = True

        if len(self.__siblings) > 0:
            for sibling in self.__siblings:
                assert isinstance(sibling, MetaTable)
                sibling.generate_file(path)

        if len(self.__children) > 0:
            # noinspection PyPep8Naming
            from os.path import sep as PATH_SEPARATOR, exists
            child_path = path + self.__file_name + PATH_SEPARATOR

            if not exists(child_path):
                from os import mkdir
                mkdir(child_path)

            for child in self.__children:
                assert isinstance(child, MetaTable)
                child.generate_file(child_path)



