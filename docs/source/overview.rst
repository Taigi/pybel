Overview
========

Background on Systems Biology Modelling
---------------------------------------

Biological Expression Language (BEL)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Biological Expression Language (BEL) is a domain specific language that enables the expression of complex molecular
relationships and their context in a machine-readable form. Its simple grammar and expressive power have led to its
successful use in the `IMI <https://www.imi.europa.eu/>`_ project, `AETIONOMY <http://www.aetionomy.eu/>`_, to describe
complex disease networks with several thousands of relationships. For a detailed explanation, see the
BEL `1.0 <http://openbel.org/language/version_1.0/bel_specification_version_1.0.html>`_ and
`2.0 <http://openbel.org/language/version_2.0/bel_specification_version_2.0.html>`_ specifications.

OpenBEL Links
~~~~~~~~~~~~~

- OpenBEL on `Google Groups <https://groups.google.com/forum/#!forum/openbel-discuss>`_
- OpenBEL `Wiki <https://wiki.openbel.org/>`_
- OpenBEL on `GitHub <https://github.com/OpenBEL>`_
- Chat on `Gitter <https://gitter.im/OpenBEL/chat>`_

Design Considerations
---------------------
Missing Namespaces and Improper Names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The use of openly shared controlled vocabularies (namespaces) within BEL facilitates the exchange and consistency of
information. Finding the correct :code:`namespace:name` pair is often a difficult part of the curation process.

Outdated Namespaces
~~~~~~~~~~~~~~~~~~~
OpenBEL provides a variety of `namespaces <https://wiki.openbel.org/display/BELNA/Namespaces+Overview>`_
covering each of the BEL function types. These namespaces are generated by code found at
https://github.com/OpenBEL/resource-generator and distributed at http://resources.openbel.org/belframework/.

This code has not been maintained to reflect the changes in the underlying resources, so this repository has been
forked and updated at https://github.com/pybel/resource-generator to reflect the most recent versions of the underlying
namespaces. The files are now distributed using the Fraunhofer SCAI ownCloud server. An example list of these namespaces
can be found in the `template BEL script <https://github.com/pybel/pybel-resources/blob/master/template.bel>`_ in the
`PyBEL Resources <https://github.com/pybel/pybel-resources>`_ repository on GitHub.

Generating New Namespaces
~~~~~~~~~~~~~~~~~~~~~~~~~
In some cases, it is appropriate to design a new namespace, using the
`custom namespace specification <http://openbel-framework.readthedocs.io/en/latest/tutorials/building_custom_namespaces.html>`_
provided by the OpenBEL Framework. Scripts for generating additional resource files have been posted to the
`PyBEL Notebooks <https://github.com/pybel/pybel-notebooks/tree/master/resources>`_ repository on GitHub.

Synonym Issues
~~~~~~~~~~~~~~
Due to the huge number of terms across many namespaces, it's difficult for curators to know the domain-specific
synonyms that obscure the controlled/preferred term. However, the issue of synonym resolution and semantic searching
has already been generally solved by the use of ontologies. Besides just a controlled vocabulary, they also a
hierarchical model of knowledge, synonyms with cross-references to databases and other ontologies, and other
information semantic reasoning. Ontologies in the biomedical domain can be found at `OBO <obofoundry.org>`_ and
`EMBL-EBI OLS <http://www.ebi.ac.uk/ols/index>`_.

Additionally, as a tool for curators, the EMBL Ontology Lookup Service (OLS) allows for semantic searching. Simple
queries for the terms 'mitochondrial dysfunction' and 'amyloid beta-peptides' immediately returned results from
relevant ontologies, and ended a long debate over how to represent these objects within BEL. EMBL-EBI also provides a
programmatic API to the OLS service, for searching terms (http://www.ebi.ac.uk/ols/api/search?q=folic%20acid) and
suggesting resolutions (http://www.ebi.ac.uk/ols/api/suggest?q=folic+acid)

Implementation
--------------
PyBEL is implemented using the PyParsing module. It provides flexibility and incredible speed in parsing compared
to regular expression implementation. It also allows for the addition of parsing action hooks, which allow
the graph to be checked semantically at compile-time.

It uses SQLite to provide a consistent and lightweight caching system for external data, such as
namespaces, annotations, ontologies, and SQLAlchemy to provide a cross-platform interface. The same data management
system is used to store graphs for high-performance querying.

Extensions to BEL
-----------------
The PyBEL compiler is fully compliant with both BEL v1.0 and v2.0 and automatically upgrades legacy statements.
Additionally, we have included several additions to the BEL specification to enable expression of important concepts
in molecular biology that were previously missing and to facilitate integrating new data types. A short example is the
inclusion of protein oxidation in the default BEL namespace for protein modifications. Other, more elaborate additions
are outlined below.

Syntax for Epigenetics
~~~~~~~~~~~~~~~~~~~~~~
We introduce the gene modification function, gmod(), as a syntax for encoding epigenetic modifications. Its usage
mirrors the pmod() function for proteins and includes arguments for methylation.

For example, the methylation of NDUFB6 was found to be negatively correlated with its expression in a study of insulin
resistance and Type II diabetes. This can now be expressed in BEL such as in the following statement:

``g(HGNC:NDUFB6, gmod(Me)) negativeCorrelation r(HGNC:NDUFB6)``

References:

- https://www.ncbi.nlm.nih.gov/pubmed/17948130
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4655260/

Definition of Namespaces as Regular Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
BEL imposes the constraint that each identifier must be qualified with an enumerated namespace to enable semantic
interoperability and data integration. However, enumerating a namespace with potentially billions of names, such as
dbSNP, poses a computational issue. We introduce syntax for defining namespaces with a consistent pattern using a
regular expression to overcome this issue. For these namespaces, semantic validation can be perform in post-processing
against the underlying database. The dbSNP namespace can be defined with a syntax familiar to BEL annotation
definitions with regular expressions as follows:

``DEFINE NAMESPACE dbSNP AS PATTERN "rs[0-9]+"``

Definition of Resources using OWL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
One constraint imposed by the BEL language is that definitions of namespaces and annotations must follow a specific
format. However, the creation and maintenance of terminologies in the biological domain has tended towards the usage
of the Web Ontology Format (OWL). Services such as the Ontology Lookup Service allow for standardized querying and
search of these resources, and provide an important semantic integration layer that previous software tools for BEL
did not include. PyBEL allows for these resources to be named directly in definitions with the following syntax:

``DEFINE ANNOTATION CELL AS OWL "http://purl.obolibrary.org/obo/cl/releases/2016-11-23/cl.owl"``
``DEFINE NAMESPACE DO AS OWL "http://purl.obolibrary.org/obo/doid/releases/2017-05-05/doid.owl"``

This allows PyBEL to import the semantic information from the ontology as well, and provide much more rich
algorithms that take into account the hierarchy and synonyms provided.

PyBEL uses the `onto2nx <https://github.com/cthoyt/onto2nx>`_ package to parse OWL documents in many different
formats, including OWL/XML, RDF/XML, and RDF.

Explicit Node Labels
~~~~~~~~~~~~~~~~~~~~
While the BEL 2.0 specification made it possible to represent new terms, such as the APOE gene with two variants
resulting in the E2 allele, it came at the price of encoding terms in a technical and less readable way. An explicit
statement for labeling nodes has been added, such that the resulting data structure will have a label for the node:

``g(HGNC:APOE, var(c.388T>C), var(c.526C>T)) labeled "APOE E2"``

When InChI is used, these strings are very hard to visualize. Using a label is helpful for later visualization:

``a(INCHI:"InChI=1S/C20H28N2O5/c1-3-27-20(26)16(12-11-15-8-5-4-6-9-15)21-14(2)18(23)22-13-7-10-17(22)19(24)25/h4-6,8-9,14,16-17,21H,3,7,10-13H2,1-2H3,(H,24,25)/t14-,16-,17-/m0/s1") labeled "Enalapril"``

Below is the same molecule again, but represented with an InChIKey:

``a(INCHIKEY:"GBXSMTUPTTWBMN-XIRDDKMYSA-N") labeled "Enalapril"``

It's also easy to use the universe of RESTFul API services from UniChem, ChEMBL, or WikiData to download and annotate
these automatically. For futher information on Enalapril can be found `WikiData <https://www.wikidata.org/wiki/Q422185>`_,
`UniChem <https://www.ebi.ac.uk/unichem/frontpage/results?queryText=GBXSMTUPTTWBMN-XIRDDKMYSA-N&kind=InChIKey&sources=&incl=exclude>`_,
and `ChEMBL <https://www.ebi.ac.uk/chembldb/compound/inspect/CHEMBL578>`_.

Things to Consider
------------------
Do All Statements Need Supporting Text?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yes! All statements must be minimally qualified with a citation and evidence (now called SupportingText in BEL 2.0) to
maintain provenance. Statements without evidence can't be traced to their source or evaluated independently from the
curator, so they are excluded.

Multiple Annotations
~~~~~~~~~~~~~~~~~~~~
When an annotation has a list, it means that the following BEL relations are true for each of the listed values.
The lines below show a BEL relation that corresponds to two edges, each with the same citation but different values
for :code:`ExampleAnnotation`. This should be considered carefully for analyses dealing with the number of edges
between two entities.

.. code::

    SET Citation = {"PubMed","Example Article","12345"}
    SET ExampleAnnotation = {"Example Value 1", "Example Value 2"}
    p(HGNC:YFG1) -> p(HGNC:YFG2)

Furthermore, if there are multiple annotations with lists, the following BEL relations are true for all of the
different combinations of them. The following statements will produce four edges, as the cartesian product of the values
used for both :code:`ExampleAnnotation1` and :code:`ExampleAnnotation2`. This might not be the knowledge that the
annotator wants to express, and is prone to mistakes, so use of annotation lists are not recommended.

.. code::

    SET Citation = {"PubMed","Example Article","12345"}
    SET ExampleAnnotation1 = {"Example Value 11", "Example Value 12"}
    SET ExampleAnnotation2 = {"Example Value 21", "Example Value 22"}
    p(HGNC:YFG1) -> p(HGNC:YFG2)

Namespace and Annotation Name Choices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:code:`*.belns` and :code:`*.belanno` configuration files include an entry called "Keyword" in their respective
[Namespace] and [AnnotationDefinition] sections. To maintain understandability between BEL documents, PyBEL
warns when the names given in :code:`*.bel` documents do not match their respective resources. For now, capitalization
is not considered, but in the future, PyBEL will also warn when capitalization is not properly stylized, like forgetting
the lowercase 'h' in "ChEMBL".

Why Not Nested Statements?
~~~~~~~~~~~~~~~~~~~~~~~~~~
BEL has different relationships for modeling direct and indirect causal relations.

Direct
******
- :code:`A => B` means that `A` directly increases `B` through a physical process.
- :code:`A =| B` means that `A` directly decreases `B` through a physical process.

Indirect
********
The relationship between two entities can be coded in BEL, even if the process is not well understood.

- :code:`A -> B` means that `A` indirectly increases `B`. There are hidden elements in `X` that mediate this interaction
  through a pathway direct interactions :code:`A (=> or =|) X_1 (=> or =|) ... X_n (=> or =|) B`, or through an entire
  network.

- :code:`A -| B` means that `A` indirectly decreases `B`. Like for :code:`A -> B`, this process involves hidden
  components with varying activities.

Increasing Nested Relationships
*******************************
BEL also allows object of a relationship to be another statement.

- :code:`A => (B => C)` means that `A` increases the process by which `B` increases `C`. The example in the BEL Spec
  :code:`p(HGNC:GATA1) => (act(p(HGNC:ZBTB16)) => r(HGNC:MPL))` represents GATA1 directly increasing the process by
  which ZBTB16 directly increases MPL. Before, we were using directly increasing to specify physical contact, so it's
  reasonable to conclude that  :code:`p(HGNC:GATA1) => act(p(HGNC:ZBTB16))`. The specification cites examples when `B`
  is an activity that only is affected in the context of `A` and `C`. This complicated enough that it is both
  impractical to standardize during curation, and impractical to represent in a network.

- :code:`A -> (B => C)` can be interpreted by assuming that `A` indirectly increases `B`, and because of monotonicity,
  conclude that :code:`A -> C` as well.

- :code:`A => (B -> C)` is more difficult to interpret, because it does not describe which part of process
  :code:`B -> C` is affected by `A` or how. Is it that :code:`A => B`, and :code:`B => C`, so we conclude
  :code:`A -> C`, or does it mean something else? Perhaps `A` impacts a different portion of the hidden process in
  :code:`B -> C`. These statements are ambiguous enough that they should be written as just :code:`A => B`, and
  :code:`B -> C`. If there is no literature evidence for the statement :code:`A -> C`, then it is not the job of the
  curator to make this inference. Identifying statements of this might be the goal of a bioinformatics analysis of the
  BEL network after compilation.

- :code:`A -> (B -> C)` introduces even more ambiguity, and it should not be used.

- :code:`A => (B =| C)` states `A` increases the process by which `B` decreases `C`. One interpretation of this
  statement might be that :code:`A => B` and :code:`B =| C`. An analysis could infer :code:`A -| C`.  Statements in the
  form of :code:`A -> (B =| C)` can also be resolved this way, but with added ambiguity.

Decreasing Nested Relationships
*******************************
While we could agree on usage for the previous examples, the decrease of a nested statement introduces an unreasonable
amount of ambiguity.

- :code:`A =| (B => C)` could mean `A` decreases `B`, and `B` also increases `C`. Does this mean A decreases C, or does
  it mean that C is still increased, but just not as much? Which of these statements takes precedence? Or do their
  effects cancel? The same can be said about :code:`A -| (B => C)`, and with added ambiguity for indirect increases
  :code:`A -| (B -> C)`

- :code:`A =| (B =| C)` could mean that `A` decreases `B` and `B` decreases `C`. We could conclude that `A` increases
  `C`, or could we again run into the problem of not knowing the precedence? The same is true for the indirect versions.

Recommendations for Use in PyBEL
********************************
We considered the ambiguity of nested statements to be too great of a risk to include their usage in the PyBEL compiler.
In our group at Fraunhofer SCAI, curators resolved these statements to single statements to improve the precision and
readability of our BEL documents.

While most statements in the form :code:`A rel1 (B rel2 C)` can be reasonably expanded to :code:`A rel1 B` and
:code:`B rel2 C`, the few that cannot are the difficult-to-interpret cases that we need to be careful about in our
curation and later analyses.

Why Not RDF?
~~~~~~~~~~~~
Current bel2rdf serialization tools build URLs with the OpenBEL Framework domain as a namespace, rather than respect
the original namespaces of original entities. This does not follow the best
practices of the semantic web, where URL’s representing an object point to a real page with additional information.
For example, UniProt Knowledge Base does an exemplary job of this. Ultimately, using non-standard URL’s makes
harmonizing and data integration difficult.

Additionally, the RDF format does not easily allow for the annotation of edges. A simple statement in BEL that one
protein up-regulates another can be easily represented in a triple in RDF, but when the annotations and citation from
the BEL document need to be included, this forces RDF serialization to use approaches like representing the statement
itself as a node. RDF was not intended to represent this type of information, but more properly for locating resources
(hence its name). Furthermore, many blank nodes are introduced throughout the process. This makes RDF incredibly
difficult to understand or work with. Later, writing queries in SPARQL becomes very difficult because the data format
is complicated and the language is limited. For example, it would be incredibly complicated to write a query in SPARQL
to get the objects of statements from publications by a certain author.
