# Step 3: Hierarchical Data Model Design

**MDM Focus:** This is the canonical MDM hierarchical data model. It represents the unified master data structure that consolidates information from all source systems. Each entity serves as the "golden record" with source system tracking via SourceSystemKey fields.

**Key MDM Principles:**
- **Canonical Model:** One unified model, not source-specific schemas
- **Master Entities:** Core entities (Person, Organization, Product) as the foundation
- **Source Lineage:** SourceSystemKey tracks data origin for data quality and governance
- **Master Data Only:** Focus on identity, relationships, and core attributes (excludes transactional data)

## 3.1 Entity: Person (Unified MDM Entity)

**Type:** OOTB Entity (Extended)
**Purpose:** Unified canonical master entity consolidating all requirements (person and organization data) into single Person OOTB entity. This represents the complete MDM golden record structure.

### Identifiers
- PersonId (MDM generated)
- SSN
- TaxID

### Attributes

**OOTB Attributes:**
- FirstName
- LastName
- MiddleName
- NamePrefix
- NameSuffix
- FullName
- DateOfBirth
- Gender
- MaritalStatus
- PreferredLanguage
- DeceasedDate
- DeceasedFlag

**Custom Attributes:**
- Classification
- Ein
- Employmentstatus
- Relationshiptype
- Roletype
- Status

### Field Groups

#### Address (OOTB - Extended)
**OOTB Fields:**
- AddressLine1
- AddressLine2
- City
- State
- PostalCode
- Country
- AddressType
- PrimaryFlag
- StartDate
- EndDate
- County
- Region
- Latitude
- Longitude

**Custom Fields:**
- SourceSystemKey (for unique identification from source systems)

#### Phone (OOTB - Extended)
**OOTB Fields:**
- PhoneNumber
- PhoneType
- PrimaryFlag
- CountryCode
- AreaCode
- Extension
- StartDate
- EndDate
- DoNotCallFlag

**Custom Fields:**
- SourceSystemKey (for unique identification from source systems)

#### Email (OOTB - Extended)
**OOTB Fields:**
- EmailAddress
- EmailType
- PrimaryFlag
- StartDate
- EndDate
- DoNotEmailFlag
- BounceFlag

**Custom Fields:**
- SourceSystemKey (for unique identification from source systems)

#### Identifier (OOTB - Extended)
**OOTB Fields:**
- IdentifierValue
- IdentifierType
- PrimaryFlag
- Issuer
- StartDate
- EndDate
- VerificationStatus

**Custom Fields:**
- SourceSystemKey (for unique identification from source systems)

#### Constituent (Custom - Extended)

**Custom Fields:**
- Type
- Status
- StartDate
- EndDate
- SourceSystem
- SourceSystemKey (for unique identification from source systems)

#### Ex (Custom - Extended)

**Custom Fields:**
- Type
- Status
- StartDate
- EndDate
- SourceSystem
- SourceSystemKey (for unique identification from source systems)

## 3.2 Source System Integration

### Source Systems
- **Banner** (JDBC) → Entity and field groups
- **Workday** (SOAP API) → Entity and field groups
- **Slate** (API) → Entity and field groups
- **Salesforce** (API) → Entity and field groups
- **SFAQ** (API) → Entity and field groups
- **AffinaQuest** (API) → Entity and field groups
- **SF-STU** (API) → Entity and field groups
- **Snowflake** (Database) → Entity and field groups
- **IAM** (API) → Entity and field groups
- **Slack** (API) → Entity and field groups

### Cross-Reference Tracking
- All source systems track cross-references using SourceSystemKey in field groups
- Entities track cross-references using Identifier field group

## 3.3 Matching and Survivorship

- **Address matching:** Match based on standardized address components; may use a unique key from the source system or a com...
- **Phone matching:** Match on normalized phone number (country and area code); uniqueness may vary based on business requ...
- **Email matching:** Match on lowercased, trimmed email address; not always unique depending on real-world usage....
- **Address crosswalk:** Use reference/crosswalk tables to link and translate between keys of source and master addresses....

- **Survivorship:** Configured at attribute level with source priority rules
- **Unique Identification:** SourceSystemKey used to prevent duplicate records

## 3.4 Data Quality Rules

- **Address standardization:** Centralized standardization to uniform format...
- **Phone standardization:** Centralized standardization to uniform format...
- **Lookup value mapping:** Map source values to MDM values via reference data...

