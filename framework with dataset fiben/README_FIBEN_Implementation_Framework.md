# FIBEN Implementation Framework — Execution Guide

This README documents the adaptation of the methodology previously tested on IMDb to the FIBEN dataset.

The goal is to reuse the generic methodology pipeline as much as possible, while replacing only the dataset-specific layer:

1. dataset registration in DuckDB;
2. conceptual views;
3. conceptual schema;
4. workload definition;
5. observed cardinality and sharedness extraction;
6. MongoDB materialization logic;
7. concrete benchmark queries.

The methodology computes:

- selected root;
- Rc;
- D;
- Re;
- DeltaR;
- DeltaRratio;
- semantic relationship profile;
- update volatility;
- observed sharedness.

The activation logic uses the generic G0–G9 configuration families.

The benchmark compares:

- primary queries;
- secondary affected queries;
- control queries.

## Execution log

This README is updated directly from the Jupyter notebook.

Created at: 2026-04-30T07:05:41





<!-- START: BLOCK 2 — Register FIBEN Scale-Factor CSVs in DuckDB -->
## BLOCK 2 — Register FIBEN Scale-Factor CSVs in DuckDB

This block registers the final materialized FIBEN CSV files as raw DuckDB views.

Selected scale factor:

    SF1

Selected folder:

    /home/jovyan/privado/fiben/fiben_sf_artifacts/sf1_materialized/tables

Persistent DuckDB file:

    /home/jovyan/privado/framework evaluation approachs/framework with dataset fiben/duckdb/fiben_sf1.duckdb

The block creates one raw DuckDB view per CSV file using the prefix:

    fiben_raw_

Number of registered raw CSV files:

    14

Generated reproducibility files:

    variables/block02/fiben_raw_inventory.csv
    variables/block02/fiben_duckdb_bundle_summary.csv
    variables/block02/fiben_duckdb_bundle_metadata.json
    logs/block_2___register_fiben_scale_factor_csvs_in_duckdb_execution_log.json

Important note:

This block only registers raw CSV tables. It does not create conceptual or semantic views yet.
The conceptual FIBEN views are created in BLOCK 3.

_Last updated: 2026-04-30T14:29:59_

<!-- END: BLOCK 2 — Register FIBEN Scale-Factor CSVs in DuckDB -->









<!-- START: BLOCK 3 — Derived Conceptual Views for FIBEN -->
## BLOCK 3 — Derived Conceptual Views for FIBEN

This block creates the first conceptual/semantic view layer for the FIBEN dataset.

The previous block registered final materialized CSV files as raw DuckDB views.
This block maps those raw views to canonical conceptual entity names used by the methodology.

Matched conceptual entities:

    ['corporations', 'reports', 'disclosures', 'securities', 'listed_securities']

Unmatched conceptual entities:

    ['report_elements', 'statement_elements', 'accounts', 'industries', 'classifications']

Created semantic views:

    {'corporations': 'fiben_corporations', 'reports': 'fiben_reports', 'disclosures': 'fiben_disclosures', 'securities': 'fiben_securities', 'listed_securities': 'fiben_listed_securities'}

Generated reproducibility files:

    variables/block03/fiben_raw_column_dictionary.csv
    variables/block03/fiben_conceptual_view_mapping.csv
    variables/block03/fiben_semantic_views_summary.csv
    variables/block03/fiben_semantic_metadata.json

Important note:

The semantic views created in this block are pass-through views.
They currently use SELECT * FROM the matched raw views.

This is intentional. The goal is to stabilize the conceptual layer before defining:
- conceptual relationships;
- query workload;
- selected root per query;
- update targets;
- observed cardinality;
- observed sharedness.

Column renaming and type normalization can be added later if required by the workload or benchmark runner.

_Last updated: 2026-04-30T14:30:07_

<!-- END: BLOCK 3 — Derived Conceptual Views for FIBEN -->


<!-- START: BLOCK 0A — Core Methodology Data Structures -->
## BLOCK 0A — Core Methodology Data Structures

This block defines the dataset-independent Python dataclasses used by the methodology notebook.

Defined classes:

    ScenarioSpec
    FragmentSpec
    RecommendationSpec
    PhysicalDBSpec
    MaterializationPlan
    BenchmarkQuery
    WorkloadSpec

These structures are reused by the FIBEN scenario block to define:

    conceptual entities;
    conceptual relationships;
    workload queries;
    recommendation fragments;
    physical materialization plan;
    benchmark workload metadata.

This block does not load data and does not create DuckDB views.
It only defines reusable methodology structures.

_Last updated: 2026-04-30T14:40:32_

<!-- END: BLOCK 0A — Core Methodology Data Structures -->


<!-- START: INSTANCE 1 — Real FIBEN Scenario -->
## INSTANCE 1 — Real FIBEN Scenario

This block defines the real FIBEN conceptual scenario and workload.

The scenario replaces the previous IMDb scenario while preserving compatibility
with the generic downstream methodology blocks.

Conceptual scenario name:

    FIBEN_Q1_Q10

Number of conceptual entities:

    15

Number of conceptual relationships:

    15

Number of workload queries:

    10

Important modeling decision:

    The term "company" in the natural-language workload is represented as
    "Corporation" in the conceptual schema.

Workload queries:

    Q1  - Show the profile of company IBM.
    Q2  - Show IBM with its industry, country, and listed securities.
    Q3  - Show the securities held in each financial service account.
    Q4  - Show the companies reached from a person through account, holding, and listed security.
    Q5  - Show the financial reports of a company and the metric data contained in each report.
    Q6  - Find listed securities of technology companies in the US with high last traded value.
    Q7  - Who bought more IBM stocks than they sold?
    Q8  - Show me each transaction for IBM whose price is less than the average selling price.
    Q9  - Show me everyone who bought and sold the same stock.
    Q10 - Create a financial service account for a person, add a holding for a listed security, and register a buy transaction with price and quantity.

Generated reproducibility files:

    variables/instance01/fiben_conceptual_entities.csv
    variables/instance01/fiben_conceptual_relationships.csv
    variables/instance01/fiben_workload_core.csv
    variables/instance01/fiben_workload_benchmark.csv
    variables/instance01/fiben_query_class_summary.csv
    variables/instance01/fiben_scenario_metadata.json

Compatibility aliases created for downstream blocks:

    imdb_scenario = fiben_scenario
    imdb_workload_mongo = fiben_workload_mongo
    hubara_imdb_recommendation = hubara_fiben_recommendation
    hubara_imdb_mongo_materialization = hubara_fiben_mongo_materialization

These aliases are temporary and allow the generic methodology blocks V0–V22D
to run without being rewritten immediately.

_Last updated: 2026-04-30T14:41:05_

<!-- END: INSTANCE 1 — Real FIBEN Scenario -->


<!-- START: BLOCK V0 — Prepare the Conceptual Workload -->
## BLOCK V0 — Prepare the Conceptual Workload

This block prepares the conceptual workload used by the FIBEN methodology execution.

The source scenario is:

    FIBEN_Q1_Q10

The block converts the workload queries into the DataFrame:

    workload_conceptual_df

This DataFrame is required by the downstream methodology blocks.

Number of workload queries:

    10

Number of unique touched entities:

    15

Main variable created:

    workload_conceptual_df

Additional variables created:

    workload_entity_incidence_df
    workload_summary_by_generic_class_df
    workload_summary_by_query_type_df

Generated reproducibility files:

    variables/block_v00/workload_conceptual.csv
    variables/block_v00/workload_entity_incidence.csv
    variables/block_v00/workload_summary_by_generic_class.csv
    variables/block_v00/workload_summary_by_query_type.csv
    variables/block_v00/workload_conceptual_metadata.json

Methodological meaning:

    This block computes R(Qi) as n_entities_touched.
    R(Qi) represents how many conceptual entities are touched by each query.

Important note:

    The variable name workload_conceptual_df is preserved because later generic
    blocks depend on it.

_Last updated: 2026-04-30T14:45:02_

<!-- END: BLOCK V0 — Prepare the Conceptual Workload -->


<!-- START: BLOCK V1 — Organize the Conceptual Relationships -->
## BLOCK V1 — Organize the Conceptual Relationships

This block organizes the conceptual relationships of the FIBEN scenario.

The source scenario is:

    FIBEN_Q1_Q10

Main variables created:

    conceptual_relationships_df
    conceptual_edges
    conceptual_adj

Additional variables created:

    conceptual_bidirectional_edges_df
    conceptual_adjacency_df
    conceptual_relationship_summary_df
    conceptual_entity_degree_df

Number of conceptual relationships:

    15

Number of bidirectional graph edges:

    30

Number of entities in the conceptual graph:

    15

Semantic relationship types:

    ['association', 'containment', 'descriptor', 'ownership', 'subtype']

Generated reproducibility files:

    variables/block_v01/conceptual_relationships.csv
    variables/block_v01/conceptual_bidirectional_edges.csv
    variables/block_v01/conceptual_adjacency.csv
    variables/block_v01/conceptual_relationship_summary.csv
    variables/block_v01/conceptual_entity_degree.csv
    variables/block_v01/conceptual_relationships_metadata.json

Methodological meaning:

    The conceptual relationships define the graph used to compute connectivity
    and conceptual distance between entities.

    Although the conceptual model stores source and target directions, the
    methodology treats the graph as undirected for distance calculations.

Why this is important:

    Later blocks use conceptual_adj and conceptual_edges to compute:
    - root candidates;
    - D(E, er, Qi);
    - Re(Qi, er, D);
    - DeltaR;
    - DeltaRratio.

_Last updated: 2026-04-30T14:49:11_

<!-- END: BLOCK V1 — Organize the Conceptual Relationships -->


<!-- START: BLOCK V2 — Extract Rc(Qi) Exactly -->
## BLOCK V2 — Extract Rc(Qi) Exactly

This block computes Rc(Qi) for each FIBEN workload query.

Rc(Qi) is the minimum number of conceptual relationships required to connect
all conceptual entities touched by a query.

Main variable created:

    rc_df

Additional variables created:

    rc_selected_edges_long_df
    rc_summary_df
    rc_disconnected_queries_df

Number of queries processed:

    10

Number of queries with Rc = 0:

    1

Number of queries with missing Rc:

    0

Maximum Rc value:

    6

Generated reproducibility files:

    variables/block_v02/rc_by_query.csv
    variables/block_v02/rc_selected_edges_long.csv
    variables/block_v02/rc_summary_by_generic_class.csv
    variables/block_v02/rc_disconnected_queries.csv
    variables/block_v02/rc_metadata.json

Methodological meaning:

    Rc(Qi) represents the original conceptual relationship cost of each query
    before selecting a document root and embedding depth.

    Later blocks compare Rc(Qi) with the number of relationships that remain
    outside the selected document configuration. This comparison is used to
    compute DeltaR and DeltaRratio.

Important note:

    Single-entity queries have Rc = 0 because no relationship traversal is
    required to connect their touched entities.

_Last updated: 2026-04-30T14:51:47_

<!-- END: BLOCK V2 — Extract Rc(Qi) Exactly -->


<!-- START: BLOCK V3 — Initial Root Candidates er -->
## BLOCK V3 — Initial Root Candidates er

This block defines the initial candidate document roots er for each FIBEN workload query.

Main variable created:

    root_candidates_df

Additional variables created:

    root_candidates_by_query
    root_candidate_summary_df
    root_candidate_entity_frequency_df

Number of queries processed:

    10

Number of root candidate rows:

    46

Unique candidate roots:

    ['BuyTransaction', 'Corporation', 'Country', 'Disclosure', 'FinancialReport', 'FinancialServiceAccount', 'Holding', 'Industry', 'ListedSecurity', 'Person', 'ReportElement', 'Security', 'SellTransaction', 'StatementElement', 'Transaction']

Generated reproducibility files:

    variables/block_v03/root_candidates.csv
    variables/block_v03/root_candidate_summary.csv
    variables/block_v03/root_candidate_entity_frequency.csv
    variables/block_v03/root_candidates_metadata.json

Methodological meaning:

    er represents a candidate document root entity for a query.

    In this first candidate generation step, every entity explicitly touched
    by a query is considered a possible document root.

Why this is important:

    The next block selects one root per query. Later blocks compute the
    conceptual distance D(E, er, Qi) from each selected root to the other
    entities touched by the query.

_Last updated: 2026-04-30T14:54:32_

<!-- END: BLOCK V3 — Initial Root Candidates er -->


<!-- START: BLOCK V4 — Define the Root Chosen by Query -->
## BLOCK V4 — Define the Root Chosen by Query

This block selects one document root entity for each FIBEN workload query.

Main variable created:

    selected_root_df

Compatibility variables created:

    selected_root_by_query
    root_chosen_by_query
    root_selection_df
    chosen_roots_df

Number of queries processed:

    10

Unique selected roots:

    ['Corporation', 'FinancialServiceAccount', 'ListedSecurity', 'Person', 'Transaction']

Number of invalid selected roots:

    0

Generated reproducibility files:

    variables/block_v04/selected_root_by_query.csv
    variables/block_v04/selected_root_summary.csv
    variables/block_v04/selected_root_by_generic_class.csv
    variables/block_v04/invalid_selected_roots.csv
    variables/block_v04/selected_root_metadata.json

Selected root decisions:

    Q1  -> Corporation
    Q2  -> Corporation
    Q3  -> FinancialServiceAccount
    Q4  -> Person
    Q5  -> Corporation
    Q6  -> ListedSecurity
    Q7  -> Person
    Q8  -> Transaction
    Q9  -> Person
    Q10 -> Person

Methodological meaning:

    The selected root is the document root candidate used to calculate
    conceptual distances from the root to all entities touched by each query.

    The next block computes D(E, er, Qi), where er is the selected root.

_Last updated: 2026-04-30T14:59:49_

<!-- END: BLOCK V4 — Define the Root Chosen by Query -->


<!-- START: BLOCK V5 — Calculate D(E, er, Qi) -->
## BLOCK V5 — Calculate D(E, er, Qi)

This block computes D(E, er, Qi), the conceptual distance between the selected
root er and each entity E touched by query Qi.

Main variables created:

    distance_df
    d_df

Additional variables created:

    distance_summary_by_query_df
    distance_by_depth_df
    distance_unreachable_entities_df

Number of query/entity pairs:

    46

Number of queries processed:

    10

Maximum conceptual distance:

    4

Number of unreachable query/entity pairs:

    0

Generated reproducibility files:

    variables/block_v05/distance_by_query_entity.csv
    variables/block_v05/d_df.csv
    variables/block_v05/distance_summary_by_query.csv
    variables/block_v05/distance_by_depth.csv
    variables/block_v05/distance_unreachable_entities.csv
    variables/block_v05/distance_metadata.json

Methodological meaning:

    D(E, er, Qi) measures how far each touched entity is from the selected
    document root in the conceptual graph.

    This value is later used to estimate which entities can be reached by
    a document configuration with a given embedding depth.

Example:

    If selected_root = Corporation, then:
    D(Corporation, Corporation, Qi) = 0
    D(FinancialReport, Corporation, Qi) = 1
    D(ReportElement, Corporation, Qi) = 2

_Last updated: 2026-04-30T15:01:37_

<!-- END: BLOCK V5 — Calculate D(E, er, Qi) -->


<!-- START: BLOCK V6 — Observed Cardinality Light Version -->
## BLOCK V6 — Observed Cardinality Light Version

This block computes a lightweight observed cardinality profile for the FIBEN
conceptual relationships.

Main variables created:

    observed_cardinality_df
    relationship_cardinality_df
    cardinality_observed_df

Additional variables created:

    fiben_entity_view_mapping_df
    candidate_join_columns_df
    observed_cardinality_summary_df
    uncomputed_cardinality_df

Number of conceptual relationships processed:

    15

Number of computed relationships:

    2

Number of uncomputed relationships:

    13

Row limit used per table:

    200000

Generated reproducibility files:

    variables/block_v06/fiben_entity_view_mapping.csv
    variables/block_v06/candidate_join_columns.csv
    variables/block_v06/observed_cardinality_by_relationship.csv
    variables/block_v06/observed_cardinality_summary.csv
    variables/block_v06/uncomputed_cardinality_relationships.csv
    variables/block_v06/observed_cardinality_metadata.json

Methodological meaning:

    This block estimates the observed cardinality pattern of each conceptual
    relationship using the physical FIBEN data available in DuckDB.

    The result is used as supporting evidence for later semantic and structural
    interpretation of document configurations.

Important limitation:

    This is a light version. It infers join columns automatically and may not
    compute every relationship if physical key names are ambiguous.

    Relationships marked as not_computed should be reviewed manually before
    running the final benchmark stage.

_Last updated: 2026-04-30T15:05:38_

<!-- END: BLOCK V6 — Observed Cardinality Light Version -->


<!-- START: BLOCK V6A — Inspect FIBEN Physical Mapping and Join Keys -->
## BLOCK V6A — Inspect FIBEN Physical Mapping and Join Keys

This diagnostic block inspects the physical FIBEN mapping before refining
the observed cardinality computation.

Main variables created:

    fiben_physical_view_inventory_df
    fiben_physical_column_dictionary_df
    fiben_likely_key_columns_df
    fiben_entity_mapping_diagnostic_df
    relationships_need_review_df

Number of physical views inspected:

    19

Number of likely key columns found:

    34

Number of relationships needing manual review:

    13

Generated reproducibility files:

    variables/block_v06a/fiben_physical_view_inventory.csv
    variables/block_v06a/fiben_physical_column_dictionary.csv
    variables/block_v06a/fiben_likely_key_columns.csv
    variables/block_v06a/fiben_entity_mapping_diagnostic.csv
    variables/block_v06a/relationships_need_manual_review.csv
    variables/block_v06a/fiben_physical_mapping_diagnostic_metadata.json

Methodological meaning:

    This block does not change the conceptual methodology.
    It helps connect the conceptual FIBEN model to the physical CSV tables
    and columns used by DuckDB.

Why this is necessary:

    Some conceptual entities may not have a direct physical table.
    Some relationships require explicit join-column hints because automatic
    inference is not always reliable.

_Last updated: 2026-04-30T15:09:51_

<!-- END: BLOCK V6A — Inspect FIBEN Physical Mapping and Join Keys -->


<!-- START: BLOCK V6B — Manual FIBEN Entity View Overrides -->
## BLOCK V6B — Manual FIBEN Entity View Overrides

This block creates manual entity-to-view overrides for the FIBEN physical mapping.

The diagnostic BLOCK V6A showed that some conceptual entities were not mapped
automatically because the physical FIBEN table names differ from the conceptual
entity names.

Main variable created:

    FIBEN_ENTITY_VIEW_OVERRIDES

Additional variables created:

    FIBEN_SEMANTIC_VIEW_SPECS
    fiben_semantic_view_creation_df
    fiben_entity_view_override_validation_df
    fiben_entity_override_columns_df

Number of entity overrides:

    15

Number of valid entity overrides:

    15

Generated reproducibility files:

    variables/block_v06b/fiben_semantic_view_creation.csv
    variables/block_v06b/fiben_entity_view_override_validation.csv
    variables/block_v06b/fiben_entity_override_columns.csv
    variables/block_v06b/fiben_entity_view_overrides_metadata.json

Important modeling note:

    BuyTransaction and SellTransaction are currently semantic aliases over
    the SecuritiesTransaction physical table.

    If a transaction-type discriminator column is identified later, these
    views should be refined with WHERE filters.

Why this block is necessary:

    The observed cardinality block needs a reliable mapping from conceptual
    entities to physical DuckDB views before computing join statistics.

_Last updated: 2026-04-30T15:13:30_

<!-- END: BLOCK V6B — Manual FIBEN Entity View Overrides -->


<!-- START: BLOCK V6C — Manual FIBEN Relationship Join Hints -->
## BLOCK V6C — Manual FIBEN Relationship Join Hints

This block defines manual join hints for the FIBEN conceptual relationships.

Main variable created:

    FIBEN_MANUAL_RELATIONSHIP_JOIN_HINTS

Additional variables created:

    fiben_relationship_join_hints_df
    invalid_join_hints_df

Number of manual join hints:

    15

Number of invalid join hints:

    0

Generated reproducibility files:

    variables/block_v06c/fiben_relationship_join_hints.csv
    variables/block_v06c/invalid_relationship_join_hints.csv
    variables/block_v06c/fiben_relationship_join_hints_metadata.json

Important notes:

    Most joins are direct foreign-key-like relationships.

    The relationship corporation_has_listed_security is treated as a bridge
    relationship through Security:

        Corporation -> Security -> ListedSecurity

    BuyTransaction and SellTransaction are currently modeled as subtype aliases
    over the SecuritiesTransaction physical table.

    Some low-confidence hints still need empirical validation through observed
    join matches.

_Last updated: 2026-04-30T15:19:51_

<!-- END: BLOCK V6C — Manual FIBEN Relationship Join Hints -->


<!-- START: BLOCK V6 — Observed Cardinality with Manual FIBEN Join Hints -->
## BLOCK V6 — Observed Cardinality with Manual FIBEN Join Hints

This block computes the observed cardinality profile for the FIBEN conceptual
relationships using manual entity/view overrides and manual join hints.

Main variables created:

    observed_cardinality_df
    relationship_cardinality_df
    cardinality_observed_df

Additional variables created:

    observed_cardinality_summary_df
    uncomputed_cardinality_df
    low_confidence_cardinality_df
    no_match_cardinality_df

Number of conceptual relationships processed:

    15

Number of computed relationships:

    15

Number of uncomputed relationships:

    0

Number of low or medium confidence relationships:

    6

Number of computed relationships with no observed matches:

    4

Row limit used per table:

    200000

Generated reproducibility files:

    variables/block_v06/observed_cardinality_by_relationship.csv
    variables/block_v06/relationship_cardinality.csv
    variables/block_v06/cardinality_observed.csv
    variables/block_v06/observed_cardinality_summary.csv
    variables/block_v06/uncomputed_cardinality_relationships.csv
    variables/block_v06/low_confidence_cardinality_relationships.csv
    variables/block_v06/no_match_cardinality_relationships.csv
    variables/block_v06/observed_cardinality_metadata.json

Methodological meaning:

    This block estimates the observed cardinality pattern of each conceptual
    relationship using the physical FIBEN data available in DuckDB.

Important notes:

    The relationship corporation_has_listed_security is computed as a bridge
    relationship through Security.

    BuyTransaction and SellTransaction are currently subtype aliases over the
    SecuritiesTransaction table.

    Low-confidence and no-match relationships should be reviewed before the
    final benchmark execution.

_Last updated: 2026-04-30T15:26:05_

<!-- END: BLOCK V6 — Observed Cardinality with Manual FIBEN Join Hints -->


<!-- START: BLOCK V7 — Semantic Classification of Relationships -->
## BLOCK V7 — Semantic Classification of Relationships

This block consolidates the semantic classification of the FIBEN conceptual
relationships.

Main variables created:

    relationship_semantics_df
    semantic_relationships_df
    relationship_semantic_profile_df

Additional variables created:

    semantic_type_summary_df
    semantic_cardinality_summary_df
    edge_semantic_type_by_edge_id
    edge_semantic_type_by_relationship_name
    missing_semantic_type_df
    missing_cardinality_merge_df

Number of relationships processed:

    15

Semantic relationship types:

    ['association', 'containment', 'descriptor', 'ownership', 'subtype']

Number of relationships with missing semantic type:

    0

Number of relationships without cardinality merge:

    0

Generated reproducibility files:

    variables/block_v07/relationship_semantics.csv
    variables/block_v07/semantic_relationships.csv
    variables/block_v07/relationship_semantic_profile.csv
    variables/block_v07/semantic_type_summary.csv
    variables/block_v07/semantic_cardinality_summary.csv
    variables/block_v07/missing_semantic_type_relationships.csv
    variables/block_v07/missing_cardinality_merge_relationships.csv
    variables/block_v07/relationship_semantics_metadata.json

Methodological meaning:

    This block assigns each conceptual relationship to a semantic category.

    These semantic categories are later used to summarize which kinds of
    relationships are touched by each workload query.

Categories used in the FIBEN scenario:

    descriptor
    association
    ownership
    containment
    subtype

_Last updated: 2026-04-30T15:29:10_

<!-- END: BLOCK V7 — Semantic Classification of Relationships -->


<!-- START: BLOCK V8 — Types of Relationships Touched by Each Query -->
## BLOCK V8 — Types of Relationships Touched by Each Query

This block identifies which semantic relationship types are touched by each
FIBEN workload query.

Main variables created:

    relationship_types_by_query_df
    query_relationship_types_df
    query_semantic_profile_df

Additional variables created:

    query_relationship_edges_df
    query_semantic_type_counts_df
    query_semantic_flags_df
    missing_semantic_for_edges_df
    query_without_relationship_edges_df

Number of queries processed:

    10

Known semantic relationship types:

    ['association', 'containment', 'descriptor', 'ownership', 'subtype']

Number of query relationship edges:

    36

Number of queries without relationship edges:

    1

Number of selected edges missing semantic classification:

    0

Generated reproducibility files:

    variables/block_v08/query_relationship_edges.csv
    variables/block_v08/query_semantic_type_counts.csv
    variables/block_v08/query_semantic_profile.csv
    variables/block_v08/query_semantic_flags.csv
    variables/block_v08/relationship_types_by_query.csv
    variables/block_v08/query_relationship_types.csv
    variables/block_v08/missing_semantic_for_edges.csv
    variables/block_v08/query_without_relationship_edges.csv
    variables/block_v08/query_relationship_types_metadata.json

Methodological meaning:

    This block builds the semantic profile of each query by combining the
    relationships selected in Rc(Qi) with the semantic classification of each
    conceptual edge.

    The resulting profile indicates whether a query touches descriptor,
    association, ownership, containment, or subtype relationships.

Important note:

    Queries with Rc = 0, such as local lookup queries over a single entity,
    do not touch relationship edges.

_Last updated: 2026-04-30T15:32:51_

<!-- END: BLOCK V8 — Types of Relationships Touched by Each Query -->


<!-- START: BLOCK V9 — Structural Analysis of Edges by Depth -->
## BLOCK V9 — Structural Analysis of Edges by Depth

This block analyzes structural edges by depth from the selected root of each
FIBEN workload query.

Main variables created:

    edge_depth_df
    structural_edges_by_depth_df
    query_edge_depth_profile_df

Additional variables created:

    query_edges_with_semantics_df
    query_depth_summary_df
    entity_depth_summary_df
    max_depth_by_query_df
    edges_missing_semantics_df
    queries_with_no_edges_df

Number of expanded edge-depth rows:

    75

Number of unique structural query-edge rows:

    38

Number of queries processed:

    10

Maximum entity depth observed:

    4

Maximum edge depth observed:

    4

Number of queries with no edges:

    1

Generated reproducibility files:

    variables/block_v09/edge_depth.csv
    variables/block_v09/query_edges_with_semantics.csv
    variables/block_v09/structural_edges_by_depth.csv
    variables/block_v09/query_depth_summary.csv
    variables/block_v09/entity_depth_summary.csv
    variables/block_v09/query_edge_depth_profile.csv
    variables/block_v09/max_depth_by_query.csv
    variables/block_v09/edges_missing_semantics.csv
    variables/block_v09/queries_with_no_edges.csv
    variables/block_v09/structural_edges_by_depth_metadata.json

Methodological meaning:

    This block identifies the depth at which each conceptual relationship
    appears from the selected root of a query.

    This structural depth information is required to compute which entities
    and relationships are reachable under a document embedding depth.

Important note:

    Queries with Rc = 0, such as local lookup over a single entity, may have
    no structural edges.

_Last updated: 2026-04-30T15:35:06_

<!-- END: BLOCK V9 — Structural Analysis of Edges by Depth -->


<!-- START: BLOCK V10 — Calculate Re(Qi, er, D) and DeltaR -->
## BLOCK V10 — Calculate Re(Qi, er, D) and DeltaR

This block computes Re(Qi, er, D), DeltaR, and DeltaRratio for the FIBEN
workload.

Main variables created:

    re_df
    delta_r_df
    re_delta_df

Additional variables created:

    best_depth_by_query_df
    re_delta_summary_df
    depth_candidate_matrix_df
    negative_delta_df
    invalid_ratio_df
    queries_without_full_coverage_df

Number of Re/DeltaR rows:

    35

Number of queries processed:

    10

Maximum document depth tested:

    4

Number of negative DeltaR rows:

    2

Number of invalid DeltaRratio rows:

    0

Generated reproducibility files:

    variables/block_v10/re_delta_by_query_depth.csv
    variables/block_v10/re_df.csv
    variables/block_v10/delta_r_df.csv
    variables/block_v10/best_depth_by_query.csv
    variables/block_v10/re_delta_summary_by_class_depth.csv
    variables/block_v10/depth_candidate_matrix.csv
    variables/block_v10/negative_delta_rows.csv
    variables/block_v10/invalid_ratio_rows.csv
    variables/block_v10/queries_without_full_coverage.csv
    variables/block_v10/re_delta_metadata.json

Methodological meaning:

    Rc(Qi) is the original number of conceptual relationships required by a query.

    Re(Qi, er, D) is the number of relationships that remain external after
    choosing root er and embedding entities up to document depth D.

    DeltaR = Rc - Re

    DeltaRratio = DeltaR / Rc

Interpretation:

    Higher DeltaRratio means that a larger portion of the original relational
    traversal can potentially be internalized by the document configuration.

Important note:

    For queries with Rc = 0, DeltaRratio is defined as 0.0 because there are
    no relationship edges to reduce.

_Last updated: 2026-04-30T15:36:55_

<!-- END: BLOCK V10 — Calculate Re(Qi, er, D) and DeltaR -->


<!-- START: BLOCK V11 — Assemble Compact Matrix by Query -->
## BLOCK V11 — Assemble Compact Matrix by Query

This block assembles a compact analytical matrix with one row per FIBEN
workload query.

Main variables created:

    compact_matrix_by_query_df
    compact_query_matrix_df
    query_compact_matrix_df
    compact_analytical_matrix_base_df

Additional variables created:

    query_cardinality_edges_df
    query_cardinality_profile_df
    compact_matrix_missing_root_df
    compact_matrix_missing_rc_df
    compact_matrix_missing_delta_df

Number of queries:

    10

Number of columns in the compact matrix:

    64

Number of queries with relationship reduction potential:

    9

Number of queries with full coverage at best depth:

    10

Number of queries with low-confidence physical mapping:

    1

Number of queries with no-match cardinality edges:

    7

Generated reproducibility files:

    variables/block_v11/compact_matrix_by_query.csv
    variables/block_v11/compact_query_matrix.csv
    variables/block_v11/query_compact_matrix.csv
    variables/block_v11/compact_analytical_matrix_base.csv
    variables/block_v11/query_cardinality_edges.csv
    variables/block_v11/query_cardinality_profile.csv
    variables/block_v11/compact_matrix_missing_root.csv
    variables/block_v11/compact_matrix_missing_rc.csv
    variables/block_v11/compact_matrix_missing_delta.csv
    variables/block_v11/compact_matrix_by_query_metadata.json

Methodological meaning:

    This block consolidates the main query-level methodology variables into
    a compact matrix.

    The matrix integrates:
    - workload metadata;
    - selected root;
    - Rc;
    - D;
    - Re;
    - DeltaR;
    - DeltaRratio;
    - semantic relationship profile;
    - observed cardinality profile.

This compact matrix is the basis for the next analytical matrix blocks.

_Last updated: 2026-04-30T15:40:46_

<!-- END: BLOCK V11 — Assemble Compact Matrix by Query -->


<!-- START: BLOCK V12 — Analytical Matrix of FIBEN Expanded by Depth -->
## BLOCK V12 — Analytical Matrix of FIBEN Expanded by Depth

This block builds the expanded analytical matrix for the FIBEN workload.

Unlike the compact matrix from BLOCK V11, this matrix has one row per:

    query + document_depth

Main variables created:

    analytical_matrix_expanded_by_depth_df
    expanded_analytical_matrix_df
    document_analytical_matrix_expanded_df
    document_variable_matrix_expanded_df

Additional variables created:

    expanded_matrix_summary_by_depth_df
    expanded_matrix_summary_by_query_df
    expanded_matrix_best_depth_rows_df
    expanded_matrix_missing_values_df
    expanded_matrix_negative_delta_df
    expanded_matrix_invalid_best_depth_df

Number of rows:

    35

Number of queries:

    10

Number of columns:

    67

Document depths represented:

    [0, 1, 2, 3, 4]

Number of best-depth rows:

    10

Number of full-coverage rows:

    10

Generated reproducibility files:

    variables/block_v12/analytical_matrix_expanded_by_depth.csv
    variables/block_v12/expanded_analytical_matrix.csv
    variables/block_v12/document_analytical_matrix_expanded.csv
    variables/block_v12/document_variable_matrix_expanded.csv
    variables/block_v12/expanded_matrix_summary_by_depth.csv
    variables/block_v12/expanded_matrix_summary_by_query.csv
    variables/block_v12/expanded_matrix_best_depth_rows.csv
    variables/block_v12/expanded_matrix_missing_values.csv
    variables/block_v12/expanded_matrix_negative_delta.csv
    variables/block_v12/expanded_matrix_invalid_best_depth.csv
    variables/block_v12/analytical_matrix_expanded_metadata.json

Methodological meaning:

    This block shows how the analytical variables change when the document
    embedding depth changes.

    It allows comparing Re, DeltaR, and DeltaRratio across depth values for
    each query.

Why this is important:

    The activation logic later uses these variables to infer which generic
    document configuration families are relevant for each query.

_Last updated: 2026-04-30T15:43:06_

<!-- END: BLOCK V12 — Analytical Matrix of FIBEN Expanded by Depth -->


<!-- START: BLOCK V13 — Compact Analytical Matrix by Query -->
## BLOCK V13 — Compact Analytical Matrix by Query

This block builds the compact analytical matrix for the FIBEN workload.

Unlike BLOCK V12, which has one row per query and document depth, this block
keeps one representative row per query. The selected representative row is
normally the best-depth row.

Main variables created:

    analytical_matrix_compact_by_query_df
    compact_analytical_matrix_df
    document_variable_matrix_df

Additional variables created:

    query_analytical_matrix_df
    document_variable_matrix_base_df
    compact_best_depth_rows_df
    compact_matrix_summary_df
    compact_matrix_by_potential_df
    compact_matrix_by_root_df
    compact_matrix_validation_df

Number of queries:

    10

Number of columns:

    71

Number of failed validation checks:

    0

Generated reproducibility files:

    variables/block_v13/analytical_matrix_compact_by_query.csv
    variables/block_v13/compact_analytical_matrix.csv
    variables/block_v13/query_analytical_matrix.csv
    variables/block_v13/document_variable_matrix.csv
    variables/block_v13/document_variable_matrix_base.csv
    variables/block_v13/compact_best_depth_rows.csv
    variables/block_v13/compact_matrix_summary.csv
    variables/block_v13/compact_matrix_by_potential.csv
    variables/block_v13/compact_matrix_by_root.csv
    variables/block_v13/compact_matrix_validation.csv
    variables/block_v13/analytical_matrix_compact_metadata.json

Methodological meaning:

    This block produces the main compact query-level analytical matrix.

    It keeps the best-depth result per query and preserves the key variables:
    - selected root;
    - document depth;
    - Rc;
    - Re;
    - DeltaR;
    - DeltaRratio;
    - semantic profile;
    - cardinality profile;
    - physical mapping reliability.

Why this is important:

    The next blocks add update-specific variables and sharedness variables
    to document_variable_matrix_df.

_Last updated: 2026-04-30T15:46:38_

<!-- END: BLOCK V13 — Compact Analytical Matrix by Query -->


<!-- START: BLOCK V14 — Entities Explicitly Modified by Query -->
## BLOCK V14 — Entities Explicitly Modified by Query

This block identifies which conceptual entities are explicitly modified by
each FIBEN workload query.

Main variables created:

    explicitly_modified_entities_df
    modified_entities_by_query_df
    query_modified_entities_df

Additional variables created:

    modified_entities_long_df
    relationship_creation_by_query_df
    update_query_summary_df
    modified_entity_frequency_df
    document_variable_matrix_with_modifications_df

Number of queries:

    10

Number of write queries:

    1

Number of read queries:

    9

Write query identified:

    Q10_CreateAccountHoldingAndBuyTransaction

Q10 created entities:

    FinancialServiceAccount
    Holding
    BuyTransaction
    Transaction

Q10 referenced existing entities:

    Person
    ListedSecurity

Q10 affected persistence-region entities:

    Person
    FinancialServiceAccount
    Holding
    ListedSecurity
    BuyTransaction
    Transaction

Generated reproducibility files:

    variables/block_v14/modified_entities_by_query.csv
    variables/block_v14/explicitly_modified_entities.csv
    variables/block_v14/query_modified_entities.csv
    variables/block_v14/modified_entities_long.csv
    variables/block_v14/relationship_creation_by_query.csv
    variables/block_v14/update_query_summary.csv
    variables/block_v14/modified_entity_frequency.csv
    variables/block_v14/document_variable_matrix_with_modifications.csv
    variables/block_v14/modified_entities_metadata.json

Methodological meaning:

    This block prepares the update-specific variables required to compute
    update volatility.

    It separates created entities from referenced existing entities because
    a document design may affect existing document roots even when the
    conceptual entity itself is not newly created.

Important note:

    BuyTransaction is modeled as a conceptual subtype of Transaction.
    Therefore, Q10 includes both BuyTransaction and Transaction as created
    write-related entities.

_Last updated: 2026-04-30T15:51:56_

<!-- END: BLOCK V14 — Entities Explicitly Modified by Query -->


<!-- START: BLOCK V15 — Calculate Update Volatility by Entity -->
## BLOCK V15 — Calculate Update Volatility by Entity

This block calculates update volatility at the conceptual entity level.

Main variables created:

    update_volatility_by_entity_df
    entity_update_volatility_df
    update_volatility_entity_df

Additional variables created:

    update_volatility_events_df
    update_volatility_summary_df
    update_volatility_category_summary_df
    entities_with_update_volatility_df
    entities_without_update_volatility_df

Number of total queries:

    10

Number of write queries:

    1

Number of conceptual entities:

    15

Number of entities with update volatility:

    6

Number of entities without update volatility:

    9

Category weights used:

    created = 1.00
    updated = 1.00
    deleted = 1.00
    relationship_created = 0.60
    affected_persistence_region = 0.40
    referenced_existing = 0.15

Excluded derived categories:

    explicitly_modified
    all_write_related

Generated reproducibility files:

    variables/block_v15/update_volatility_by_entity.csv
    variables/block_v15/entity_update_volatility.csv
    variables/block_v15/update_volatility_entity.csv
    variables/block_v15/update_volatility_events.csv
    variables/block_v15/update_volatility_summary.csv
    variables/block_v15/update_volatility_category_summary.csv
    variables/block_v15/entities_with_update_volatility.csv
    variables/block_v15/entities_without_update_volatility.csv
    variables/block_v15/update_volatility_by_entity_metadata.json

Methodological meaning:

    Update volatility estimates how strongly each conceptual entity is affected
    by write operations in the workload.

    The score is based on weighted modification events and write-query coverage.

Important note:

    In the current FIBEN workload, Q10 is the main write query.
    Therefore, the volatility signal is concentrated around the entities
    affected by Q10: Person, FinancialServiceAccount, Holding, ListedSecurity,
    BuyTransaction, and Transaction.

_Last updated: 2026-04-30T15:52:45_

<!-- END: BLOCK V15 — Calculate Update Volatility by Entity -->


<!-- START: BLOCK V16 — Summarize Update Volatility by Query -->
## BLOCK V16 — Summarize Update Volatility by Query

This block summarizes update volatility at the query level.

The previous block calculated update volatility by conceptual entity.
This block aggregates those entity-level scores for each FIBEN workload query.

Main variables created:

    update_volatility_by_query_df
    query_update_volatility_df
    update_volatility_query_df

Additional variables created:

    query_entity_update_volatility_long_df
    query_write_related_update_volatility_long_df
    update_volatility_query_summary_df
    update_volatility_by_generic_class_df
    missing_query_update_volatility_df
    write_queries_low_or_no_volatility_df
    read_queries_with_volatility_df

Number of queries:

    10

Number of queries with update volatility:

    8

Number of write queries:

    1

Maximum query update volatility score:

    0.932

Generated reproducibility files:

    variables/block_v16/update_volatility_by_query.csv
    variables/block_v16/query_update_volatility.csv
    variables/block_v16/update_volatility_query.csv
    variables/block_v16/query_entity_update_volatility_long.csv
    variables/block_v16/query_write_related_update_volatility_long.csv
    variables/block_v16/update_volatility_query_summary.csv
    variables/block_v16/update_volatility_by_generic_class.csv
    variables/block_v16/missing_query_update_volatility.csv
    variables/block_v16/write_queries_low_or_no_volatility.csv
    variables/block_v16/read_queries_with_volatility.csv
    variables/block_v16/update_volatility_by_query_metadata.json

Methodological meaning:

    Query-level update volatility estimates how sensitive each query is to
    write activity in the entities it touches.

    Read queries may still have non-zero volatility if they read entities that
    are affected by write operations elsewhere in the workload.

    Write queries combine touched-entity volatility and write-related entity
    volatility.

Important note:

    In the current FIBEN workload, Q10 is the only write query, but other
    read queries may still touch volatile entities such as Person,
    FinancialServiceAccount, Holding, ListedSecurity, BuyTransaction, and
    Transaction.

_Last updated: 2026-04-30T15:54:14_

<!-- END: BLOCK V16 — Summarize Update Volatility by Query -->


<!-- START: BLOCK V17 — Integrate Update Volatility into the Analytical Matrix -->
## BLOCK V17 — Integrate Update Volatility into the Analytical Matrix

This block integrates query-level update volatility variables into the main
analytical matrix.

Main variables created or updated:

    document_variable_matrix_df
    document_variable_matrix_with_update_volatility_df
    analytical_matrix_with_update_volatility_df

Additional variables created:

    document_variable_matrix_update_enriched_df
    update_volatility_integration_check_df
    update_volatility_matrix_summary_df
    update_volatility_by_potential_summary_df
    missing_update_volatility_merge_df
    failed_update_integration_checks_df

Rows before merge:

    10

Rows after merge:

    10

Columns after merge:

    109

Queries with update volatility:

    8

Failed integration checks:

    0

Generated reproducibility files:

    variables/block_v17/document_variable_matrix_with_update_volatility.csv
    variables/block_v17/analytical_matrix_with_update_volatility.csv
    variables/block_v17/document_variable_matrix_update_enriched.csv
    variables/block_v17/document_variable_matrix.csv
    variables/block_v17/update_volatility_integration_check.csv
    variables/block_v17/update_volatility_matrix_summary.csv
    variables/block_v17/update_volatility_by_potential_summary.csv
    variables/block_v17/missing_update_volatility_merge.csv
    variables/block_v17/failed_update_integration_checks.csv
    variables/block_v17/update_volatility_integration_metadata.json

Methodological meaning:

    This block enriches the analytical matrix with update-volatility variables.

    These variables help identify whether a candidate document configuration
    may produce a read-performance benefit while also increasing update
    maintenance pressure.

Important interpretation:

    A query with high DeltaRratio and high update volatility may be a strong
    read-optimization candidate, but it may also require careful benchmark
    evaluation for update cost.

_Last updated: 2026-04-30T15:55:36_

<!-- END: BLOCK V17 — Integrate Update Volatility into the Analytical Matrix -->


<!-- START: BLOCK V18 — Extract Sharedness Observed in the FIBEN Dataset -->
## BLOCK V18 — Extract Sharedness Observed in the FIBEN Dataset

This block extracts observed sharedness from the physical FIBEN dataset.

Sharedness measures how often a target entity is shared by multiple source
entities.

Main variables created:

    observed_sharedness_df
    relationship_sharedness_df
    sharedness_observed_df

Additional variables created:

    query_edge_sharedness_df
    query_sharedness_profile_df
    sharedness_summary_df
    query_sharedness_summary_df
    sharedness_not_computed_df
    high_sharedness_relationships_df

Number of relationships processed:

    15

Number of computed relationships:

    15

Number of relationships not computed:

    0

Number of high-sharedness relationships:

    0

Number of queries with observed sharedness:

    9

Row limit used per table:

    200000

Generated reproducibility files:

    variables/block_v18/observed_sharedness_by_relationship.csv
    variables/block_v18/relationship_sharedness.csv
    variables/block_v18/sharedness_observed.csv
    variables/block_v18/query_edge_sharedness.csv
    variables/block_v18/query_sharedness_profile.csv
    variables/block_v18/sharedness_summary.csv
    variables/block_v18/query_sharedness_summary.csv
    variables/block_v18/sharedness_not_computed.csv
    variables/block_v18/high_sharedness_relationships.csv
    variables/block_v18/observed_sharedness_metadata.json

Methodological meaning:

    Observed sharedness helps identify relationships where the target entity is
    reused by multiple source entities.

    This matters for document design because embedding highly shared entities
    can increase duplication and update-maintenance cost.

Examples in FIBEN:

    Many Corporations may share the same Country.
    Many Corporations may share the same Industry.
    Many Holdings may refer to the same ListedSecurity.

_Last updated: 2026-04-30T15:57:45_

<!-- END: BLOCK V18 — Extract Sharedness Observed in the FIBEN Dataset -->


<!-- START: BLOCK V19 — Integrate Observed Sharedness into the Analytical Matrix -->
## BLOCK V19 — Integrate Observed Sharedness into the Analytical Matrix

This block integrates observed sharedness variables into the main analytical
matrix.

Main variables created or updated:

    document_variable_matrix_df
    document_variable_matrix_with_sharedness_df
    analytical_matrix_with_sharedness_df

Additional variables created:

    document_variable_matrix_sharedness_enriched_df
    sharedness_integration_check_df
    sharedness_matrix_summary_df
    sharedness_tradeoff_summary_df
    sharedness_by_root_summary_df
    missing_sharedness_merge_df
    failed_sharedness_integration_checks_df
    high_read_gain_high_sharedness_df

Rows before merge:

    10

Rows after merge:

    10

Columns after merge:

    122

Queries with observed sharedness:

    9

Failed integration checks:

    0

Generated reproducibility files:

    variables/block_v19/document_variable_matrix_with_sharedness.csv
    variables/block_v19/analytical_matrix_with_sharedness.csv
    variables/block_v19/document_variable_matrix_sharedness_enriched.csv
    variables/block_v19/document_variable_matrix.csv
    variables/block_v19/sharedness_integration_check.csv
    variables/block_v19/sharedness_matrix_summary.csv
    variables/block_v19/sharedness_tradeoff_summary.csv
    variables/block_v19/sharedness_by_root_summary.csv
    variables/block_v19/missing_sharedness_merge.csv
    variables/block_v19/failed_sharedness_integration_checks.csv
    variables/block_v19/high_read_gain_high_sharedness_queries.csv
    variables/block_v19/sharedness_integration_metadata.json

Methodological meaning:

    Observed sharedness helps identify possible duplication pressure in
    document configurations.

    If a target entity is shared by many source entities, embedding that
    target inside many documents may duplicate data.

Important interpretation:

    A query with high DeltaRratio and high sharedness may still be a good
    read-optimization candidate, but it requires careful benchmark evaluation
    because of possible duplication and update-maintenance cost.

_Last updated: 2026-04-30T15:59:00_

<!-- END: BLOCK V19 — Integrate Observed Sharedness into the Analytical Matrix -->


<!-- START: BLOCK V20 — Final Document Variable Matrix for Activation -->
## BLOCK V20 — Final Document Variable Matrix for Activation

This block consolidates the final document variable matrix used as input for
the generic activation logic G0–G9.

Main variables created:

    final_document_variable_matrix_df
    document_variable_matrix_for_activation_df
    activation_input_matrix_df

Additional variables created:

    activation_feature_matrix_df
    activation_numeric_features_df
    activation_boolean_features_df
    activation_matrix_summary_df
    activation_by_generic_class_df
    activation_read_update_sharedness_summary_df
    activation_validation_df

Number of queries:

    10

Number of columns in the final matrix:

    138

Number of columns in the activation input matrix:

    62

Number of numeric activation features:

    24

Number of boolean activation features:

    21

Failed activation validation checks:

    0

Generated reproducibility files:

    variables/block_v20/final_document_variable_matrix.csv
    variables/block_v20/document_variable_matrix.csv
    variables/block_v20/document_variable_matrix_for_activation.csv
    variables/block_v20/activation_input_matrix.csv
    variables/block_v20/activation_feature_matrix.csv
    variables/block_v20/activation_numeric_features.csv
    variables/block_v20/activation_boolean_features.csv
    variables/block_v20/activation_matrix_summary.csv
    variables/block_v20/activation_by_generic_class.csv
    variables/block_v20/activation_read_update_sharedness_summary.csv
    variables/block_v20/activation_validation.csv
    variables/block_v20/final_document_variable_matrix_metadata.json

Methodological meaning:

    This block prepares the final activation-ready matrix.

    It consolidates:
    - Rc;
    - Re;
    - DeltaR;
    - DeltaRratio;
    - selected root;
    - document depth;
    - semantic relationship profile;
    - update volatility;
    - observed sharedness;
    - document design risk classes.

Important note:

    This block does not activate G0–G9 yet.
    It only prepares the stable input matrix for the activation logic.

_Last updated: 2026-04-30T16:00:59_

<!-- END: BLOCK V20 — Final Document Variable Matrix for Activation -->


<!-- START: BLOCK V21 — Apply Generic Activation Logic G0-G9 -->
## BLOCK V21 — Apply Generic Activation Logic G0-G9

This block applies the generic activation logic G0-G9 over the final document
variable matrix.

Main variables created:

    g_class_activation_by_query_df
    generic_activation_by_query_df
    activation_g0_g9_df

Additional variables created:

    g_class_activation_long_df
    g_class_activation_summary_df
    primary_activation_summary_df
    activation_by_generic_class_summary_df
    document_variable_matrix_with_activation_df
    activation_logic_validation_df

Number of queries:

    10

Number of activation rows:

    100

Number of queries without activation:

    0

Failed activation validation checks:

    0

Generic activation classes:

    G0 - Root-only document
    G1 - Root with direct descriptors
    G2 - Root with contained children
    G3 - Root with associated references
    G4 - Deep nested traversal document
    G5 - Shared target reference strategy
    G6 - Aggregation-oriented document
    G7 - Update-aware document strategy
    G8 - Hybrid embedded-reference strategy
    G9 - Benchmark-required trade-off candidate

Generated reproducibility files:

    variables/block_v21/g_class_rule_catalog.csv
    variables/block_v21/g_class_activation_by_query.csv
    variables/block_v21/generic_activation_by_query.csv
    variables/block_v21/activation_g0_g9.csv
    variables/block_v21/g_class_activation_long.csv
    variables/block_v21/g_class_activation_summary.csv
    variables/block_v21/primary_activation_summary.csv
    variables/block_v21/activation_by_generic_class_summary.csv
    variables/block_v21/document_variable_matrix_with_activation.csv
    variables/block_v21/activation_logic_validation.csv
    variables/block_v21/g_class_activation_metadata.json

Methodological meaning:

    This block transforms analytical variables into generic document
    configuration families.

    These classes are not yet concrete MongoDB schemas.
    They identify which families of document designs should be instantiated
    and benchmarked.

Important interpretation:

    More than one G class may be active for the same query.

    The primary activation class is selected using the highest activation score,
    but all active classes should be considered when generating candidate
    MongoDB configurations.

_Last updated: 2026-04-30T16:04:11_

<!-- END: BLOCK V21 — Apply Generic Activation Logic G0-G9 -->


<!-- START: BLOCK V22 — Instantiate Concrete MongoDB Configuration Candidates -->
## BLOCK V22 — Instantiate Concrete MongoDB Configuration Candidates

This block instantiates concrete MongoDB configuration candidates from the
active generic classes G0-G9.

Main variables created:

    mongodb_configuration_candidates_df
    concrete_mongodb_candidates_df
    mongo_candidate_configurations_df

Additional variables created:

    mongodb_configuration_candidates_long_df
    control_candidates_df
    candidate_profile_by_query_df
    document_variable_matrix_with_candidates_df
    mongodb_candidate_summary_df
    mongodb_candidate_by_query_df
    mongodb_candidate_priority_summary_df
    mongodb_candidate_validation_df

Number of MongoDB candidates:

    60

Number of queries with candidates:

    10

Number of control candidates:

    11

Number of primary candidates:

    32

Number of secondary affected candidates:

    17

Failed validation checks:

    0

Generated candidate design patterns:

    ['aggregation_materialized_collection', 'association_references', 'benchmark_tradeoff_alternative', 'deep_nested_document', 'embedded_containment', 'embedded_descriptors', 'normalized_reference_baseline', 'root_only_collection', 'shared_target_reference_strategy', 'update_aware_reference_design']

Generated reproducibility files:

    variables/block_v22/mongodb_configuration_candidates.csv
    variables/block_v22/concrete_mongodb_candidates.csv
    variables/block_v22/mongo_candidate_configurations.csv
    variables/block_v22/mongodb_configuration_candidates_long.csv
    variables/block_v22/control_candidates.csv
    variables/block_v22/candidate_profile_by_query.csv
    variables/block_v22/document_variable_matrix_with_candidates.csv
    variables/block_v22/mongodb_candidate_summary.csv
    variables/block_v22/mongodb_candidate_by_query.csv
    variables/block_v22/mongodb_candidate_priority_summary.csv
    variables/block_v22/mongodb_candidate_validation.csv
    variables/block_v22/mongodb_configuration_candidates_metadata.json

Methodological meaning:

    This block translates generic activation classes into concrete MongoDB
    candidate design patterns.

    These candidates are still logical/physical design specifications.
    They are not loaded into MongoDB yet.

Important note:

    Every query receives a control candidate using a normalized reference
    baseline. This allows later benchmark comparison between the baseline
    and the generated document-oriented alternatives.

_Last updated: 2026-04-30T16:06:52_

<!-- END: BLOCK V22 — Instantiate Concrete MongoDB Configuration Candidates -->


<!-- START: BLOCK V23 — Select Primary, Secondary Affected, and Control Configurations -->
## BLOCK V23 — Select Primary, Secondary Affected, and Control Configurations

This block selects the MongoDB configuration candidates that will be used by
the benchmark execution plan.

Main variables created:

    benchmark_configuration_selection_df
    primary_configurations_df
    secondary_affected_configurations_df
    control_configurations_df

Additional variables created:

    benchmark_execution_plan_df
    benchmark_selection_by_query_df
    document_variable_matrix_with_benchmark_selection_df
    benchmark_selection_summary_df
    benchmark_group_summary_df
    benchmark_selection_validation_df

Number of selected configurations:

    60

Number of queries:

    10

Number of primary configurations:

    33

Number of secondary affected configurations:

    17

Number of control configurations:

    10

Failed validation checks:

    0

Warning validation checks:

    0

Generated reproducibility files:

    variables/block_v23/benchmark_configuration_selection.csv
    variables/block_v23/primary_configurations.csv
    variables/block_v23/secondary_affected_configurations.csv
    variables/block_v23/control_configurations.csv
    variables/block_v23/benchmark_execution_plan.csv
    variables/block_v23/benchmark_selection_by_query.csv
    variables/block_v23/document_variable_matrix_with_benchmark_selection.csv
    variables/block_v23/document_variable_matrix.csv
    variables/block_v23/benchmark_selection_summary.csv
    variables/block_v23/benchmark_group_summary.csv
    variables/block_v23/benchmark_selection_validation.csv
    variables/block_v23/benchmark_configuration_selection_metadata.json

Methodological meaning:

    This block separates the generated MongoDB candidates into benchmark
    groups.

    The control group contains normalized/reference baselines.

    The primary group contains the main candidate configurations expected to
    improve read behavior for the target query.

    The secondary_affected group contains candidates that may improve reads
    but should be evaluated carefully because of update volatility, sharedness,
    or document-design trade-offs.

Important note:

    This block still does not execute MongoDB loads or benchmark queries.

    It only produces the benchmark execution plan that the external server-side
    script will use later.

_Last updated: 2026-04-30T16:08:49_

<!-- END: BLOCK V23 — Select Primary, Secondary Affected, and Control Configurations -->


<!-- START: BLOCK V24 — Export Benchmark Configuration Artifacts -->
## BLOCK V24 — Export Benchmark Configuration Artifacts

This block exports benchmark configuration artifacts for the external
server-side load and benchmark script.

Main variables created:

    benchmark_artifacts_dir
    benchmark_manifest
    exported_artifacts_df
    benchmark_export_validation_df

Artifact directory:

    /home/jovyan/privado/framework evaluation approachs/framework with dataset fiben/benchmark_artifacts/fiben_mongodb_configurations

Number of exported artifacts:

    15

Number of selected configurations:

    60

Number of candidate specs:

    60

Number of queries in query-to-candidate mapping:

    10

Failed validation checks:

    0

Warning validation checks:

    0

Main exported files:

    benchmark_execution_plan.csv
    benchmark_execution_plan.json
    mongodb_candidate_specs.json
    mongodb_candidate_specs_by_candidate_id.json
    query_to_candidate_mapping.json
    benchmark_group_mapping.json
    benchmark_groups_summary.csv
    benchmark_selection_by_query.csv
    primary_configurations.csv
    secondary_affected_configurations.csv
    control_configurations.csv
    workload_query_metadata.json
    document_variable_matrix.csv
    benchmark_manifest.json
    README_benchmark_artifacts.md

Generated reproducibility files:

    variables/block_v24/exported_artifacts.csv
    variables/block_v24/benchmark_execution_plan_export.csv
    variables/block_v24/benchmark_export_validation.csv
    variables/block_v24/failed_benchmark_export_validation.csv
    variables/block_v24/warning_benchmark_export_validation.csv
    variables/block_v24/benchmark_manifest.json
    variables/block_v24/benchmark_export_metadata.json

Methodological meaning:

    This block closes the notebook-side methodology pipeline.

    It exports the selected MongoDB configuration candidates and benchmark
    execution plan to files that can be consumed by a separate execution script.

Important note:

    The exported artifacts do not include the FIBEN dataset files.

    The benchmark runner must receive the dataset path and MongoDB connection
    information separately.

_Last updated: 2026-04-30T16:10:46_

<!-- END: BLOCK V24 — Export Benchmark Configuration Artifacts -->

