__author__ = 'Alexander Dethof'


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
            column_separator_name = 'semicolon'
    ):
        self.__file_name = file_name
        self.__extension = extension
        self.__comment_symbol = comment_symbol
        self.__column_separator = column_separator
        self.__column_separator_name = column_separator_name
        self.__header_doc = header_doc
        self.__fields = fields
        self.__data = data

        self.__children = []
        self.__siblings = []
        self.__parent = None

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

    def __finalize(self):
        self._cfd__file_handler.close()
        return self

    def __add_comment_text(self, comment_text):
        assert isinstance(self._cfd__file_handler, file)
        assert isinstance(comment_text, basestring)

        comment_lines = comment_text.split('\n')
        for comment_line in comment_lines:
            self._cfd__file_handler.write(self.__comment_symbol + ' ' + comment_line)

        return self

    def __add_empty_comment_line(self):
        return self.__add_comment_text('')

    def __add_file_header(self):
        return self.__add_comment_text(self.__file_name.upper()) \
                   .__add_empty_comment_line() \
                   .__add_comment_text(self.__header_doc) \
                   .__add_empty_comment_line()

    def __add_field_description(self):
        assert isinstance(self.__fields, list)

        self.__add_comment_text('Fields:')

        for field_description in self.__fields:
            assert isinstance(field_description, dict)
            assert 'name' in field_description
            assert 'type' in field_description
            assert 'doc' in field_description

            self.__add_comment_text(
                '* <%s> %s: %s' % (field_description['type'], field_description['name'], field_description['doc'])
            )

        return self.__add_empty_comment_line()

    def __add_column_separation_comment(self):
        return self.__add_comment_text('NOTE: The table entries are separated by a %s' % self.__column_separator_name) \
                   .__add_empty_comment_line()

    def __add_column_headers(self):
        assert isinstance(self.__fields, list)

        field_names = []
        for field_description in self.__fields:
            assert isinstance(field_description, dict)
            assert 'name' in field_description

            field_names = field_description['name']

        self._cfd__file_handler.write(self.__column_separator.join(field_names))

    def __init_file(self, path):
        assert isinstance(path, basestring)

        from os.path import extsep as FILE_EXTENSION_SEPARATOR, exists
        file_path = path + self.__file_name + FILE_EXTENSION_SEPARATOR + self.__extension

        if exists(file_path):
            raise Exception("The file `%s` already exists!")

        self.__create_file(file_path) \
            .__add_file_header() \
            .__add_field_description() \
            .__add_column_separation_comment() \
            .__add_column_headers() \
            ._cfd__finalize()

