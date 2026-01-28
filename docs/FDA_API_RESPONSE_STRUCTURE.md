# FDA Drug API Response Structure

## Overview
This document describes the structure and content of responses from the FDA's Drug FDA API endpoint (`https://api.fda.gov/drug/drugsfda.json`), which provides information about FDA-approved drugs.

## API Endpoint
- **Base URL:** `https://api.fda.gov/drug/drugsfda.json`
- **Rate Limit:** 100 requests per minute (higher with API key)
- **Pagination:** `limit` (max 1000) and `skip` (max 25000) parameters
- **Max Results:** Approximately 26,000 most recent drug records accessible

## Response Structure

### Top-Level Fields

```json
{
  "application_number": "ANDA078284",
  "sponsor_name": "ORBION PHARMS",
  "submissions": [],
  "products": [],
  "openfda": {}
}
```

### Application Number
- **Type:** String
- **Description:** FDA's unique identifier for the drug application
- **Format:** NDA (New Drug Application) or ANDA (Abbreviated New Drug Application) followed by numbers
- **Examples:** `NDA002282`, `ANDA078284`

### Sponsor Name
- **Type:** String
- **Description:** Company or organization that submitted the drug application
- **Examples:** `ORBION PHARMS`, `Wyeth Pharmaceuticals LLC`

## Submissions Array

Each drug application can have multiple submissions. A submission represents a formal request or update to the FDA.

### Submission Fields

```json
{
  "submission_type": "ORIG",
  "submission_number": "1",
  "submission_status": "AP",
  "submission_status_date": "20090810",
  "review_priority": "STANDARD",
  "submission_class_code": "TYPE1",
  "submission_class_code_description": "Type 1 - New Molecular Entity",
  "application_docs": []
}
```

#### submission_type
- **Type:** String
- **Description:** Whether this is an original (ORIG) or supplemental (SUPPL) submission
- **Possible Values:** `ORIG`, `SUPPL`

#### submission_number
- **Type:** String
- **Description:** Sequential number for the submission

#### submission_status
- **Type:** String
- **Description:** Approval status of the submission
- **Possible Values:** `AP` (Approved), `RJ` (Rejected), `WD` (Withdrawn), etc.

#### submission_status_date
- **Type:** String (YYYYMMDD format)
- **Description:** Date when the submission status was finalized
- **Example:** `20090810` = August 10, 2009

#### review_priority
- **Type:** String
- **Description:** Priority level of the FDA review
- **Possible Values:** `STANDARD`, `PRIORITY`

#### submission_class_code
- **Type:** String
- **Description:** Code for the submission class
- **Examples:** `TYPE1`, `LABELING`, `CMC`, `EFFICACY`, `REMS`

#### submission_class_code_description
- **Type:** String
- **Description:** Human-readable description of the submission class
- **See below** for complete list of all submission types

## All Submission Class Types

The following is a comprehensive list of all submission class types found in the FDA database:

### Original Drug Approvals (ORIG submissions)
These represent original submissions for new drugs:
- **Type 1 - New Molecular Entity** - Completely new drug compound
- **Type 2 - New Active Ingredient** - New therapeutic ingredient in existing drug class
- **Type 3 - New Dosage Form** - Existing drug in new formulation (tablet, capsule, etc.)
- **Type 3 - New Dosage Form and Type 4 - New Combination** - Combination of new dosage form and new combination
- **Type 4 - New Combination** - Existing drugs combined in new formulation
- **Type 5 - New Formulation or New Manufacturer** - Reformulation or change of manufacturer
- **Type 7 - Drug Already Marketed without Approved NDA** - Drug previously approved or grandfathered

### Update/Supplemental Submissions (SUPPL submissions)
These represent updates to approved applications:
- **Labeling** - Changes to prescribing information, packaging, or labels
- **Manufacturing (CMC)** - Chemistry, Manufacturing, and Controls updates
- **Efficacy** - Clinical efficacy data updates
- **REMS** - Risk Evaluation and Mitigation Strategies
- **Supplement** - General supplemental submissions
- **Not Applicable** - No specific classification

## OpenFDA Section

The `openfda` field contains enriched, indexed data from multiple FDA systems for easier searching and analysis.

```json
{
  "application_number": ["ANDA078284"],
  "brand_name": ["SUMATRIPTAN"],
  "generic_name": ["SUMATRIPTAN"],
  "manufacturer_name": ["Bionpharma Inc."],
  "product_ndc": ["69452-344", "69452-345"],
  "product_type": ["HUMAN PRESCRIPTION DRUG"],
  "route": ["ORAL"],
  "substance_name": ["SUMATRIPTAN SUCCINATE"],
  "rxcui": ["313160"],
  "spl_id": ["025c1199-46e1-4e03-8489-8a24a0834891"],
  "spl_set_id": ["e90b0eea-c424-4f00-98da-6ed6e80de1f6"],
  "package_ndc": ["69452-344-60"],
  "unii": ["J8BDZ68989"]
}
```

### OpenFDA Fields
- **application_number** - FDA application number(s)
- **brand_name** - Trademarked product name(s)
- **generic_name** - Generic/chemical name(s)
- **manufacturer_name** - Company/manufacturer name(s)
- **product_ndc** - National Drug Code for the product
- **product_type** - Type of product (e.g., HUMAN PRESCRIPTION DRUG, OTC)
- **route** - Route of administration (ORAL, INTRAVENOUS, etc.)
- **substance_name** - Chemical substance name(s)
- **rxcui** - RxNorm Concept Unique Identifiers
- **spl_id** - FDA Structured Product Labeling ID
- **spl_set_id** - SPL Set ID for grouping related products
- **package_ndc** - NDC code for specific packaging
- **unii** - Unique Ingredient Identifier

## Products Array

Each drug application includes one or more products (different formulations, strengths, etc.).

```json
{
  "product_number": "001",
  "reference_drug": "No",
  "brand_name": "SUMATRIPTAN SUCCINATE",
  "active_ingredients": [
    {
      "name": "SUMATRIPTAN SUCCINATE",
      "strength": "EQ 50MG BASE"
    }
  ],
  "reference_standard": "No",
  "dosage_form": "TABLET",
  "route": "ORAL",
  "marketing_status": "Prescription",
  "te_code": "AB"
}
```

### Product Fields
- **product_number** - Product identifier within the application
- **reference_drug** - Whether it's designated as a reference drug for generics
- **brand_name** - Product brand name
- **active_ingredients** - Array of active pharmaceutical ingredients with strengths
- **reference_standard** - Whether it's a pharmaceutical reference standard
- **dosage_form** - Physical form (TABLET, CAPSULE, LIQUID, etc.)
- **route** - Route of administration (ORAL, IV, IM, etc.)
- **marketing_status** - Marketing category (Prescription, OTC, etc.)
- **te_code** - Therapeutic equivalence code for generic drugs

## Current Filtering in DrugStats

The drugstats script currently filters for **ORIG (original) submissions** with **AP (approved) status** and includes the following submission types:
- Type 1 - New Molecular Entity (NME)
- Type 2 - New Active Ingredient
- Type 3 - New Dosage Form
- Type 4 - New Combination
- Type 10 - New Indication (Note: Type 10 shown as "Type 10 - New Indication" when present)

This filtering ensures we count only **new drug approvals** and exclude **supplemental updates** (labeling changes, manufacturing updates, etc.).

## Notes

- Not all fields are present in every response
- The `openfda` section may have empty values if the drug predates the indexing
- Dates are in YYYYMMDD format
- Arrays are used even for single values to maintain consistency
- The API limits pagination to `skip <= 25000`, allowing access to approximately the first 26,000 most recent records
