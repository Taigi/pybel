# -*- coding: utf-8 -*-

"""
Gene substitutions are legacy statements defined in BEL 1.0. BEL 2.0 reccomends using HGVS strings. Luckily,
the information contained in a BEL 1.0 encoding, such as :code:`g(HGNC:APP,sub(G,275341,C))` can be
automatically translated to the appropriate HGVS :code:`g(HGNC:APP, var(c.275341G>C))`, assuming that all
substitutions are using the reference coding gene sequence for numbering and not the genomic reference.
The previous statements both produce the underlying data:

.. code::

    {
        'function': 'Gene',
        'identifier': {
            'namespace': 'HGNC',
            'name': 'APP'
        },
        'variants': [
            {
                'kind': 'hgvs',
                'identifier': 'c.275341G>C'
            }
        ]
    }
"""

import logging

from pyparsing import pyparsing_common as ppc

from .variant import VariantParser
from ..baseparser import BaseParser, one_of_tags, nest
from ..language import dna_nucleotide
from ...constants import HGVS, KIND

log = logging.getLogger(__name__)


class GsubParser(BaseParser):
    REFERENCE = 'reference'
    POSITION = 'position'
    VARIANT = 'variant'

    def __init__(self):
        gsub_tag = one_of_tags(tags=['sub', 'substitution'], canonical_tag=HGVS, identifier=KIND)
        self.language = gsub_tag + nest(dna_nucleotide(self.REFERENCE), ppc.integer(self.POSITION),
                                        dna_nucleotide(self.VARIANT))
        self.language.setParseAction(self.handle_gsub)

    def handle_gsub(self, s, l, tokens):
        upgraded = 'c.{}{}>{}'.format(tokens[self.POSITION], tokens[self.REFERENCE], tokens[self.VARIANT])
        log.debug('legacy sub() %s upgraded to %s', s, upgraded)
        tokens[VariantParser.IDENTIFIER] = upgraded
        del tokens[self.POSITION]
        del tokens[self.REFERENCE]
        del tokens[self.VARIANT]
        return tokens

    def get_language(self):
        return self.language
